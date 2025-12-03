# ui/pages/tasa_creditos.py
from decimal import Decimal
import pandas as pd
import streamlit as st

from core.rate_solver import RateSolver
from services.export_service import ExportService
from utils.session_state import get_state, set_state, has_state
from utils.formatters import format_currency, format_percentage

# ======================
#   Estado / Config UI
# ======================
if not has_state("creditos"):
    set_state("creditos", [])

# Configuración SOLO para esta página (evita colisiones con otras)
if not has_state("cfg_tasas"):
    set_state("cfg_tasas", {
        "currency_symbol": "$",
        "decimals_money": 2,
        "decimals_pct": 2,
    })
cfg = get_state("cfg_tasas")

# Estado de inputs del formulario
for key, default in {
    "nombre_credito_input": "",
    "monto_input": 0.0,
    "num_pagos_input": 0,
    "pago_input": 0.0,
}.items():
    if not has_state(key):
        set_state(key, default)

# Limpieza de formulario vía bandera
if get_state("clear_form", False):
    set_state("nombre_credito_input", "")
    set_state("monto_input", 0.0)
    set_state("num_pagos_input", 0)
    set_state("pago_input", 0.0)
    set_state("clear_form", False)
    st.rerun()

# ======================
#   Encabezado
# ======================
st.markdown("# :blue[Comparador de Tasas de Crédito]")
st.caption("Agrega créditos y compara tasa mensual, tasa anual nominal y tasa anual efectiva (TAE).")

# ==============
#   Formulario
# ==============
with st.expander("➕ **Agregar crédito**", expanded=(len(get_state("creditos")) == 0)):
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
        set_state("clear_form", True)
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
            # Usar RateSolver para calcular la tasa
            solver = RateSolver()
            tasa_m = solver.solve_monthly_rate(
                Decimal(str(monto)),
                Decimal(str(pago)),
                int(num_pagos)
            )
            
            if tasa_m is None or tasa_m < 0:
                st.error("No se pudo calcular una tasa válida. Verifica los datos.", icon="🚨")
            else:
                tasa_m_float = float(tasa_m)
                fila = {
                    "Nombre crédito": nom_credito.strip(),
                    "Número de pagos": int(num_pagos),
                    "Pago": float(pago),
                    "Monto del crédito": float(monto),
                    "Tasa mensual": tasa_m_float,                           # proporción (0.02 = 2%)
                    "Tasa anual nominal": tasa_m_float * 12,                # proporción
                    "Tasa anual efectiva": (1.0 + tasa_m_float)**12 - 1.0,  # proporción
                }
                creditos = get_state("creditos")
                creditos.append(fila)
                set_state("creditos", creditos)
                st.success("Crédito agregado correctamente ✅")
                # Limpia el formulario para el siguiente registro
                set_state("clear_form", True)
                st.rerun()

# =================
#   Contenido
# =================
if len(get_state("creditos")) == 0:
    st.info("Agrega al menos un crédito para comenzar.")
else:
    df = pd.DataFrame(get_state("creditos"))

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

        # Vista formateada SOLO para presentación
        df_display = df_sorted.copy()
        df_display["Pago"] = df_display["Pago"].map(
            lambda x: format_currency(Decimal(str(x)), cfg['currency_symbol'], cfg['decimals_money']) if pd.notna(x) else ""
        )
        df_display["Monto del crédito"] = df_display["Monto del crédito"].map(
            lambda x: format_currency(Decimal(str(x)), cfg['currency_symbol'], cfg['decimals_money']) if pd.notna(x) else ""
        )
        df_display["Tasa mensual"] = df_display["Tasa mensual"].map(
            lambda x: format_percentage(Decimal(str(x)), cfg['decimals_pct']) if pd.notna(x) else ""
        )
        df_display["Tasa anual nominal"] = df_display["Tasa anual nominal"].map(
            lambda x: format_percentage(Decimal(str(x)), cfg['decimals_pct']) if pd.notna(x) else ""
        )
        df_display["Tasa anual efectiva"] = df_display["Tasa anual efectiva"].map(
            lambda x: format_percentage(Decimal(str(x)), cfg['decimals_pct']) if pd.notna(x) else ""
        )

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
                set_state("creditos", [])
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

        # Preparar metadata
        metadata = {
            "title": "Tabla comparativa de tasas",
            "parameters": {
                "Información 1": "Prioriza la **TAE** para comparar créditos.",
                "Información 2": "Como segunda métrica, revisa la **tasa nominal anual**.",
                "Información 3": "La **tasa mensual** ayuda a evaluar el impacto inmediato.",
            },
            "currency_symbol": cfg["currency_symbol"],
            "decimals": cfg["decimals_money"]
        }
        
        export_service = ExportService()
        
        # CSV (numérico)
        csv_buffer = export_service.export('csv', df, metadata)
        st.download_button(
            "CSV (datos numéricos)",
            data=csv_buffer,
            file_name="comparador_tasas.csv",
            mime="text/csv",
            use_container_width=True,
        )

        # Excel (dos hojas: datos y vista formateada)
        excel_metadata = {**metadata, "formatted_df": df_display}
        excel_buffer = export_service.export('excel', df, excel_metadata)
        st.download_button(
            "Excel",
            data=excel_buffer,
            file_name="comparador_tasas.xlsx",
            mime="application/vnd.openxmlformats-officedocument.spreadsheetml.sheet",
            use_container_width=True,
        )

        # PDF
        st.divider()
        st.caption("PDF con observaciones y tabla formateada.")
        
        pdf_buffer = export_service.export('pdf', df_display, metadata)
        st.download_button(
            "PDF",
            data=pdf_buffer,
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
            set_state("cfg_tasas", cfg)
            st.success("Formato actualizado.")
