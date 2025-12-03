# ui/pages/sensibilidad.py
from decimal import Decimal
import pandas as pd
import streamlit as st

from models.loan import Loan, LoanParameters
from services.analysis_service import sensitivity_analysis, tornado_analysis
from services.export_service import ExportService
from utils.session_state import get_state, set_state, has_state
from utils.formatters import format_currency

# ======================
#   Estado / Config local
# ======================
if not has_state("sens_cfg"):
    set_state("sens_cfg", {
        "symbol": "$",
        "decimals_money": 2,
        "decimals_pct": 2,
        "delta_list": [-20, -10, -5, 0, 5, 10, 20],  # % por defecto para sensibilidad local
    })
cfg = get_state("sens_cfg")

# Buffer de resultados
if not has_state("sens_result"):
    set_state("sens_result", {})

st.markdown("# :blue[📉 Análisis de sensibilidad]")
st.caption("Explora cómo afectan cambios en tasa, plazo o monto al pago mensual, total pagado e intereses.")

st.divider()

# ======================
#   Escenario base
# ======================
with st.form("base_form", border=True):
    c1, c2, c3 = st.columns(3)
    with c1:
        monto = st.number_input(
            "Monto del crédito",
            min_value=0.0, step=10_000.0, value=50_000.0, format="%.2f",
        )
    with c2:
        tasa_anual = st.number_input(
            "Tasa anual nominal (%)",
            min_value=0.0, max_value=200.0, step=0.10, value=12.0, format="%.2f",
        )
    with c3:
        plazo_meses = st.number_input(
            "Plazo (meses)",
            min_value=6, max_value=600, step=6, value=120,
        )
    run_base = st.form_submit_button("Calcular escenario base", type="primary", use_container_width=True)

if run_base:
    # Crear loan usando el modelo
    params = LoanParameters(
        principal=Decimal(str(monto)),
        annual_rate=Decimal(str(tasa_anual)) / Decimal('100'),  # Convert percentage to decimal
        num_payments=int(plazo_meses)
    )
    loan = Loan(params)
    loan.calculate()
    
    set_state("sens_base", {
        "monto": float(monto),
        "tasa_anual": float(tasa_anual),
        "plazo_meses": int(plazo_meses),
        "loan": loan,
    })

# Mostrar base
if "sens_base" in st.session_state:
    base = get_state("sens_base")
    loan = base["loan"]
    metrics = loan.metrics
    df_tabla = loan.schedule
    
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

    st.markdown("### Tabla de amortización (base)")
    df_show = df_tabla.copy()
    df_show["Mes"] = df_show["Mes"].astype(int)
    for col in ["Pago", "Interés", "Abono a capital", "Saldo restante"]:
        df_show[col] = df_show[col].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    st.dataframe(df_show, use_container_width=True, hide_index=True)

st.divider()

# ======================
#   1) Sensibilidad local (uno a la vez)
# ======================
st.subheader("1) Sensibilidad local (uno a la vez)")

with st.form("sens_local_form", border=True):
    colp, cold = st.columns([1.2, 1.8])
    with colp:
        variable = st.selectbox(
            "Variable a analizar",
            options=["Tasa anual nominal (%)", "Plazo (meses)", "Monto del crédito"],
            index=0,
        )
    with cold:
        deltas_text = st.text_input(
            "Deltas porcentuales (separados por coma)",
            value=",".join(map(str, cfg["delta_list"])),
            help="Ejemplo: -20,-10,-5,0,5,10,20 (para Monto y Tasa). "
                 "Para Plazo también se aplica en % sobre el plazo base."
        )
    run_local = st.form_submit_button("Ejecutar sensibilidad local", type="secondary", use_container_width=True)

def _parse_deltas(text: str) -> list:
    try:
        vals = [float(x.strip()) for x in text.split(",") if x.strip() != ""]
        if len(vals) == 0:
            return cfg["delta_list"]
        return vals
    except Exception:
        return cfg["delta_list"]

