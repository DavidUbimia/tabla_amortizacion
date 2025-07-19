import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from matplotlib.backends.backend_pdf import PdfPages
import io
from reportlab.lib.pagesizes import A4
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.lib import colors
import io

from reportlab.lib.pagesizes import A4, landscape



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

# def generar_pdf(df, titulo, parametros):
#     buffer = io.BytesIO()
#     with PdfPages(buffer) as pdf:
#         fig, ax = plt.subplots(figsize=(8.27, 11.69))  # Tamaño A4
#         ax.axis('off')

#         # Construir texto
#         text = f"{titulo}\n\n"
#         for clave, valor in parametros.items():
#             text += f"{clave}: {valor}\n"
#         text += "\n"

#         # Agrega la tabla como texto
#         tabla_texto = df.to_string(index=False)
#         ax.text(0, 1, text + tabla_texto, ha='left', va='top', fontsize=9, family='monospace', wrap=True)

#         pdf.savefig(fig, bbox_inches='tight')
#         plt.close()

#     buffer.seek(0)
#     return buffer



def generar_pdf_tabla(df, titulo, parametros):
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4))
    elementos = []
    estilos = getSampleStyleSheet()

    # Título
    elementos.append(Paragraph(f"<b>{titulo}</b>", estilos["Title"]))
    elementos.append(Spacer(1, 12))

    # Parámetros
    for clave, valor in parametros.items():
        elementos.append(Paragraph(f"<b>{clave}:</b> {valor}", estilos["Normal"]))
    elementos.append(Spacer(1, 12))

    # Convertimos el DataFrame a lista de listas
    data = [df.columns.tolist()] + df.values.tolist()

    # Crear tabla y aplicar estilos
    tabla = Table(data, repeatRows=1, hAlign='LEFT')
    tabla.setStyle(TableStyle([
        ('BACKGROUND', (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ('TEXTCOLOR', (0, 0), (-1, 0), colors.white),
        ('FONTNAME', (0, 0), (-1, -1), 'Helvetica'),
        ('FONTSIZE', (0, 0), (-1, -1), 9),
        ('ALIGN', (0, 0), (-1, -1), 'RIGHT'),
        ('ALIGN', (0, 0), (0, -1), 'CENTER'),  # Columna de Mes
        ('GRID', (0, 0), (-1, -1), 0.25, colors.grey),
        ('BOTTOMPADDING', (0, 0), (-1, 0), 6),
        ('TOPPADDING', (0, 0), (-1, 0), 6),
    ]))

    elementos.append(tabla)
    doc.build(elementos)
    buffer.seek(0)
    return buffer



