# ui/pages/simulador.py
import math
from decimal import Decimal
import pandas as pd
import streamlit as st

from models.loan import Loan, LoanParameters
from services.scenario_service import ScenarioRepository
from services.analysis_service import sensitivity_analysis
from services.export_service import ExportService
from utils.session_state import get_state, set_state, has_state
from utils.formatters import format_currency, format_percentage

# ======================
#   Estado / Config UI
# ======================
if not has_state("sim_cfg"):
    set_state("sim_cfg", {
        "symbol": "$",
        "decimals_money": 2,
        "decimals_pct": 2,
    })
cfg = get_state("sim_cfg")

if not has_state("escenarios_guardados"):
    set_state("escenarios_guardados", [])

# ======================
#   Encabezado
# ======================
st.markdown("# :blue[🔮 Simulador de escenarios]")
st.caption("Ajusta monto, tasa y plazo. Explora la sensibilidad (barrido) y compara escenarios guardados.")

st.divider()

# ======================
#   Parámetros base
# ======================
with st.form("base_form", border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        monto = st.number_input(
            "Monto del crédito",
            min_value=0.0, step=1_000.0, value=10_000.0, format="%.2f",
            help="Monto principal del crédito."
        )
    with c2:
        tasa_anual = st.number_input(
            "Tasa anual nominal (%)",
            min_value=0.0, max_value=200.0, step=0.10, value=12.0, format="%.2f",
            help="Porcentaje anual nominal."
        )
    with c3:
        plazo_meses = st.number_input(
            "Plazo (meses)",
            min_value=6, max_value=600, step=6, value=120,
            help="Número de pagos mensuales."
        )

    submit_base = st.form_submit_button("Calcular escenario base", type="primary", use_container_width=True)

# ======================
#   Cálculo base
# ======================
if submit_base:
    # Crear loan usando el modelo
    params = LoanParameters(
        principal=Decimal(str(monto)),
        annual_rate=Decimal(str(tasa_anual)) / Decimal('100'),  # Convert percentage to decimal
        num_payments=int(plazo_meses)
    )
    loan = Loan(params)
    loan.calculate()
    
    set_state("sim_base", {
        "monto": monto,
        "tasa_anual": tasa_anual,
        "plazo_meses": int(plazo_meses),
        "loan": loan,
    })

if "sim_base" in st.session_state:
    base = get_state("sim_base")
    loan = base["loan"]
    metrics = loan.metrics
    df_tabla = loan.schedule

    pago = float(metrics.monthly_payment)
    total_pagado = float(metrics.total_paid)
    total_interes = float(metrics.total_interest)

    a, b, c, d = st.columns(4)
    with a:
        st.metric("Pago mensual", format_currency(metrics.monthly_payment, cfg['symbol'], cfg['decimals_money']))
    with b:
        st.metric("Tasa anual", f"{base['tasa_anual']:.{cfg['decimals_pct']}f}%")
    with c:
        st.metric("Total pagado", format_currency(metrics.total_paid, cfg['symbol'], cfg['decimals_money']))
    with d:
        st.metric("Total intereses", format_currency(metrics.total_interest, cfg['symbol'], cfg['decimals_money']))

    st.markdown("### 🧾 Tabla de amortización (escenario base)")
    df_show = df_tabla.copy()
    df_show["Mes"] = df_show["Mes"].astype(int)
    df_show["Pago"] = df_show["Pago"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_show["Interés"] = df_show["Interés"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_show["Abono a capital"] = df_show["Abono a capital"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_show["Saldo restante"] = df_show["Saldo restante"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    st.dataframe(df_show, use_container_width=True, hide_index=True)

    st.markdown("### 📈 Gráficas base")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Saldo restante por mes**")
        st.line_chart(df_tabla.set_index("Mes")["Saldo restante"], x_label="Mes", y_label="Saldo")
    with g2:
        st.markdown("**Descomposición del pago**")
        st.area_chart(df_tabla.set_index("Mes")[["Interés", "Abono a capital"]], x_label="Mes", y_label="Monto")

    st.markdown("### 📥 Descargas del escenario base")
    
    metadata = {
        "title": "Escenario base - Tabla de amortización",
        "parameters": {
            "Monto": format_currency(Decimal(str(base['monto'])), cfg['symbol'], cfg['decimals_money']),
            "Tasa anual": f"{base['tasa_anual']:.2f}%",
            "Plazo": f"{base['plazo_meses']} meses",
            "Pago mensual": format_currency(metrics.monthly_payment, cfg['symbol'], cfg['decimals_money']),
            "Total pagado": format_currency(metrics.total_paid, cfg['symbol'], cfg['decimals_money']),
            "Intereses": format_currency(metrics.total_interest, cfg['symbol'], cfg['decimals_money'])
        },
        "currency_symbol": cfg['symbol'],
        "decimals": cfg['decimals_money']
    }
    
    export_service = ExportService()
    
    # CSV
    csv_buffer = export_service.export('csv', df_tabla, metadata)
    st.download_button(
        "CSV",
        data=csv_buffer,
        file_name="amortizacion_escenario_base.csv",
        mime="text/csv",
        use_container_width=True,
    )
    
    # Excel
    excel_metadata = {**metadata, "totals_df": pd.DataFrame({
        "Pago mensual": [pago],
        "Total pagado": [total_pagado],
        "Total intereses": [total_interes]
    })}
    excel_buffer = export_service.export('excel', df_tabla, excel_metadata)
    st.download_button(
        "Excel",
        data=excel_buffer,
        file_name="amortizacion_escenario_base.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    
    # PDF
    pdf_buffer = export_service.export('pdf', df_tabla, metadata)
    st.download_button(
        "PDF",
        data=pdf_buffer,
        file_name="amortizacion_escenario_base.pdf",
        mime="application/pdf",
        use_container_width=True,
    )

st.divider()

# ======================
#   Barrido (sensibilidad)
# ======================
st.subheader("📉 Análisis de sensibilidad (barrido)")

with st.form("sweep_form", border=True):
    colp1, colp2 = st.columns([1.1, 2])
    with colp1:
        param = st.selectbox(
            "Parámetro a barrer",
            options=["Tasa anual nominal (%)", "Plazo (meses)", "Monto del crédito"],
            index=0,
            help="Se generan escenarios variando este único parámetro."
        )
    with colp2:
        if param == "Tasa anual nominal (%)":
            vmin = st.number_input("Desde (%)", value=8.0, step=0.25, format="%.2f")
            vmax = st.number_input("Hasta (%)", value=16.0, step=0.25, format="%.2f")
            vstep = st.number_input("Paso (%)", value=0.50, step=0.25, format="%.2f")
        elif param == "Plazo (meses)":
            vmin = st.number_input("Desde (meses)", value=60, step=6)
            vmax = st.number_input("Hasta (meses)", value=180, step=6)
            vstep = st.number_input("Paso (meses)", value=12, step=6)
        else:
            vmin = st.number_input("Desde (monto)", value=200_000.0, step=10_000.0, format="%.2f")
            vmax = st.number_input("Hasta (monto)", value=1_000_000.0, step=10_000.0, format="%.2f")
            vstep = st.number_input("Paso (monto)", value=50_000.0, step=10_000.0, format="%.2f")

    run_sweep = st.form_submit_button("Generar barrido", type="secondary", use_container_width=True)

if run_sweep:
    # Sanidad de rango
    if vmax <= vmin or vstep <= 0:
        st.error("Revisa el rango y el paso del barrido.", icon="🚨")
    else:
        # Usar el servicio de análisis
        if "sim_base" in st.session_state:
            base = get_state("sim_base")
            
            # Mapear el parámetro seleccionado
            param_map = {
                "Tasa anual nominal (%)": "annual_rate",
                "Plazo (meses)": "num_payments",
                "Monto del crédito": "principal"
            }
            
            variable = param_map[param]
            
            # Crear loan base
            base_params = LoanParameters(
                principal=Decimal(str(base['monto'])),
                annual_rate=Decimal(str(base['tasa_anual'])) / Decimal('100'),  # Convert percentage to decimal
                num_payments=int(base['plazo_meses'])
            )
            base_loan = Loan(base_params)
            base_loan.calculate()
            
            # Ejecutar análisis de sensibilidad
            df_sweep = sensitivity_analysis(
                base_loan=base_loan,
                variable=variable,
                min_value=Decimal(str(vmin)),
                max_value=Decimal(str(vmax)),
                step=Decimal(str(vstep))
            )
            
            # Agregar columna de parámetro para compatibilidad con UI existente
            df_sweep["Parámetro"] = param
            df_sweep["Valor"] = df_sweep[variable]
            
            set_state("df_sweep", df_sweep)
        else:
            st.error("Primero calcula el escenario base.", icon="🚨")

if "df_sweep" in st.session_state:
    df_sweep = get_state("df_sweep")
    st.markdown("### Resultados del barrido")
    
    df_view = df_sweep.copy()
    df_view["Pago mensual"] = df_view["monthly_payment"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_view["Total pagado"] = df_view["total_paid"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_view["Total intereses"] = df_view["total_interest"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_view["Tasa anual"] = df_view["annual_rate"].map(lambda x: f"{float(x):.{cfg['decimals_pct']}f}%")

    st.dataframe(
        df_view[["Parámetro", "Valor", "Pago mensual", "Total pagado", "Total intereses", "Tasa anual"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### 📊 Gráficas del barrido")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("**Pago mensual**")
        st.line_chart(df_sweep.set_index("Valor")["monthly_payment"], x_label="Valor", y_label="Pago")
    with g2:
        st.markdown("**Total pagado**")
        st.line_chart(df_sweep.set_index("Valor")["total_paid"], x_label="Valor", y_label="Total")
    with g3:
        st.markdown("**Total intereses**")
        st.line_chart(df_sweep.set_index("Valor")["total_interest"], x_label="Valor", y_label="Intereses")

    st.markdown("### 📥 Descargas del barrido")
    
    metadata = {
        "title": "Barrido de escenarios",
        "parameters": {},
        "currency_symbol": cfg['symbol'],
        "decimals": cfg['decimals_money']
    }
    
    export_service = ExportService()
    
    # CSV
    csv_buffer = export_service.export('csv', df_sweep, metadata)
    st.download_button(
        "CSV (barrido)",
        data=csv_buffer,
        file_name="barrido_escenarios.csv",
        mime="text/csv",
        use_container_width=True,
    )
    
    # Excel
    excel_buffer = export_service.export('excel', df_sweep, metadata)
    st.download_button(
        "Excel (barrido)",
        data=excel_buffer,
        file_name="barrido_escenarios.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )

st.divider()

# ======================
#   Comparador de escenarios guardados
# ======================
st.subheader("🧮 Comparador de escenarios")
st.caption("Guarda el escenario actual y compáralo con otros.")

if "sim_base" in st.session_state:
    with st.form("save_form", border=True):
        nombre = st.text_input("Nombre del escenario", placeholder="Escenario A (base)")
        guardar = st.form_submit_button("Guardar escenario", use_container_width=True)
    if guardar:
        base = get_state("sim_base")
        loan = base["loan"]
        metrics = loan.metrics
        
        escenarios = get_state("escenarios_guardados")
        escenarios.append({
            "Nombre": (nombre.strip() or "Escenario"),
            "Monto": float(base["monto"]),
            "Tasa anual": float(base["tasa_anual"]),
            "Plazo (meses)": int(base["plazo_meses"]),
            "Pago mensual": float(metrics.monthly_payment),
            "Total pagado": float(metrics.total_paid),
            "Total intereses": float(metrics.total_interest),
        })
        set_state("escenarios_guardados", escenarios)
        st.success("Escenario guardado ✅")
        st.rerun()

if len(get_state("escenarios_guardados")) > 0:
    df_comp = pd.DataFrame(get_state("escenarios_guardados"))
    
    # Vista formateada
    df_comp_v = df_comp.copy()
    df_comp_v["Pago mensual"] = df_comp_v["Pago mensual"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_comp_v["Total pagado"] = df_comp_v["Total pagado"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_comp_v["Total intereses"] = df_comp_v["Total intereses"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_comp_v["Tasa anual"] = df_comp_v["Tasa anual"].map(lambda x: f"{x:.{cfg['decimals_pct']}f}%")

    st.dataframe(
        df_comp_v[["Nombre", "Monto", "Tasa anual", "Plazo (meses)", "Pago mensual", "Total pagado", "Total intereses"]],
        use_container_width=True, hide_index=True
    )

    st.markdown("### 📊 Gráficas comparativas")
    g1, g2 = st.columns(2)
    with g1:
        st.markdown("**Pago mensual**")
        st.bar_chart(df_comp.set_index("Nombre")["Pago mensual"], x_label="Escenario", y_label="Pago")
    with g2:
        st.markdown("**Total intereses**")
        st.bar_chart(df_comp.set_index("Nombre")["Total intereses"], x_label="Escenario", y_label="Intereses")

    st.markdown("### 🧹 Gestión")
    cdel1, cdel2 = st.columns(2)
    with cdel1:
        if st.button("Eliminar último escenario", use_container_width=True):
            escenarios = get_state("escenarios_guardados")
            set_state("escenarios_guardados", escenarios[:-1])
            st.rerun()
    with cdel2:
        if st.button("Limpiar todos", use_container_width=True):
            set_state("escenarios_guardados", [])
            st.rerun()

st.divider()

# ======================
#   Preferencias de formato
# ======================
st.subheader("⚙️ Preferencias")
cA, cB, cC = st.columns(3)
with cA:
    symbol = st.selectbox("Símbolo de moneda", ["$", "MXN$", "USD$", "€", "£"],
                          index=["$", "MXN$", "USD$", "€", "£"].index(cfg["symbol"]) if cfg["symbol"] in ["$", "MXN$", "USD$", "€", "£"] else 0)
with cB:
    dec_m = st.number_input("Decimales (dinero)", min_value=0, max_value=4, value=int(cfg["decimals_money"]), step=1)
with cC:
    dec_p = st.number_input("Decimales (%)", min_value=0, max_value=4, value=int(cfg["decimals_pct"]), step=1)

if (symbol != cfg["symbol"]) or (dec_m != cfg["decimals_money"]) or (dec_p != cfg["decimals_pct"]):
    cfg["symbol"] = symbol
    cfg["decimals_money"] = int(dec_m)
    cfg["decimals_pct"] = int(dec_p)
    set_state("sim_cfg", cfg)
    st.success("Formato actualizado.")
