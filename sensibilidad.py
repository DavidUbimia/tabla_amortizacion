# sensibilidad.py
import io
import math
import pandas as pd
import streamlit as st
from functions import calcular_pago_mensual, tabla_amortizacion, generar_pdf_tabla

# ======================
#   Estado / Config local
# ======================
if "sens_cfg" not in st.session_state:
    st.session_state.sens_cfg = {
        "symbol": "$",
        "decimals_money": 2,
        "decimals_pct": 2,
        "delta_list": [-20, -10, -5, 0, 5, 10, 20],  # % por defecto para sensibilidad local
    }
cfg = st.session_state.sens_cfg

# Buffer de resultados
if "sens_result" not in st.session_state:
    st.session_state.sens_result = {}

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
    pago_base = calcular_pago_mensual(tasa_anual, monto, int(plazo_meses))
    df_base = tabla_amortizacion(pago_base, tasa_anual, monto, int(plazo_meses))
    st.session_state.sens_base = {
        "monto": float(monto),
        "tasa_anual": float(tasa_anual),
        "plazo_meses": int(plazo_meses),
        "pago": float(pago_base),
        "tabla": df_base,
    }

# Mostrar base
if "sens_base" in st.session_state:
    base = st.session_state.sens_base
    df_tabla = base["tabla"]
    total_pagado = float(df_tabla["Pago"].sum())
    total_interes = float(df_tabla["Interés"].sum())

    a, b, c, d = st.columns(4)
    with a:
        st.metric("Pago mensual", f"{cfg['symbol']}{base['pago']:,.{cfg['decimals_money']}f}")
    with b:
        st.metric("Tasa anual", f"{base['tasa_anual']:.{cfg['decimals_pct']}f}%")
    with c:
        st.metric("Total pagado", f"{cfg['symbol']}{total_pagado:,.{cfg['decimals_money']}f}")
    with d:
        st.metric("Total intereses", f"{cfg['symbol']}{total_interes:,.{cfg['decimals_money']}f}")

    st.markdown("### Tabla de amortización (base)")
    df_show = df_tabla.copy()
    df_show["Mes"] = df_show["Mes"].astype(int)
    money = lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}"
    for col in ["Pago", "Interés", "Abono a capital", "Saldo restante"]:
        df_show[col] = df_show[col].map(money)
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

def _parse_deltas(text: str) -> list[float]:
    try:
        vals = [float(x.strip()) for x in text.split(",") if x.strip() != ""]
        if len(vals) == 0:
            return cfg["delta_list"]
        return vals
    except Exception:
        return cfg["delta_list"]

def _calc_metrics(tasa_anual, monto, plazo):
    pago = calcular_pago_mensual(tasa_anual, monto, int(plazo))
    df = tabla_amortizacion(pago, tasa_anual, monto, int(plazo))
    total = float(df["Pago"].sum())
    interes = float(df["Interés"].sum())
    return pago, total, interes

if run_local and "sens_base" in st.session_state:
    base = st.session_state.sens_base
    deltas = _parse_deltas(deltas_text)
    registros = []

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

        pago_, total_, interes_ = _calc_metrics(tasa_, monto_, plazo_)
        registros.append({
            "Variable": variable,
            "Delta (%)": d,
            "Monto": monto_,
            "Tasa anual": tasa_,
            "Plazo (meses)": plazo_,
            "Pago mensual": pago_,
            "Total pagado": total_,
            "Total intereses": interes_,
        })

    df_local = pd.DataFrame(registros).sort_values("Delta (%)").reset_index(drop=True)
    st.session_state.sens_result["local"] = df_local

