import streamlit as st
import pandas as pd
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io


# TABLA DE AMORTIZACIÓN

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


# TASA DE CRÉDITOS

def calcular_tasa(num_pagos, pago, monto, precision=1e-6, max_iter=1000):
    if monto <= 0 or pago <= 0 or num_pagos <= 0:
        return None
    
    def f(tasa):
        if tasa == 0:
            vpn = monto - pago * num_pagos
            derivada = -pago * num_pagos * (num_pagos + 1) / 2
        else:
            factor = (1 + tasa)**num_pagos
            vpn = monto - (pago / tasa) * (1 - 1/factor)
            derivada = (pago / tasa**2) * (1 - 1/factor) - (pago * num_pagos) / (tasa * (1 + tasa)**(num_pagos + 1))
        return vpn, derivada

    tasa = 0.1
    for _ in range(max_iter):
        vpn, derivada = f(tasa)
        nueva_tasa = tasa - vpn / derivada
        if nueva_tasa <= -1:
            nueva_tasa = -0.9
        if abs(nueva_tasa - tasa) < precision:
            return nueva_tasa
        tasa = nueva_tasa
    return tasa


# Impresión pdf









