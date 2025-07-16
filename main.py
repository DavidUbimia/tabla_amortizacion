import streamlit as st

st.set_page_config(page_title="Tool credits")


pages = {
    "Calculadoras": [
        st.Page("tabla_amortizacion.py", title="Tabla amortización"),
        st.Page("tasa_creditos.py", title="Tasa créditos")
    ] 
}

pages = st.navigation(pages=pages, position="sidebar",expanded=True)
pages.run()