if run_local and "sens_base" in st.session_state:
    base = get_state("sens_base")
    deltas = _parse_deltas(deltas_text)
    registros = []

    # Mapear variable
    var_map = {
        "Tasa anual nominal (%)": "annual_rate",
        "Plazo (meses)": "num_payments",
        "Monto del crédito": "principal"
    }
    var_key = var_map[variable]

    for d in deltas:
        if variable == "Tasa anual nominal (%)":
            tasa_ = max(0.0, base["tasa_anual"] * (1 + d / 100.0))
            plazo_ = base["plazo_meses"]
            monto_ = base["monto"]
        elif variable == "Plazo (meses)":
            plazo_ = max(1, int(round(base["plazo_meses"] * (1 + d / 100.0))))
            tasa_ = base["tasa_anual"]
            monto_ = base["monto"]
        else:
            monto_ = max(0.0, base["monto"] * (1 + d / 100.0))
            tasa_ = base["tasa_anual"]
            plazo_ = base["plazo_meses"]

        # Crear loan y calcular
        params = LoanParameters(
            principal=Decimal(str(monto_)),
            annual_rate=Decimal(str(tasa_)) / Decimal('100'),  # Convert percentage to decimal
            num_payments=int(plazo_)
        )
        loan = Loan(params)
        loan.calculate()
        metrics = loan.metrics

        registros.append({
            "Variable": variable,
            "Delta (%)": d,
            "Monto": monto_,
            "Tasa anual": tasa_,
            "Plazo (meses)": plazo_,
            "Pago mensual": float(metrics.monthly_payment),
            "Total pagado": float(metrics.total_paid),
            "Total intereses": float(metrics.total_interest),
        })

    df_local = pd.DataFrame(registros).sort_values("Delta (%)").reset_index(drop=True)
    sens_result = get_state("sens_result")
    sens_result["local"] = df_local
    set_state("sens_result", sens_result)

