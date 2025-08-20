# tasa_creditos.py
import io
import pandas as pd
import streamlit as st
from functions import calcular_tasa, generar_pdf_tabla

# ======================
#   Estado / Config UI
# ======================
if "creditos" not in st.session_state:
    st.session_state.creditos = []

# Configuración SOLO para esta página (evita colisiones con otras)
if "cfg_tasas" not in st.session_state:
    st.session_state.cfg_tasas = {
        "currency_symbol": "$",
        "decimals_money": 2,
        "decimals_pct": 2,
    }
cfg = st.session_state.cfg_tasas

# Estado de inputs del formulario
for key, default in {
    "nombre_credito_input": "",
    "monto_input": 0.0,
    "num_pagos_input": 0,
    "pago_input": 0.0,
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Limpieza de formulario vía bandera
if st.session_state.get("clear_form", False):
    st.session_state.nombre_credito_input = ""
    st.session_state.monto_input = 0.0
    st.session_state.num_pagos_input = 0
    st.session_state.pago_input = 0.0
    st.session_state.clear_form = False
    st.rerun()

# ======================
#   Encabezado
# ======================
st.markdown("# :blue[Comparador de Tasas de Crédito]")
st.caption("Agrega créditos y compara tasa mensual, tasa anual nominal y tasa anual efectiva (TAE).")

# ==============
#   Formulario
# ==============
with st.expander("➕ **Agregar crédito**", expanded=(len(st.session_state.creditos) == 0)):
    with st.form("credito_form", border=True):
        c1, c2, c3, c4 = st.columns([1.2, 1, 1, 1])
        with c1:
            nom_credito = st.text_input(
                "**Nombre del crédito**",
                placeholder="Crédito 1",
                key="nombre_credito_input",
            )
        with c2:
            monto = st.number_input(
                "**Monto del crédito**",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="monto_input",
            )
        with c3:
            num_pagos = st.number_input(
                "**Número de pagos**",
                min_value=0,
                step=1,
                key="num_pagos_input",
            )
        with c4:
            pago = st.number_input(
                "**Pago (mensual)**",
                min_value=0.0,
                step=100.0,
                format="%.2f",
                key="pago_input",
            )

        b1, b2 = st.columns(2)
        with b1:
            add_btn = st.form_submit_button("Agregar", type="primary", use_container_width=True)
        with b2:
            clear_btn = st.form_submit_button("Limpiar formulario", use_container_width=True)

    # Acciones del formulario
    if clear_btn:
        st.session_state.clear_form = True
        st.rerun()

    if add_btn:
        if not nom_credito.strip():
            st.error("Indica el **nombre** del crédito.", icon="🚨")
        elif monto <= 0:
            st.error("El **monto** debe ser mayor a 0.", icon="🚨")
        elif num_pagos <= 0:
            st.error("El **número de pagos** debe ser mayor a 0.", icon="🚨")
        elif pago <= 0:
            st.error("El **pago mensual** debe ser mayor a 0.", icon="🚨")
        elif (pago * num_pagos) <= monto:
            st.error("El total de pagos (pago × meses) debe ser **mayor** al monto del crédito.", icon="🚨")
            st.warning(
                f"Detalles: pago = {pago:,.2f}, meses = {num_pagos}, total = {pago * num_pagos:,.2f} "
                f"≤ monto = {monto:,.2f}"
            )
        else:
            tasa_m = calcular_tasa(int(num_pagos), float(pago), float(monto))
            if tasa_m is None or tasa_m < 0:
                st.error("No se pudo calcular una tasa válida. Verifica los datos.", icon="🚨")
            else:
                fila = {
                    "Nombre crédito": nom_credito.strip(),
                    "Número de pagos": int(num_pagos),
                    "Pago": float(pago),
                    "Monto del crédito": float(monto),
                    "Tasa mensual": float(tasa_m),                           # proporción (0.02 = 2%)
                    "Tasa anual nominal": float(tasa_m) * 12,                # proporción
                    "Tasa anual efectiva": (1.0 + float(tasa_m))**12 - 1.0,  # proporción
                }
                st.session_state.creditos.append(fila)
                st.success("Crédito agregado correctamente ✅")
                # Limpia el formulario para el siguiente registro
                st.session_state.clear_form = True
                st.rerun()

# =================
#   Contenido
# =================
if len(st.session_state.creditos) == 0:
    st.info("Agrega al menos un crédito para comenzar.")
else:
    df = pd.DataFrame(st.session_state.creditos)

    # KPIs rápidos (promedios y mejor TAE)
    try:
        mejor_idx = df["Tasa anual efectiva"].idxmin()
        mejor_nombre = df.loc[mejor_idx, "Nombre crédito"]
        mejor_tae = df.loc[mejor_idx, "Tasa anual efectiva"]
    except Exception:
        mejor_nombre, mejor_tae = "—", float("nan")

    c1, c2, c3 = st.columns(3)
    with c1:
        st.metric("Créditos cargados", f"{len(df)}")
    with c2:
        st.metric("Promedio TAE", f"{df['Tasa anual efectiva'].mean():.2%}" if len(df) else "—")
    with c3:
        st.metric("Mejor TAE", f"{mejor_tae:.2%}" if pd.notna(mejor_tae) else "—", help=f"Crédito con menor TAE: {mejor_nombre}")

    st.markdown("---")

    # =================
    #   Pestañas
    # =================
    tab_tabla, tab_graficas, tab_export, tab_formato = st.tabs(
        ["🧾 Tabla comparativa", "📊 Gráficas", "📥 Descargas", "⚙️ Formato"]
    )

    # ----------------
    #   TAB: Tabla
    # ----------------
    with tab_tabla:
        st.subheader("Resumen de créditos")

        opciones_orden = [
            "Nombre crédito",
            "Número de pagos",
            "Pago",
            "Monto del crédito",
            "Tasa mensual",
            "Tasa anual nominal",
            "Tasa anual efectiva",
        ]
        col_sort, col_order = st.columns([2, 1])
        with col_sort:
            orden_col = st.selectbox("Ordenar por", options=opciones_orden, index=opciones_orden.index("Tasa anual efectiva"))
        with col_order:
            asc = st.toggle("Ascendente", value=True)

        df_sorted = df.sort_values(orden_col, ascending=asc).reset_index(drop=True)

        # Lambdas de formateo robustas
        money = lambda x: f"{cfg['currency_symbol']}{x:,.{cfg['decimals_money']}f}" if pd.notna(x) else ""
        pct   = lambda x: f"{x:.{cfg['decimals_pct']}%}" if pd.notna(x) else ""

        # Vista formateada SOLO para presentación
        df_display = df_sorted.copy()
        df_display["Pago"] = df_display["Pago"].map(money)
        df_display["Monto del crédito"] = df_display["Monto del crédito"].map(money)
        df_display["Tasa mensual"] = df_display["Tasa mensual"].map(pct)
        df_display["Tasa anual nominal"] = df_display["Tasa anual nominal"].map(pct)
        df_display["Tasa anual efectiva"] = df_display["Tasa anual efectiva"].map(pct)

        st.dataframe(
            df_display[
                [
                    "Nombre crédito",
                    "Número de pagos",
                    "Pago",
                    "Monto del crédito",
                    "Tasa mensual",
                    "Tasa anual nominal",
                    "Tasa anual efectiva",
                ]
            ],
            hide_index=True,
            use_container_width=True,
        )

        col_left, col_right = st.columns(2)
        with col_left:
            if st.button("🧹 Limpiar todos los créditos", use_container_width=True):
                st.session_state.creditos = []
                st.rerun()
        with col_right:
            st.caption("Sugerencia: ordena por **TAE** para identificar la mejor opción.")

    # ----------------
    #   TAB: Gráficas
    # ----------------
    with tab_graficas:
        st.subheader("Comparativas visuales")
        g1, g2 = st.columns(2)

        with g1:
            st.markdown("**Tasa anual efectiva (TAE)**")
            st.bar_chart(
                df.set_index("Nombre crédito")["Tasa anual efectiva"] * 100,
                x_label="Créditos",
                y_label="TAE (%)",
            )

        with g2:
            st.markdown("**Nominal vs efectiva**")
            comp = df.set_index("Nombre crédito")[["Tasa anual nominal", "Tasa anual efectiva"]].mul(100)
            st.bar_chart(comp, x_label="Créditos", y_label="Tasa (%)")

    # ----------------
    #   TAB: Descargas
    # ----------------
    with tab_export:
        st.subheader("Descargas")

        # CSV (numérico)
        csv_bytes = df.to_csv(index=False).encode("utf-8-sig")
        st.download_button(
            "CSV (datos numéricos)",
            data=csv_bytes,
            file_name="comparador_tasas.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Excel (dos hojas: datos y vista formateada)
        excel_buf = io.BytesIO()
        with pd.ExcelWriter(excel_buf, engine="xlsxwriter") as writer:
            df.to_excel(writer, sheet_name="Datos", index=False)
            df_display.to_excel(writer, sheet_name="Vista", index=False)
        excel_buf.seek(0)
        st.download_button(
            "Excel",
            data=excel_buf,
            file_name="comparador_tasas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        # PDF (usa tu utilidad)
        st.divider()
        st.caption("PDF con observaciones y tabla formateada.")
        titulo = "Tabla comparativa de tasas"
        parametros = {
            "Información 1": "Prioriza la **TAE** para comparar créditos.",
            "Información 2": "Como segunda métrica, revisa la **tasa nominal anual**.",
            "Información 3": "La **tasa mensual** ayuda a evaluar el impacto inmediato.",
        }

        df_pdf = df_display.copy().astype(str)  # texto seguro para ReportLab
        pdf_bytes = generar_pdf_tabla(df_pdf, titulo, parametros)
        if hasattr(pdf_bytes, "getvalue"):  # compatibilidad si regresa BytesIO
            pdf_bytes = pdf_bytes.getvalue()

        st.download_button(
            "PDF",
            data=pdf_bytes,
            file_name="comparador_tasas.pdf",
            mime="application/pdf",
            use_container_width=True,
        )

    # ----------------
    #   TAB: Formato
    # ----------------
    with tab_formato:
        st.subheader("Preferencias de formato")
        cA, cB, cC = st.columns(3)
        with cA:
            symbol = st.selectbox(
                "Símbolo de moneda",
                ["$", "MXN$", "USD$", "€", "£"],
                index=["$", "MXN$", "USD$", "€", "£"].index(cfg["currency_symbol"])
                if cfg["currency_symbol"] in ["$", "MXN$", "USD$", "€", "£"]
                else 0,
            )
        with cB:
            dec_m = st.number_input(
                "Decimales (dinero)",
                min_value=0,
                max_value=4,
                value=int(cfg["decimals_money"]),
                step=1,
            )
        with cC:
            dec_p = st.number_input(
                "Decimales (%)",
                min_value=0,
                max_value=4,
                value=int(cfg["decimals_pct"]),
                step=1,
            )

        if (symbol != cfg["currency_symbol"]) or (dec_m != cfg["decimals_money"]) or (dec_p != cfg["decimals_pct"]):
            cfg["currency_symbol"] = symbol
            cfg["decimals_money"] = int(dec_m)
            cfg["decimals_pct"] = int(dec_p)
            st.session_state.cfg_tasas = cfg  # guardar cambios en sesión
            st.success("Formato actualizado.")
