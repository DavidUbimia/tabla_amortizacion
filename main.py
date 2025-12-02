# main.py
import streamlit as st

# ────────────────────────────────────────────────────────────────
# Configuración de página
# ────────────────────────────────────────────────────────────────
st.set_page_config(
    page_title="Créditos | Amortización y Tasas",
    page_icon="💳",
    layout="wide",
    initial_sidebar_state="expanded",
)

# ────────────────────────────────────────────────────────────────
# Estilos rápidos (opcionales)
# ────────────────────────────────────────────────────────────────
CUSTOM_CSS = """
<style>
h1, .stMarkdown h1 { 
    font-weight: 800 !important;
    letter-spacing: .2px;
}
hr { opacity: .25; }
.footer-note {
    font-size: 0.85rem;
    opacity: 0.7;
    margin-top: .75rem;
}
.block-container { padding-top: 1.2rem; }
.sidebar-help p { margin-bottom: .35rem; }
</style>
"""
st.markdown(CUSTOM_CSS, unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# Barra lateral: branding y ayuda rápida
# ────────────────────────────────────────────────────────────────
with st.sidebar:
    st.markdown("### 💳 Herramientas de crédito")
    st.caption("Calcula pagos, compara tasas y analiza escenarios.")

    with st.popover("ℹ️ Ayuda rápida"):
        st.markdown(
            """
            **Básicos**
            - *Tabla de amortización*: calcula la mensualidad y el desglose.
            - *Tasa de créditos*: compara tasa mensual, nominal y efectiva.

            **Avanzados**
            - *Simulador de escenarios*: prueba diferentes montos/plazos/tasas.
            - *Análisis de sensibilidad*: barridos y gráfico tipo tornado.
            """
        )

    st.divider()
    st.markdown(
        """
        **Tip:** Tras cambiar parámetros usa **Calcular** / **Agregar** para refrescar.
        """,
        help="Cada página gestiona su propio estado con `st.session_state`."
    )

    st.divider()
    st.markdown('<div class="footer-note">SciDatDav</div>', unsafe_allow_html=True)

# ────────────────────────────────────────────────────────────────
# Navegación: grupos Básicos y Avanzados
# ────────────────────────────────────────────────────────────────
pages = {
    "Básicos": [
        st.Page("ui/pages/tabla_amortizacion.py", title="🧾 Tabla amortización"),
        st.Page("ui/pages/tasa_creditos.py",   title="📊 Tasa créditos"),
    ],
    "Avanzados": [
        st.Page("ui/pages/simulador.py",    title="🔮 Simulador de escenarios"),
        st.Page("ui/pages/sensibilidad.py", title="📉 Análisis de sensibilidad"),
    ],
}

nav = st.navigation(pages=pages, position="sidebar", expanded=True)

# ────────────────────────────────────────────────────────────────
# Ejecutar la página seleccionada
# ────────────────────────────────────────────────────────────────
nav.run()