if "local" in st.session_state.sens_result:
    df_local = st.session_state.sens_result["local"]
    st.markdown("#### Resultados — Sensibilidad local")

    df_view = df_local.copy()
    df_view["Pago mensual"] = df_view["Pago mensual"].map(lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}")
    df_view["Total pagado"] = df_view["Total pagado"].map(lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}")
    df_view["Total intereses"] = df_view["Total intereses"].map(lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}")
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
    # CSV
    csv_bytes = df_local.to_csv(index=False).encode("utf-8")
    st.download_button("CSV (sensibilidad local)", data=csv_bytes,
                       file_name="sens_local.csv", mime="text/csv", use_container_width=True)
    # Excel
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        df_local.to_excel(writer, sheet_name="SensLocal", index=False)
    excel_buf.seek(0)
    st.download_button("Excel (sensibilidad local)", data=excel_buf,
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
    base = st.session_state.sens_base
    pago_b, total_b, interes_b = _calc_metrics(base["tasa_anual"], base["monto"], base["plazo_meses"])
    base_metric = {"Pago mensual": pago_b, "Total pagado": total_b, "Total intereses": interes_b}[metrica]

    vars_cfg = [
        ("Tasa anual nominal (%)", "tasa"),
        ("Plazo (meses)", "plazo"),
        ("Monto del crédito", "monto"),
    ]

    filas = []
    for label, key in vars_cfg:
        if key == "tasa":
            plus = max(0.0, base["tasa_anual"] * (1 + delta_tornado / 100.0))
            minus = max(0.0, base["tasa_anual"] * (1 - delta_tornado / 100.0))
            m_plus = _calc_metrics(plus, base["monto"], base["plazo_meses"])
            m_minus = _calc_metrics(minus, base["monto"], base["plazo_meses"])
        elif key == "plazo":
            plus = max(1, int(round(base["plazo_meses"] * (1 + delta_tornado / 100.0))))
            minus = max(1, int(round(base["plazo_meses"] * (1 - delta_tornado / 100.0))))
            m_plus = _calc_metrics(base["tasa_anual"], base["monto"], plus)
            m_minus = _calc_metrics(base["tasa_anual"], base["monto"], minus)
        else:
            plus = max(0.0, base["monto"] * (1 + delta_tornado / 100.0))
            minus = max(0.0, base["monto"] * (1 - delta_tornado / 100.0))
            m_plus = _calc_metrics(base["tasa_anual"], plus, base["plazo_meses"])
            m_minus = _calc_metrics(base["tasa_anual"], minus, base["plazo_meses"])

        # Elegir la métrica
        mp = {"Pago mensual": m_plus[0], "Total pagado": m_plus[1], "Total intereses": m_plus[2]}[metrica]
        mm = {"Pago mensual": m_minus[0], "Total pagado": m_minus[1], "Total intereses": m_minus[2]}[metrica]

        # Desviación relativa al base
        delta_plus = mp - base_metric
        delta_minus = mm - base_metric

        filas.append({
            "Variable": label,
            "+Δ%": delta_tornado,
            "Cambio +Δ": delta_plus,
            "Cambio -Δ": delta_minus,
            "Base": base_metric,
        })

    df_tornado = pd.DataFrame(filas)
    # ordenar por impacto máximo absoluto
    df_tornado["Impacto abs max"] = df_tornado[["Cambio +Δ", "Cambio -Δ"]].abs().max(axis=1)
    df_tornado = df_tornado.sort_values("Impacto abs max", ascending=True).reset_index(drop=True)  # asc para hospedarlo como “tornado horizontal”
    st.session_state.sens_result["tornado"] = (metrica, df_tornado)

if "tornado" in st.session_state.sens_result:
    metrica, df_tornado = st.session_state.sens_result["tornado"]

    st.markdown(f"#### Tornado — impacto sobre **{metrica}**")
    # Vista formateada
    df_view = df_tornado.copy()
    if "Pago" in metrica or "Total" in metrica or "Intereses" in metrica:
        fmt = lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}"
    else:
        fmt = lambda x: f"{x:,.{cfg['decimals_money']}f}"
    df_view["Cambio +Δ"] = df_view["Cambio +Δ"].map(fmt)
    df_view["Cambio -Δ"] = df_view["Cambio -Δ"].map(fmt)
    df_view["Base"] = df_view["Base"].map(fmt)
    df_view = df_view.drop(columns=["Impacto abs max"])
    st.dataframe(df_view, use_container_width=True, hide_index=True)

    # Gráfico tipo tornado (aproximado con barras horizontales)
    st.markdown("**Visualización del tornado (barras horizontales)**")
    # Construir dataset para barras: dos series por variable
    plot_df = df_tornado[["Variable", "Cambio +Δ", "Cambio -Δ"]].set_index("Variable")
    # Streamlit no soporta nativamente barras horizontales con orientación directa,
    # pero podemos mostrar dos columnas como barras por variable (absoluto).
    # Para una imagen más clásica se puede usar altair, pero evitamos dependencias extra.
    gcol1, gcol2 = st.columns(2)
    with gcol1:
        st.markdown("**Cambio -Δ (izquierda)**")
        st.bar_chart(plot_df["Cambio -Δ"].abs(), x_label="Variable", y_label="|Δ|")
    with gcol2:
        st.markdown("**Cambio +Δ (derecha)**")
        st.bar_chart(plot_df["Cambio +Δ"].abs(), x_label="Variable", y_label="|Δ|")

    st.markdown("#### Descargas")
    # CSV
    csv_bytes = df_tornado.to_csv(index=False).encode("utf-8")
    st.download_button("CSV (tornado)", data=csv_bytes,
                       file_name="tornado.csv", mime="text/csv", use_container_width=True)
    # Excel
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        df_tornado.to_excel(writer, sheet_name="Tornado", index=False)
    excel_buf.seek(0)
    st.download_button("Excel (tornado)", data=excel_buf,
                       file_name="tornado.xlsx",
                       mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
                       use_container_width=True)

    # PDF
    titulo = f"Tornado — impacto sobre {metrica}"
    parametros = {
        "Escenario base": f"Monto: {cfg['symbol']}{st.session_state.sens_base['monto']:,.2f} | "
                          f"Tasa: {st.session_state.sens_base['tasa_anual']:.2f}% | "
                          f"Plazo: {st.session_state.sens_base['plazo_meses']} meses",
        "Δ% simétrico": f"{st.session_state.sens_cfg['decimals_pct']}% (configurable en formulario)",
    }
    df_pdf = df_view.astype(str)
    pdf_bytes = generar_pdf_tabla(df_pdf, titulo, parametros)
    if hasattr(pdf_bytes, "getvalue"):
        pdf_bytes = pdf_bytes.getvalue()
    st.download_button("PDF (tornado)", data=pdf_bytes,
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
    st.session_state.sens_cfg = cfg
    st.success("Formato actualizado.")
