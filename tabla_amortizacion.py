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

    tabla = []

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



st.set_page_config(page_title="Calculadora de Crédito", layout="centered")
st.title("💰 Tabla de amortización")

st.markdown("#### Introduce los datos del crédito:")

# Formulario
with st.form("form_credito"):
    tasa_input = st.number_input("Tasa de interés anual (%)", min_value=0.0, step=0.1, value=10.0, format="%.2f")
    monto_input = st.number_input("Monto del crédito ($)", min_value=0.0, step=100.0, value=10000.0, format="%.2f")
    pagos_input = st.number_input("Número de pagos (meses)", min_value=1, step=12, value=12)

    submitted = st.form_submit_button("Calcular")

# Resultado
if submitted:
    pago = calcular_pago_mensual(tasa_input, monto_input, pagos_input)
    tabla = tabla_amortizacion(pago, tasa_input, monto_input, pagos_input)

    st.markdown("---")
    st.subheader("📊 Resultado del Cálculo")
    st.write(f"**Tasa anual:** {tasa_input:.2f}%")
    st.write(f"**Monto del crédito:** ${monto_input:,.2f}")
    st.write(f"**Número de pagos:** {pagos_input} meses")
    st.success(f"💸 El pago mensual estimado es: **${pago:,.2f}**")

    st.write("")
    st.markdown("---")
    st.markdown("### 🧾 Tabla de amortización")
    st.dataframe(tabla, use_container_width=True,hide_index=True)



