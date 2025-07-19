import streamlit as st
import pandas as pd
from functions import *

# Título y descripción
st.markdown("# :blue[Comparador de Tasas de Crédito]")
st.markdown("""
Ingresa los detalles de tus créditos para calcular y comparar las tasas de interés.
La tasa se calcula usando un método numérico propio (Newton-Raphson).
""")

# Inicializar valores en session_state
if 'creditos' not in st.session_state:
    st.session_state.creditos = []

# if 'tab_print' not in st.session_state:
#     st.session_state.tab_print = None

for key, default in {
    "nombre_credito_input": "",
    "num_pagos_input": 0,
    "pago_input": 0,
    "monto_input": 0
}.items():
    if key not in st.session_state:
        st.session_state[key] = default

# Si se activó la limpieza del formulario
if st.session_state.get("clear_form", False):
    st.session_state.nombre_credito_input = ""
    st.session_state.num_pagos_input = 0
    st.session_state.pago_input = 0
    st.session_state.monto_input = 0
    st.session_state.clear_form = False

# Formulario
with st.expander("**Agregar Crédito**", expanded=len(st.session_state.creditos)==0):
    with st.form("credito_form"):
        col1, col2, col3, col4 = st.columns(4)
        with col1:
            nom_credito = st.text_input("**Nombre del crédito**", placeholder="Crédito 1", key="nombre_credito_input")

        with col3:
            num_pagos = st.number_input("**Número de pagos**", min_value=0, step=1, key="num_pagos_input")

        with col4:
            pago = st.number_input("**Pago**", min_value=0, key="pago_input")

        with col2:
            monto = st.number_input("**Monto del crédito**", min_value=0, key="monto_input")

        submitted = st.form_submit_button("**Agregar Crédito**")

        if submitted:
            if nom_credito == '':
                st.error("Indica el nombre del crédito a agregar!", icon="🚨")
            elif monto == 0:
                st.error("El monto del crédito no puede ser cero!", icon="🚨")
            elif num_pagos == 0:
                st.error("El número de pagos no puede ser cero!", icon="🚨")
            elif pago == 0:
                st.error("El pago ó abono no puede ser cero!", icon="🚨")
            elif pago * num_pagos <= monto:
                str_warning = f"[Explicación]: Si se multiplica el pago igual a {pago} por el número de pagos {num_pagos}, el resultado es {pago * num_pagos}, el cual es menor al monto solicitado {monto}. Por ello hay un error."
                st.error("El valor total de pagos debe ser mayor que el monto del crédito!", icon="🚨")
                st.warning(str_warning)
            else:
                tasa = round(calcular_tasa(num_pagos, pago, monto), ndigits=2)
                if tasa is not None and tasa >= 0:
                    nuevo_credito = {
                        'Nombre crédito': nom_credito,
                        'Número de pagos': num_pagos,
                        'Pago': pago,
                        'Monto del crédito': monto,
                        'Tasa mensual': tasa,
                        'Tasa anual nominal': tasa * 12,
                        'Tasa anual efectiva': (1 + tasa)**12 - 1
                    }
                    st.session_state.creditos.append(nuevo_credito)
                    st.success("Crédito agregado correctamente!")

                    # Activar bandera de limpieza y reiniciar
                    st.session_state.clear_form = True
                    st.rerun()
                else:
                    st.error("No se pudo calcular una tasa válida. Verifica los datos.")

# Mostrar resumen de créditos
if len(st.session_state.creditos) > 0:
    st.subheader("Resumen de Créditos")

    df = pd.DataFrame(st.session_state.creditos)

    df_display = df.copy()
    df_display['Pago'] = df_display['Pago'].map("${:,.2f}".format)
    df_display['Monto del crédito'] = df_display['Monto del crédito'].map("${:,.2f}".format)
    df_display['Tasa mensual'] = df_display['Tasa mensual'].apply(lambda x: f"{x:.2%}")
    df_display['Tasa anual nominal'] = df_display['Tasa anual nominal'].apply(lambda x: f"{x:.2%}")
    df_display['Tasa anual efectiva'] = df_display['Tasa anual efectiva'].apply(lambda x: f"{x:.2%}")

    st.dataframe(df_display[['Nombre crédito','Número de pagos', 'Pago', 'Monto del crédito', 
                            'Tasa mensual', 'Tasa anual nominal', 'Tasa anual efectiva']], 
                hide_index=True)

    st.subheader("Comparación de Tasas Anuales Efectivas")
    st.bar_chart(df.set_index('Nombre crédito')['Tasa anual efectiva']*100, 
                 x_label="Créditos", y_label="Tasa efectiva anual")

    #---------------------------------------------- Impresión de pdf
    # Parámetros
    # Título y parámetros
    titulo = "Tabla comparativa tasas"
    param1 = "Se debe tomar mucho en cuenta la comparativa para el caso tasa efectiva anual."
    param2 = "Como segunda observación la comparación para la tasa nominal anual."
    param3 = "Como último tip, observar al mes qué tasa mensual es más baja directamente."
    parametros = {
        "Información 1": param1,
        "Información 2": param2,
        "Información 3": param3
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
        file_name="tabla_comparativa_tasas.pdf",
        mime="application/pdf"
    )



    if st.button("Limpiar todos los créditos"):
        st.session_state.creditos = []
        # st.session_state.tab_print = None
        st.rerun()
else:
    st.info("Agrega al menos un crédito para comenzar.")