if "local" in get_state("sens_result"):
    df_local = get_state("sens_result")["local"]
    st.markdown("#### Resultados — Sensibilidad local")

    df_view = df_local.copy()
    df_view["Pago mensual"] = df_view["Pago mensual"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_view["Total pagado"] = df_view["Total pagado"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_view["Total intereses"] = df_view["Total intereses"].map(lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money']))
    df_view["Tasa anual"] = df_view["Tasa anual"].map(lambda x: f"{x:.{cfg['decimals_pct']}f}%")
    st.dataframe(
        df_view[["Variable", "Delta (%)", "Pago mensual", "Total pagado", "Total intereses", "Monto", "Tasa anual", "Plazo (meses)"]],
        use_container_width=True, hide_index=True
    )

    st.markdown("#### Gráficas")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("**Pago mensual vs Delta**")
        st.line_chart(df_local.set_index("Delta (%)")["Pago mensual"], x_label="Delta (%)", y_label="Pago")
    with g2:
        st.markdown("**Total pagado vs Delta**")
        st.line_chart(df_local.set_index("Delta (%)")["Total pagado"], x_label="Delta (%)", y_label="Total")
    with g3:
        st.markdown("**Total intereses vs Delta**")
        st.line_chart(df_local.set_index("Delta (%)")["Total intereses"], x_label="Delta (%)", y_label="Intereses")

    st.markdown("#### Descargas")
    
    metadata = {
        "title": "Sensibilidad local",
        "parameters": {},
        "currency_symbol": cfg["symbol"],
        "decimals": cfg["decimals_money"]
    }
    
    export_service = ExportService()
    
    # CSV
    csv_buffer = export_service.export('csv', df_local, metadata)
    st.download_button("CSV (sensibilidad local)", data=csv_buffer,
                       file_name="sens_local.csv", mime="text/csv", use_container_width=True)
    
    # Excel
    excel_buffer = export_service.export('excel', df_local, metadata)
    st.download_button("Excel (sensibilidad local)", data=excel_buffer,
                       file_name="sens_local.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

st.divider()

# ======================
#   2) Tornado (impacto relativo)
# ======================
st.subheader("2) Tornado — impacto en métrica objetivo")
st.caption("Compara el efecto de ±Δ% en cada variable sobre una métrica (Pago mensual, Total pagado o Intereses).")

with st.form("tornado_form", border=True):
    metrica = st.selectbox(
        "Métrica objetivo",
        options=["Pago mensual", "Total pagado", "Total intereses"],
        index=2,
    )
    delta_tornado = st.number_input(
        "Δ% simétrico para cada variable",
        min_value=0.1, max_value=100.0, step=0.5, value=10.0, format="%.2f",
        help="Se evalúa el cambio de la métrica con +Δ% y -Δ% en cada variable."
    )
    run_tornado = st.form_submit_button("Generar tornado", type="secondary", use_container_width=True)

if run_tornado and "sens_base" in st.session_state:
    base = get_state("sens_base")
    base_loan = base["loan"]
    
    # Mapear métrica
    metric_map = {
        "Pago mensual": "monthly_payment",
        "Total pagado": "total_paid",
        "Total intereses": "total_interest"
    }
    target_metric = metric_map[metrica]
    
    # Ejecutar análisis tornado
    df_tornado = tornado_analysis(
        base_loan=base_loan,
        target_metric=target_metric,
        delta_percent=Decimal(str(delta_tornado))
    )
    
    sens_result = get_state("sens_result")
    sens_result["tornado"] = (metrica, df_tornado)
    set_state("sens_result", sens_result)

if "tornado" in get_state("sens_result"):
    metrica, df_tornado = get_state("sens_result")["tornado"]

    st.markdown(f"#### Tornado — impacto sobre **{metrica}**")
    
    # Vista formateada
    df_view = df_tornado.copy()
    fmt = lambda x: format_currency(Decimal(str(x)), cfg['symbol'], cfg['decimals_money'])
    df_view["Cambio +Δ"] = df_view["delta_plus"].map(fmt)
    df_view["Cambio -Δ"] = df_view["delta_minus"].map(fmt)
    df_view["Base"] = df_view["base_value"].map(fmt)
    df_view = df_view[["variable", "delta_percent", "Cambio +Δ", "Cambio -Δ", "Base"]]
    df_view.columns = ["Variable", "+Δ%", "Cambio +Δ", "Cambio -Δ", "Base"]
    
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    # Gráfico tipo tornado (aproximado con barras horizontales)
    st.markdown("**Visualización del tornado (barras horizontales)**")
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.markdown("**Cambio -Δ (izquierda)**")
        st.bar_chart(df_tornado.set_index("variable")["delta_minus"].abs(), x_label="Variable", y_label="|Δ|")
    with gcol2:
        st.markdown("**Cambio +Δ (derecha)**")
        st.bar_chart(df_tornado.set_index("variable")["delta_plus"].abs(), x_label="Variable", y_label="|Δ|")

    st.markdown("#### Descargas")
    
    metadata = {
        "title": f"Tornado — impacto sobre {metrica}",
        "parameters": {
            "Escenario base": f"Monto: {format_currency(Decimal(str(get_state('sens_base')['monto'])), cfg['symbol'], cfg['decimals_money'])} | "
                              f"Tasa: {get_state('sens_base')['tasa_anual']:.2f}% | "
                              f"Plazo: {get_state('sens_base')['plazo_meses']} meses",
        },
        "currency_symbol": cfg["symbol"],
        "decimals": cfg["decimals_money"]
    }
    
    export_service = ExportService()
    
    # CSV
    csv_buffer = export_service.export('csv', df_tornado, metadata)
    st.download_button("CSV (tornado)", data=csv_buffer,
                       file_name="tornado.csv", mime="text/csv", use_container_width=True)
    
    # Excel
    excel_buffer = export_service.export('excel', df_tornado, metadata)
    st.download_button("Excel (tornado)", data=excel_buffer,
                       file_name="tornado.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

    # PDF
    pdf_buffer = export_service.export('pdf', df_view, metadata)
    st.download_button("PDF (tornado)", data=pdf_buffer,
                       file_name="tornado.pdf", mime="application/pdf",
                       use_container_width=True)

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
    set_state("sens_cfg", cfg)
    st.success("Formato actualizado.")
