"""
Configuration module for loan calculator application.
Contains app-wide constants and default values.
"""

from decimal import Decimal
from typing import Dict, List

# ============================================================================
# Application Metadata
# ============================================================================
APP_NAME = "Créditos | Amortización y Tasas"
APP_ICON = "💳"
APP_VERSION = "2.0.0"

# ============================================================================
# Calculation Defaults
# ============================================================================
DEFAULT_PRINCIPAL = Decimal("10000.00")
DEFAULT_ANNUAL_RATE = Decimal("12.0")  # percentage
DEFAULT_NUM_PAYMENTS = 12
DEFAULT_PRECISION = Decimal("1e-10")
MAX_ITERATIONS = 200

# ============================================================================
# Validation Limits
# ============================================================================
MIN_PRINCIPAL = Decimal("0.01")
MAX_PRINCIPAL = Decimal("100000000.00")  # 100 million
MIN_ANNUAL_RATE = Decimal("0.0")
MAX_ANNUAL_RATE = Decimal("200.0")  # percentage
MIN_NUM_PAYMENTS = 1
MAX_NUM_PAYMENTS = 600  # 50 years

# ============================================================================
# Numerical Stability
# ============================================================================
EPSILON_RATE = Decimal("1e-15")  # For zero rate detection
EPSILON_BALANCE = Decimal("0.01")  # For zero balance detection (monetary)
EPSILON_CONVERGENCE = Decimal("1e-10")  # For rate solver convergence

# ============================================================================
# Display Formatting Defaults
# ============================================================================
DEFAULT_CURRENCY_SYMBOL = "$"
DEFAULT_DECIMAL_PLACES_MONEY = 2
DEFAULT_DECIMAL_PLACES_PERCENT = 2

SUPPORTED_CURRENCIES: List[str] = ["$", "MXN$", "USD$", "€", "£"]

# ============================================================================
# Export Settings
# ============================================================================
EXPORT_FORMATS: List[str] = ["csv", "excel", "pdf"]
CSV_ENCODING = "utf-8-sig"  # UTF-8 with BOM for Excel compatibility
EXCEL_ENGINE = "xlsxwriter"

# ============================================================================
# Performance Settings
# ============================================================================
CACHE_TTL = 3600  # seconds (1 hour)
MAX_TABLE_ROWS_DISPLAY = 100  # For pagination threshold

# ============================================================================
# UI Settings
# ============================================================================
LAYOUT = "wide"
SIDEBAR_STATE = "expanded"

# Theme colors (matching .streamlit/config.toml)
PRIMARY_COLOR = "#4F81BD"
BACKGROUND_COLOR = "#FFFFFF"
SECONDARY_BACKGROUND_COLOR = "#F0F2F6"
TEXT_COLOR = "#000000"

# ============================================================================
# Session State Keys
# ============================================================================
SESSION_KEYS = {
    "tabla": "tabla",
    "pago": "pago",
    "inputs": "inputs",
    "cfg": "cfg",
    "creditos": "creditos",
    "escenarios_guardados": "escenarios_guardados",
    "sim_base": "sim_base",
    "sens_base": "sens_base",
}
