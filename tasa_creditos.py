import streamlit as st
import pandas as pd

def calcular_tasa(num_pagos, pago, monto, precision=1e-6, max_iter=1000):
    """
    Calcula la tasa de interés periódica usando el método de Newton-Raphson
    
    Args:
        num_pagos (int): Número total de pagos
        pago (float): Valor de cada pago
        monto (float): Monto total del crédito (valor actual)
        precision (float): Precisión deseada para el cálculo
        max_iter (int): Máximo número de iteraciones
        
    Returns:
        float: Tasa de interés periódica (por periodo)
    """
    if monto <= 0 or pago <= 0 or num_pagos <= 0:
        return None
    
    # Función para calcular el valor presente neto (VPN) y su derivada
    def f(tasa):
        if tasa == 0:
            vpn = monto - pago * num_pagos
            derivada = -pago * num_pagos * (num_pagos + 1) / 2
        else:
            factor = (1 + tasa)**num_pagos
            vpn = monto - (pago / tasa) * (1 - 1/factor)
            derivada = (pago / tasa**2) * (1 - 1/factor) - (pago * num_pagos) / (tasa * (1 + tasa)**(num_pagos + 1))
        return vpn, derivada
    
    # Método de Newton-Raphson
    tasa = 0.1  # Valor inicial (10%)
    for _ in range(max_iter):
        vpn, derivada = f(tasa)
        nueva_tasa = tasa - vpn / derivada
        
        # Evitar tasas negativas
        if nueva_tasa <= -1:
            nueva_tasa = -0.9
            
        # Criterio de convergencia
        if abs(nueva_tasa - tasa) < precision:
            return nueva_tasa
        
        tasa = nueva_tasa
    
    return tasa  # Retorna el mejor valor encontrado


st.markdown("# :blue[Comparador de Tasas de Crédito]")
st.markdown("""
Ingresa los detalles de tus créditos para calcular y comparar las tasas de interés.
La tasa se calcula usando un método numérico propio (Newton-Raphson).
""")

# Inicializar lista de créditos en session_state si no existe
if 'creditos' not in st.session_state:
    st.session_state.creditos = []

# Formulario para agregar créditos
with st.expander("**Créditos**", expanded=len(st.session_state.creditos)==0):
    with st.form("credito_form"):
        col1, col2, col3, col4 = st.columns(4)

        with col1:
            nom_credito = st.text_input("**Nombre del crédito**",placeholder="Crédito 1")
        with col3:
            num_pagos = st.number_input("**Número de pagos**", min_value=0, step=1, value=0)
        with col4:
            pago = st.number_input("**Pago**", min_value=0, value=0)
        with col2:
            monto = st.number_input("**Monto del crédito**", min_value=0, value=0)
        
        submitted = st.form_submit_button("**Agregar Crédito**")
        
        if submitted:

            # Validar datos
            if nom_credito=='':
                st.error("Indica el nombre del crédito a agregar!", icon="🚨")
            elif monto==0:
                st.error("El monto del crédito no puede ser cero!", icon="🚨")
            elif num_pagos==0:
                st.error("El número de pagos no puede ser cero!", icon="🚨")
            elif pago==0:
                st.error("El pago ó abono no puede ser cero!", icon="🚨")
            elif pago * num_pagos <= monto:
                str_warning = f"[Explicación]: Si se multiplica el pago igual a {pago} por el número de pagos {num_pagos}\
                    , el resultado es {pago * num_pagos}, el cual es menor al monto solicitado {monto}. Por ello hay un error."
                st.error("El valor total de pagos debe ser mayor que el monto del crédito!", icon="🚨")
                st.warning(str_warning)
            else:
                # Calcular tasa
                tasa = round(calcular_tasa(num_pagos, pago, monto),ndigits=2)
                
                if tasa is not None and tasa >= 0:
                    # Agregar a la lista de créditos
                    nuevo_credito = {
                        'Nombre crédito': nom_credito,
                        'Número de pagos': num_pagos,
                        'Pago': pago,
                        'Monto del crédito': monto,
                        'Tasa mensual': tasa,
                        'Tasa anual nominal': tasa * 12, # como se maneja mensual el pago el número 12 es fijo
                        'Tasa anual efectiva': (1 + tasa)**12 - 1
                    }
                    st.session_state.creditos.append(nuevo_credito)
                    st.success("Crédito agregado correctamente!")
                else:
                    st.error("No se pudo calcular una tasa válida. Verifica los datos.")

# Mostrar tabla de créditos
if len(st.session_state.creditos) > 0:
    st.subheader("Resumen de Créditos")
    
    # Convertir a DataFrame para mejor visualización
    df = pd.DataFrame(st.session_state.creditos)
    
    # Formatear columnas
    df_display = df.copy()
    df_display['Pago'] = df_display['Pago'].map("${:,.2f}".format)
    df_display['Monto del crédito'] = df_display['Monto del crédito'].map("${:,.2f}".format)
    df_display['Tasa mensual'] = df_display['Tasa mensual'].apply(lambda x: f"{x:.2%}")
    df_display['Tasa anual nominal'] = df_display['Tasa anual nominal'].apply(lambda x: f"{x:.2%}")
    df_display['Tasa anual efectiva'] = df_display['Tasa anual efectiva'].apply(lambda x: f"{x:.2%}")
    
    st.dataframe(df_display[['Nombre crédito','Número de pagos', 'Pago', 'Monto del crédito', 
                            'Tasa mensual', 'Tasa anual nominal', 'Tasa anual efectiva']], 
                hide_index=True)
    
    # Gráfico comparativo
    st.subheader("Comparación de Tasas Anuales Efectivas")
    st.bar_chart(df.set_index('Nombre crédito')['Tasa anual efectiva']*100,x_label="Créditos", y_label="Tasa efectiva anual")
    
    # Botón para limpiar todos los créditos
    if st.button("Limpiar todos los créditos"):
        st.session_state.creditos = []
        st.rerun()
else:
    st.info("Agrega al menos un crédito para comenzar.")
