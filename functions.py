# functions.py
from __future__ import annotations

import io
from typing import Dict, Optional

import pandas as pd

from reportlab.lib import colors
from reportlab.lib.pagesizes import A4, landscape
from reportlab.lib.styles import getSampleStyleSheet
from reportlab.platypus import SimpleDocTemplate, Table, TableStyle, Paragraph, Spacer


# =========================
#   TABLA DE AMORTIZACIÓN
# =========================

def calcular_pago_mensual(tasa_anual: float, monto: float, num_pagos: int) -> float:
    """
    Calcula el pago mensual de una anualidad nivelada.
    - tasa_anual: % nominal anual (p.ej. 12.0 para 12%)
    - monto: principal del crédito
    - num_pagos: número de pagos (meses)

    Devuelve el pago mensual (float).
    """
    if num_pagos <= 0 or monto < 0:
        return 0.0

    r = (tasa_anual / 100.0) / 12.0
    if abs(r) < 1e-15:
        # Crédito sin interés
        return monto / num_pagos

    # Fórmula de anualidad: P = M * [ r (1+r)^n / ((1+r)^n - 1) ]
    factor = (1.0 + r) ** num_pagos
    pago = monto * (r * factor) / (factor - 1.0)
    return float(pago)


def tabla_amortizacion(pago: float, tasa_anual: float, monto: float, num_pagos: int) -> pd.DataFrame:
    """
    Genera una tabla de amortización clásico (francés).
    Ajusta el último abono/pago para eliminar residuales por redondeo.
    """
    if num_pagos <= 0 or monto < 0 or pago < 0:
        return pd.DataFrame(columns=["Mes", "Pago", "Interés", "Abono a capital", "Saldo restante"])

    r = (tasa_anual / 100.0) / 12.0
    saldo = float(monto)

    filas = [{
        "Mes": 0,
        "Pago": 0.0,
        "Interés": 0.0,
        "Abono a capital": 0.0,
        "Saldo restante": round(max(saldo, 0.0), 2),
    }]

    for mes in range(1, num_pagos + 1):
        interes = saldo * r if r > 0 else 0.0
        abono = pago - interes

        # Si el abono excede el saldo por residuales, corrige el último pago
        if abono > saldo or mes == num_pagos:
            abono = saldo
            pago_efectivo = interes + abono
        else:
            pago_efectivo = pago

        saldo = saldo - abono

        filas.append({
            "Mes": mes,
            "Pago": round(pago_efectivo, 2),
            "Interés": round(interes, 2),
            "Abono a capital": round(abono, 2),
            "Saldo restante": round(max(saldo, 0.0), 2),
        })

        if saldo <= 1e-8:
            # Forzamos a cero para evitar -0.00 por flotantes,
            # y terminamos si ya está liquidado.
            filas[-1]["Saldo restante"] = 0.0
            # Si quedaran meses por delante (no debería con pago correcto),
            # cortamos la tabla.
            break

    return pd.DataFrame(filas)


# ====================
#   TASA DE CRÉDITOS
# ====================

def _pv_anualidad(pago: float, tasa: float, n: int) -> float:
    """
    Valor presente de una anualidad de 'pago' durante n periodos con tasa 'tasa' (mensual).
    Para tasa ~0 usa el límite continuo.
    """
    if n <= 0:
        return 0.0
    if tasa <= 1e-15:
        return pago * n
    factor = (1.0 + tasa) ** n
    return pago * (1.0 - 1.0 / factor) / tasa


