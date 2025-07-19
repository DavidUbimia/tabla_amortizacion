import streamlit as st
import pandas as pd
import streamlit as st

import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io

from functions import *


# Inicializaciones
st.session_state.tabla=None
st.session_state.df_display = None

st.markdown("# :blue[💰 Tabla de amortización]")

st.markdown("#### Introduce los datos del crédito:")

# Formulario
with st.form("form_credito"):
    tasa_input = st.number_input("**Tasa de interés anual (% Nominal)**", min_value=0.0, step=0.1, value=10.0, format="%.2f")
    monto_input = st.number_input("**Monto del crédito ($)**", min_value=0.0, step=100.0, value=10000.0, format="%.2f")
    pagos_input = st.number_input("**Número de pagos (meses)**", min_value=1, step=12, value=12)

    submitted = st.form_submit_button("Calcular")

# Resultado
if submitted:
    pago = calcular_pago_mensual(tasa_input, monto_input, pagos_input)
    st.session_state.tabla = tabla_amortizacion(pago, tasa_input, monto_input, pagos_input)

    st.markdown("---")
    st.subheader("📊 Estimación pago mensual")
    st.write(f"**Tasa anual:** {tasa_input:.2f}%")
    st.write(f"**Monto del crédito:** ${monto_input:,.2f}")
    st.write(f"**Número de pagos:** {pagos_input} meses")
    st.success(f"💸 El pago mensual estimado es: **${pago:,.2f}**")



    st.write("")
    st.markdown("---")
    st.markdown("### 🧾 Tabla de amortización")
    df_display = st.session_state.tabla.copy()
    # Formateo de columnas
    df_display["Mes"] = df_display["Mes"].astype(int)  # Mes como entero sin decimales
    df_display["Pago"] = df_display["Pago"].map("${:,.2f}".format)  # Formato monetario
    df_display["Interés"] = df_display["Interés"].map("${:,.2f}".format)  # Formato monetario
    df_display["Abono a capital"] = df_display["Abono a capital"].map("${:,.2f}".format)  # Formato monetario
    df_display["Saldo restante"] = df_display["Saldo restante"].map("${:,.2f}".format)  # Formato monetario

    st.session_state.df_display = df_display
    st.dataframe(df_display, use_container_width=True,hide_index=True)

    st.write("")
    st.markdown("---")
    st.markdown("### $ Totales")
    tabla = st.session_state.tabla.copy()
    df_totales=pd.DataFrame({
        'Total monto a pagar': [tabla['Pago'].sum()],
        'Total interés a pagar': [tabla['Interés'].sum()]
    })

    df_totales['Total monto a pagar'] = df_totales['Total monto a pagar'].map("${:,.1f}".format)
    df_totales['Total interés a pagar'] = df_totales['Total interés a pagar'].map("${:,.1f}".format)

    st.dataframe(df_totales, use_container_width=True,hide_index=True)

    #---------------------------------------------- Impresión de pdf
    # Parámetros
    # Título y parámetros
    titulo = "Tabla de amortización"
    param1 = f"Monto crédito: ${monto_input:,.2f} — Tasa nominal anual: {tasa_input:.2f}% — Número de Pagos: {pagos_input}"
    param2 = f"Mensualidad estimada: ${pago:,.2f}"

    parametros = {
        "Datos del crédito": param1,
        "Resultado": param2
    }

    # Prepara el DataFrame como texto
    df_pdf = df_display.copy()
    for col in df_pdf.columns:
        df_pdf[col] = df_pdf[col].astype(str)

    # Generar PDF
    # pdf_bytes = generar_pdf(df_pdf, titulo, parametros)
    pdf_bytes = generar_pdf_tabla(df_pdf, titulo, parametros)
    # Descargar
    st.download_button(
        label="📥 Descargar PDF",
        data=pdf_bytes,
        file_name="tabla_amortizacion.pdf",
        mime="application/pdf"
    )




