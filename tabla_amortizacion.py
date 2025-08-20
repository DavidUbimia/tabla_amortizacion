# tabla_amortizacion.py
import io
import pandas as pd
import streamlit as st

from functions import calcular_pago_mensual, tabla_amortizacion, generar_pdf_tabla, style_amort

# ======================
#   Estado / Config UI
# ======================
if "tabla" not in st.session_state:
    st.session_state.tabla = None
if "pago" not in st.session_state:
    st.session_state.pago = None
if "inputs" not in st.session_state:
    st.session_state.inputs = {"tasa": 10.0, "monto": 10000.0, "pagos": 12}
if "cfg" not in st.session_state:
    st.session_state.cfg = {"currency_symbol": "$", "decimals": 2, "show_row0": True}

cfg = st.session_state.cfg
inp = st.session_state.inputs

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
    st.session_state.inputs = {"tasa": tasa_input, "monto": monto_input, "pagos": int(pagos_input)}
    # Calculamos y guardamos en sesión
    pago = calcular_pago_mensual(tasa_input, monto_input, int(pagos_input))
    st.session_state.pago = pago
    st.session_state.tabla = tabla_amortizacion(pago, tasa_input, monto_input, int(pagos_input))



# =================
#   Resultados UI
# =================
if st.session_state.tabla is not None and st.session_state.pago is not None:
    tabla_df = st.session_state.tabla.copy()
    pago = st.session_state.pago
    tasa_input = st.session_state.inputs["tasa"]
    monto_input = st.session_state.inputs["monto"]
    pagos_input = st.session_state.inputs["pagos"]

    # KPIs
    total_pagado = float(tabla_df["Pago"].sum())
    total_interes = float(tabla_df["Interés"].sum())
    colA, colB, colC, colD = st.columns([1, 1, 1, 1])
    with colA:
        st.metric("Pago mensual estimado", f"{cfg['currency_symbol']}{pago:,.2f}")
    with colB:
        st.metric("Tasa nominal anual", f"{tasa_input:.2f}%")
    with colC:
        st.metric("Total a pagar", f"{cfg['currency_symbol']}{total_pagado:,.2f}")
    with colD:
        st.metric("Total de intereses", f"{cfg['currency_symbol']}{total_interes:,.2f}")

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

        st.dataframe(
            style_amort(df_show, cfg["currency_symbol"], cfg["decimals"]),
            use_container_width=True,
            hide_index=True,
        )

    # ----------------
    #   TAB: Gráficas
    # ----------------
    with tab_graficas:
        st.subheader("Visualizaciones")
        c1, c2 = st.columns(2)
        with c1:
            st.markdown("**Saldo restante por mes**")
            st.line_chart(
                data=tabla_df.set_index("Mes")["Saldo restante"],
                x_label="Mes", y_label="Saldo restante"
            )
        with c2:
            st.markdown("**Descomposición del pago**")
            st.area_chart(
                data=tabla_df.set_index("Mes")[["Interés", "Abono a capital"]],
                x_label="Mes", y_label="Monto"
            )

    # ---------------------------
    #   TAB: Totales & Descargas
    # ---------------------------
    with tab_totales:
        st.subheader("Totales")
        df_totales = pd.DataFrame(
            {"Total monto a pagar": [total_pagado], "Total interés a pagar": [total_interes]}
        )
        st.dataframe(
            style_amort(df_totales.rename_axis(None, axis=1), cfg["currency_symbol"], cfg["decimals"]),
            use_container_width=True,
            hide_index=True,
        )

        st.markdown("### Descargas")
        # CSV
        csv_bytes = tabla_df.to_csv(index=False).encode('utf-8-sig')
        st.download_button(
            "📥 Descargar CSV",
            data=csv_bytes,
            file_name="tabla_amortizacion.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Excel
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
            tabla_df.to_excel(writer, sheet_name="Amortizacion", index=False)
            df_totales.to_excel(writer, sheet_name="Totales", index=False)
        excel_buf.seek(0)
        st.download_button(
            "📥 Descargar Excel",
            data=excel_buf,
            file_name="tabla_amortizacion.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        # PDF
        st.divider()
        st.caption("PDF con parámetros y formato tabular.")

        titulo = "Tabla de amortización"
        param1 = (
            f"Monto crédito: {cfg['currency_symbol']}{monto_input:,.2f} — "
            f"Tasa nominal anual: {tasa_input:.2f}% — Número de pagos: {int(pagos_input)}"
        )
        param2 = f"Mensualidad estimada: {cfg['currency_symbol']}{pago:,.2f}"
        parametros = {"Datos del crédito": param1, "Resultado": param2}

        df_pdf = tabla_df.copy()
        df_pdf["Mes"] = df_pdf["Mes"].astype(int)
        for col in ["Pago", "Interés", "Abono a capital", "Saldo restante"]:
            df_pdf[col] = df_pdf[col].map(lambda x: f"{cfg['currency_symbol']}{x:,.2f}")
        df_pdf = df_pdf.astype(str)

        pdf_bytes = generar_pdf_tabla(df_pdf, titulo, parametros)
        if hasattr(pdf_bytes, "getvalue"):  # compatibilidad si regresa BytesIO
            pdf_bytes = pdf_bytes.getvalue()

        st.download_button(
            label="📥 Descargar PDF",
            data=pdf_bytes,
            file_name="tabla_amortizacion.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # ----------------
    #   TAB: Formato
    # ----------------
    with tab_formato:
        st.subheader("Preferencias de formato")
        colx, coly = st.columns(2)
        with colx:
            currency_symbol = st.selectbox(
                "Símbolo de moneda", options=["$", "MXN$", "USD$", "€", "£"],
                index=["$", "MXN$", "USD$", "€", "£"].index(cfg["currency_symbol"])
                if cfg["currency_symbol"] in ["$", "MXN$", "USD$", "€", "£"] else 0,
                help="Sólo afecta presentación (no el cálculo)."
            )
        with coly:
            decimals = st.number_input(
                "Decimales para mostrar", min_value=0, max_value=4,
                value=int(cfg["decimals"]), step=1
            )
        if (currency_symbol != cfg["currency_symbol"]) or (decimals != cfg["decimals"]):
            cfg["currency_symbol"] = currency_symbol
            cfg["decimals"] = int(decimals)
            st.success("Formato actualizado.")
else:
    st.info("Completa el formulario y pulsa **Calcular** para ver resultados.")
