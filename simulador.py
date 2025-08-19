# simulador.py
import io
import math
import pandas as pd
import streamlit as st
from functions import calcular_pago_mensual, tabla_amortizacion, generar_pdf_tabla

# ======================
#   Estado / Config UI
# ======================
if "sim_cfg" not in st.session_state:
    st.session_state.sim_cfg = {
        "symbol": "$",
        "decimals_money": 2,
        "decimals_pct": 2,
    }
cfg = st.session_state.sim_cfg

if "escenarios_guardados" not in st.session_state:
    st.session_state.escenarios_guardados = []  # lista de dict con los parámetros y métricas

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
    pago = calcular_pago_mensual(tasa_anual, monto, int(plazo_meses))
    df_base = tabla_amortizacion(pago, tasa_anual, monto, int(plazo_meses))
    st.session_state.sim_base = {
        "monto": monto,
        "tasa_anual": tasa_anual,
        "plazo_meses": int(plazo_meses),
        "pago": pago,
        "tabla": df_base,
    }

if "sim_base" in st.session_state:
    base = st.session_state.sim_base
    df_tabla = base["tabla"]
    pago = base["pago"]

    total_pagado = float(df_tabla["Pago"].sum())
    total_interes = float(df_tabla["Interés"].sum())

    a, b, c, d = st.columns(4)
    with a:
        st.metric("Pago mensual", f"{cfg['symbol']}{pago:,.{cfg['decimals_money']}f}")
    with b:
        st.metric("Tasa anual", f"{base['tasa_anual']:.{cfg['decimals_pct']}f}%")
    with c:
        st.metric("Total pagado", f"{cfg['symbol']}{total_pagado:,.{cfg['decimals_money']}f}")
    with d:
        st.metric("Total intereses", f"{cfg['symbol']}{total_interes:,.{cfg['decimals_money']}f}")

    st.markdown("### 🧾 Tabla de amortización (escenario base)")
    df_show = df_tabla.copy()
    df_show["Mes"] = df_show["Mes"].astype(int)
    money_fmt = lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}"
    df_show["Pago"] = df_show["Pago"].map(money_fmt)
    df_show["Interés"] = df_show["Interés"].map(money_fmt)
    df_show["Abono a capital"] = df_show["Abono a capital"].map(money_fmt)
    df_show["Saldo restante"] = df_show["Saldo restante"].map(money_fmt)
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
    # CSV
    csv_bytes = df_tabla.to_csv(index=False).encode("utf-8")
    st.download_button(
        "CSV",
        data=csv_bytes,
        file_name="amortizacion_escenario_base.csv",
        mime="text/csv",
        use_container_width=True,
    )
    # Excel
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        df_tabla.to_excel(writer, sheet_name="Amortizacion", index=False)
        pd.DataFrame(
            {"Pago mensual": [pago], "Total pagado": [total_pagado], "Total intereses": [total_interes]}
        ).to_excel(writer, sheet_name="Resumen", index=False)
    excel_buf.seek(0)
    st.download_button(
        "Excel",
        data=excel_buf,
        file_name="amortizacion_escenario_base.xlsx",
        mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
        use_container_width=True,
    )
    # PDF
    titulo = "Escenario base - Tabla de amortización"
    parametros = {
        "Crédito": f"Monto: {cfg['symbol']}{base['monto']:,.2f} — Tasa anual: {base['tasa_anual']:.2f}% — Plazo: {base['plazo_meses']} meses",
        "Resultado": f"Pago mensual: {cfg['symbol']}{base['pago']:,.2f} | Total pagado: {cfg['symbol']}{total_pagado:,.2f} | Intereses: {cfg['symbol']}{total_interes:,.2f}",
    }
    df_pdf = df_show.astype(str)
    pdf_bytes = generar_pdf_tabla(df_pdf, titulo, parametros)
    if hasattr(pdf_bytes, "getvalue"):
        pdf_bytes = pdf_bytes.getvalue()
    st.download_button(
        "PDF",
        data=pdf_bytes,
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
    if vmax <= vmin or (param != "Monto del crédito" and vstep <= 0) or (param == "Monto del crédito" and vstep <= 0.0):
        st.error("Revisa el rango y el paso del barrido.", icon="🚨")
    else:
        registros = []
        # Construir serie de valores
        def frange(a, b, step):
            # rango inclusivo; evita acumulación flotante
            kmax = int(math.floor((b - a) / step)) + 1
            return [a + i * step for i in range(kmax)]

        valores = frange(vmin, vmax, vstep)

        for val in valores:
            if param == "Tasa anual nominal (%)":
                tasa_ = val
                monto_ = monto
                plazo_ = int(plazo_meses)
            elif param == "Plazo (meses)":
                tasa_ = tasa_anual
                monto_ = monto
                plazo_ = int(val)
            else:  # Monto
                tasa_ = tasa_anual
                monto_ = float(val)
                plazo_ = int(plazo_meses)

            pago_ = calcular_pago_mensual(tasa_, monto_, plazo_)
            tabla_ = tabla_amortizacion(pago_, tasa_, monto_, plazo_)
            total_pagado_ = float(tabla_["Pago"].sum())
            total_interes_ = float(tabla_["Interés"].sum())

            registros.append({
                "Parámetro": param,
                "Valor": val,
                "Pago mensual": pago_,
                "Total pagado": total_pagado_,
                "Total intereses": total_interes_,
                "Monto": monto_,
                "Tasa anual": tasa_,
                "Plazo (meses)": plazo_,
            })

        df_sweep = pd.DataFrame(registros)
        st.session_state.df_sweep = df_sweep

if "df_sweep" in st.session_state:
    df_sweep = st.session_state.df_sweep
    st.markdown("### Resultados del barrido")
    money = lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}"
    pct = lambda x: f"{x:.{cfg['decimals_pct']}f}%"
    df_view = df_sweep.copy()
    df_view["Pago mensual"] = df_view["Pago mensual"].map(money)
    df_view["Total pagado"] = df_view["Total pagado"].map(money)
    df_view["Total intereses"] = df_view["Total intereses"].map(money)
    df_view["Tasa anual"] = df_view["Tasa anual"].map(pct)

    st.dataframe(
        df_view[["Parámetro", "Valor", "Pago mensual", "Total pagado", "Total intereses", "Monto", "Tasa anual", "Plazo (meses)"]],
        use_container_width=True,
        hide_index=True,
    )

    st.markdown("### 📊 Gráficas del barrido")
    g1, g2, g3 = st.columns(3)
    with g1:
        st.markdown("**Pago mensual**")
        st.line_chart(df_sweep.set_index("Valor")["Pago mensual"], x_label="Valor", y_label="Pago")
    with g2:
        st.markdown("**Total pagado**")
        st.line_chart(df_sweep.set_index("Valor")["Total pagado"], x_label="Valor", y_label="Total")
    with g3:
        st.markdown("**Total intereses**")
        st.line_chart(df_sweep.set_index("Valor")["Total intereses"], x_label="Valor", y_label="Intereses")

    st.markdown("### 📥 Descargas del barrido")
    # CSV
    csv_bytes = df_sweep.to_csv(index=False).encode("utf-8")
    st.download_button(
        "CSV (barrido)",
        data=csv_bytes,
        file_name="barrido_escenarios.csv",
        mime="text/csv",
        use_container_width=True,
    )
    # Excel
    excel_buf = io.BytesIO()
    with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
        df_sweep.to_excel(writer, sheet_name="Barrido", index=False)
    excel_buf.seek(0)
    st.download_button(
        "Excel (barrido)",
        data=excel_buf,
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
        base = st.session_state.sim_base
        df_tabla = base["tabla"]
        total_pagado = float(df_tabla["Pago"].sum())
        total_interes = float(df_tabla["Interés"].sum())
        st.session_state.escenarios_guardados.append({
            "Nombre": (nombre.strip() or "Escenario"),
            "Monto": float(base["monto"]),
            "Tasa anual": float(base["tasa_anual"]),
            "Plazo (meses)": int(base["plazo_meses"]),
            "Pago mensual": float(base["pago"]),
            "Total pagado": total_pagado,
            "Total intereses": total_interes,
        })
        st.success("Escenario guardado ✅")
        st.rerun()

if len(st.session_state.escenarios_guardados) > 0:
    df_comp = pd.DataFrame(st.session_state.escenarios_guardados)
    # Vista formateada
    df_comp_v = df_comp.copy()
    df_comp_v["Pago mensual"] = df_comp_v["Pago mensual"].map(lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}")
    df_comp_v["Total pagado"] = df_comp_v["Total pagado"].map(lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}")
    df_comp_v["Total intereses"] = df_comp_v["Total intereses"].map(lambda x: f"{cfg['symbol']}{x:,.{cfg['decimals_money']}f}")
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
            st.session_state.escenarios_guardados = st.session_state.escenarios_guardados[:-1]
            st.rerun()
    with cdel2:
        if st.button("Limpiar todos", use_container_width=True):
            st.session_state.escenarios_guardados = []
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
    st.session_state.sim_cfg = cfg
    st.success("Formato actualizado.")
