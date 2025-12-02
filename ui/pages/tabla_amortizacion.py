# ui/pages/tabla_amortizacion.py
import io
from decimal import Decimal
import pandas as pd
import streamlit as st

from core.calculations import calculate_monthly_payment
from core.amortization import AmortizationSchedule
from services.export_service import ExportService
from ui.components.forms import loan_input_form, format_preferences_form
from ui.components.charts import display_balance_chart, display_payment_breakdown_chart
from ui.components.metrics import display_loan_metrics
from ui.components.tables import display_amortization_table
from utils.session_state import get_state, set_state, has_state
from utils.formatters import format_currency

# ======================
#   Estado / Config UI
# ======================
if not has_state("tabla"):
    set_state("tabla", None)
if not has_state("pago"):
    set_state("pago", None)
if not has_state("inputs"):
    set_state("inputs", {"tasa": 10.0, "monto": 10000.0, "pagos": 12})
if not has_state("cfg"):
    set_state("cfg", {"currency_symbol": "$", "decimals": 2, "show_row0": True})

cfg = get_state("cfg")
inp = get_state("inputs")

st.markdown("# :blue[💰 Tabla de amortización]")
st.caption("Calculadora de pagos y desglose mensual con exportaciones y visualizaciones.")

# ==============
#   Formulario
# ==============
with st.form("form_credito", border=True):
    col1, col2, col3 = st.columns([1, 1, 1])
    with col1:
        tasa_input = st.number_input(
            "Tasa de interés anual (% nominal)",
            min_value=0.0, step=0.1, value=float(inp["tasa"]), format="%.2f",
            help="Tasa nominal anual. La frecuencia de pagos se asume mensual.",
        )
    with col2:
        monto_input = st.number_input(
            "Monto del crédito",
            min_value=0.0, step=100.0, value=float(inp["monto"]), format="%.2f",
        )
    with col3:
        pagos_input = st.number_input(
            "Número de pagos (meses)",
            min_value=1, step=12, value=int(inp["pagos"]),
            help="Plazo en meses (por ejemplo, 12, 24, 36...).",
        )

    submitted = st.form_submit_button("Calcular", use_container_width=True, type="primary")

# =================
#   Cálculo
# =================
if submitted:
    # Guardamos entradas
    set_state("inputs", {"tasa": tasa_input, "monto": monto_input, "pagos": int(pagos_input)})
    
    # Calculamos usando módulos core
    principal = Decimal(str(monto_input))
    annual_rate = Decimal(str(tasa_input))
    num_payments = int(pagos_input)
    
    pago = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    # Generar tabla de amortización
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, pago)
    tabla_df = schedule.generate()
    
    set_state("pago", float(pago))
    set_state("tabla", tabla_df)

# =================
#   Resultados UI
# =================
if get_state("tabla") is not None and get_state("pago") is not None:
    tabla_df = get_state("tabla").copy()
    pago = get_state("pago")
    tasa_input = get_state("inputs")["tasa"]
    monto_input = get_state("inputs")["monto"]
    pagos_input = get_state("inputs")["pagos"]

    # KPIs
    total_pagado = float(tabla_df["Pago"].sum())
    total_interes = float(tabla_df["Interés"].sum())
    
    display_loan_metrics(
        monthly_payment=Decimal(str(pago)),
        total_paid=Decimal(str(total_pagado)),
        total_interest=Decimal(str(total_interes)),
        annual_rate=Decimal(str(tasa_input)),
        currency_symbol=cfg['currency_symbol'],
        decimals=cfg['decimals']
    )

    st.markdown("---")

    # =================
    #   Pestañas
    # =================
    tab_tabla, tab_graficas, tab_totales, tab_formato = st.tabs(
        ["🧾 Tabla", "📈 Gráficas", "∑ Totales & Descargas", "⚙️ Formato"]
    )

    # -------------
    #   TAB: Tabla
    # -------------
    with tab_tabla:
        st.subheader("Tabla de amortización")

        # Opción para mostrar/ocultar fila 0
        cfg["show_row0"] = st.toggle(
            "Mostrar fila 0 (saldo inicial)", value=cfg["show_row0"],
            help="Si desactivas, la tabla inicia en el Mes 1."
        )

        df_show = tabla_df.copy()
        if not cfg["show_row0"]:
            df_show = df_show[df_show["Mes"] != 0].reset_index(drop=True)

        display_amortization_table(df_show, cfg["currency_symbol"], cfg["decimals"])

    # ----------------
    #   TAB: Gráficas
    # ----------------
    with tab_graficas:
        st.subheader("Visualizaciones")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Saldo restante por mes**")
            display_balance_chart(tabla_df)
        with c2:
            st.markdown("**Descomposición del pago**")
            display_payment_breakdown_chart(tabla_df)

    # ---------------------------
    #   TAB: Totales & Descargas
    # ---------------------------
    with tab_totales:
        st.subheader("Totales")
        df_totales = pd.DataFrame(
            {"Total monto a pagar": [total_pagado], "Total interés a pagar": [total_interes]}
        )
        
        # Format totales
        df_totales_display = df_totales.copy()
        for col in df_totales_display.columns:
            df_totales_display[col] = df_totales_display[col].map(
                lambda x: format_currency(Decimal(str(x)), cfg["currency_symbol"], cfg["decimals"])
            )
        
        st.dataframe(
            df_totales_display.rename_axis(None, axis=1),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Descargas")
        
        # Preparar metadata para exportación
        metadata = {
            "title": "Tabla de amortización",
            "parameters": {
                "Monto crédito": format_currency(Decimal(str(monto_input)), cfg["currency_symbol"], cfg["decimals"]),
                "Tasa nominal anual": f"{tasa_input:.2f}%",
                "Número de pagos": str(int(pagos_input)),
                "Mensualidad estimada": format_currency(Decimal(str(pago)), cfg["currency_symbol"], cfg["decimals"])
            },
            "currency_symbol": cfg["currency_symbol"],
            "decimals": cfg["decimals"]
        }
        
        export_service = ExportService()
        
        # CSV
        csv_buffer = export_service.export('csv', tabla_df, metadata)
        st.download_button(
            "📥 Descargar CSV",
            data=csv_buffer.getvalue(),
            file_name="tabla_amortizacion.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Excel
        excel_buffer = export_service.export('excel', tabla_df, {**metadata, "totals_df": df_totales})
        st.download_button(
            "📥 Descargar Excel",
            data=excel_buffer.getvalue(),
            file_name="tabla_amortizacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        # PDF
        st.divider()
        st.caption("PDF con parámetros y formato tabular.")
        
        pdf_buffer = export_service.export('pdf', tabla_df, metadata)
        st.download_button(
            label="📥 Descargar PDF",
            data=pdf_buffer.getvalue(),
            file_name="tabla_amortizacion.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # ----------------
    #   TAB: Formato
    # ----------------
    with tab_formato:
        st.subheader("Preferencias de formato")
        new_cfg = format_preferences_form(cfg)
        if new_cfg != cfg:
            set_state("cfg", new_cfg)
            st.success("Formato actualizado.")
else:
    st.info("Completa el formulario y pulsa **Calcular** para ver resultados.")
