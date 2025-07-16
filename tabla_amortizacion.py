import streamlit as st
import pandas as pd
import streamlit as st

def calcular_pago_mensual(tasa_anual, monto, num_pagos):
    tasa_mensual = tasa_anual / 100 / 12
    if tasa_mensual == 0:
        return monto / num_pagos
    else:
        return monto * (tasa_mensual * (1 + tasa_mensual) ** num_pagos) / ((1 + tasa_mensual) ** num_pagos - 1)
    

def tabla_amortizacion(pago, tasa, monto, pagos):
    tasa_mensual = tasa / 100 / 12
    saldo = monto

    tabla = [{
            "Mes": 0,
            "Pago": 0,
            "Interés": 0,
            "Abono a capital": 0,
            "Saldo restante": round(max(saldo, 0), 2)
        }]

    for mes in range(1, pagos + 1):
        interes = saldo * tasa_mensual
        abono = pago - interes
        saldo = saldo - abono

        tabla.append({
            "Mes": mes,
            "Pago": round(pago, 2),
            "Interés": round(interes, 2),
            "Abono a capital": round(abono, 2),
            "Saldo restante": round(max(saldo, 0), 2)
        })

    return pd.DataFrame(tabla)





# Inicializaciones
st.session_state.tabla=None


st.title("💰 Tabla de amortización")

st.markdown("#### Introduce los datos del crédito:")

# Formulario
with st.form("form_credito"):
    tasa_input = st.number_input("Tasa de interés anual (% Nominal)", min_value=0.0, step=0.1, value=10.0, format="%.2f")
    monto_input = st.number_input("Monto del crédito ($)", min_value=0.0, step=100.0, value=10000.0, format="%.2f")
    pagos_input = st.number_input("Número de pagos (meses)", min_value=1, step=12, value=12)

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


    st.dataframe(df_display, use_container_width=True,hide_index=True)

    st.write("")
    st.markdown("---")
    st.markdown("### $ Totales")
    tabla = st.session_state.tabla.copy()
    df_totales=pd.DataFrame({
        'Total monto a pagar': [tabla['Pago'].sum()],
        'Total interés a pagar': [tabla['Interés'].sum()]
    })

    df_totales['Total monto a pagar'] = df_totales['Total monto a pagar'].map("${:,.2f}".format)
    df_totales['Total interés a pagar'] = df_totales['Total interés a pagar'].map("${:,.2f}".format)

    st.dataframe(df_totales, use_container_width=True,hide_index=True)