def calcular_tasa(num_pagos: int, pago: float, monto: float,
                  precision: float = 1e-10, max_iter: int = 200) -> Optional[float]:
    """
    Calcula la TASA MENSUAL que iguala el valor presente de los pagos al monto.
    Usa BÚSQUEDA POR BISECCIÓN con expansión del intervalo (estable y sin divergencias).

    Retorna:
        tasa_mensual (float) en proporción (p.ej. 0.015 = 1.5% mensual),
        o None si no se puede determinar.

    Notas:
    - Requiere que pago * num_pagos > monto (si no, la tasa debe ser <= 0).
    - Si pago * num_pagos == monto, la tasa es 0 exacta.
    """
    if monto <= 0 or pago <= 0 or num_pagos <= 0:
        return None

    total_sin_interes = pago * num_pagos
    if abs(total_sin_interes - monto) < 1e-12:
        return 0.0
    if total_sin_interes < monto:
        # Con pagos insuficientes, no existe tasa mensual positiva que cierre
        return None

    # Buscamos r >= 0 tal que PV(r) = monto.
    # PV es monótona decreciente en r. Bisección en [lo, hi].
    lo, hi = 0.0, 0.01  # empezamos con 1% mensual
    pv_lo = _pv_anualidad(pago, lo, num_pagos)  # = total_sin_interes
    pv_hi = _pv_anualidad(pago, hi, num_pagos)

    # Expandir hi hasta que PV(hi) <= monto (bracketing)
    # Límite superior razonable: 1000% mensual (hi=10)
    while pv_hi > monto and hi < 10.0:
        hi *= 2.0
        pv_hi = _pv_anualidad(pago, hi, num_pagos)

    # Si ni con hi enorme logramos PV <= monto, algo es inconsistente
    if pv_hi > monto:
        return None

    # Bisección
    for _ in range(max_iter):
        mid = 0.5 * (lo + hi)
        pv_mid = _pv_anualidad(pago, mid, num_pagos)

        # Criterio de convergencia por diferencia relativa/absoluta
        if abs(pv_mid - monto) <= max(precision * max(monto, 1.0), 1e-12):
            return mid

        if pv_mid > monto:
            # Necesitamos una tasa mayor (reducir PV)
            lo = mid
        else:
            # PV demasiado bajo → tasa menor
            hi = mid

        if abs(hi - lo) < precision:
            return 0.5 * (lo + hi)

    # Si llegó aquí, devolver mejor aproximación
    return 0.5 * (lo + hi)


# ====================
#   PDF UTILITARIOS
# ====================

def generar_pdf_tabla(df: pd.DataFrame, titulo: str, parametros: Dict[str, str]) -> bytes:
    """
    Genera un PDF en formato horizontal A4 con:
      - Título
      - Lista de parámetros (key: value)
      - Tabla con cabecera repetida

    Devuelve los BYTES del PDF (listos para Streamlit download_button).
    """
    buffer = io.BytesIO()
    doc = SimpleDocTemplate(buffer, pagesize=landscape(A4),
                            leftMargin=24, rightMargin=24, topMargin=24, bottomMargin=24)

    estilos = getSampleStyleSheet()
    elementos = []

    # Título
    elementos.append(Paragraph(f"<b>{titulo}</b>", estilos["Title"]))
    elementos.append(Spacer(1, 10))

    # Parámetros
    if parametros:
        for clave, valor in parametros.items():
            elementos.append(Paragraph(f"<b>{clave}:</b> {valor}", estilos["Normal"]))
        elementos.append(Spacer(1, 12))

    # Asegurar conversión a strings para reporte tabular estable
    data = [list(map(str, df.columns.tolist()))] + [list(map(str, row)) for row in df.values.tolist()]

    tabla = Table(data, repeatRows=1, hAlign="LEFT")
    tabla.setStyle(TableStyle([
        ("BACKGROUND", (0, 0), (-1, 0), colors.HexColor("#4F81BD")),
        ("TEXTCOLOR", (0, 0), (-1, 0), colors.white),
        ("FONTNAME", (0, 0), (-1, -1), "Helvetica"),
        ("FONTSIZE", (0, 0), (-1, -1), 9),
        ("ALIGN", (0, 0), (-1, -1), "RIGHT"),
        ("ALIGN", (0, 0), (0, -1), "CENTER"),  # Columna 0 (p.ej. Mes)
        ("GRID", (0, 0), (-1, -1), 0.25, colors.grey),
        ("BOTTOMPADDING", (0, 0), (-1, 0), 6),
        ("TOPPADDING", (0, 0), (-1, 0), 6),
    ]))

    elementos.append(tabla)
    doc.build(elementos)

    buffer.seek(0)
    return buffer.getvalue()

# ---------------------------
#   Helper: estilo (Styler)
# ---------------------------
def style_amort(df, symbol, decimals):
    """Devuelve un pandas Styler con formato de moneda; sin type hints de pandas internos."""
    def fmt_money(x, s=symbol, d=decimals):
        try:
            return f"{s}{x:,.{d}f}"
        except Exception:
            return x
    return df.style.format({
        "Mes": "{:,.0f}",
        "Pago": fmt_money,
        "Interés": fmt_money,
        "Abono a capital": fmt_money,
        "Saldo restante": fmt_money
    })