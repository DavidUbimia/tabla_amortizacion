"""
Formatting configuration for currency and number display.
"""

from dataclasses import dataclass
from typing import Dict

from config.settings import (
    DEFAULT_CURRENCY_SYMBOL,
    DEFAULT_DECIMAL_PLACES_MONEY,
    DEFAULT_DECIMAL_PLACES_PERCENT,
)


@dataclass
class CurrencyConfig:
    """Configuration for a specific currency."""
    
    symbol: str
    decimal_places: int = 2
    thousands_separator: str = ","
    decimal_separator: str = "."
    symbol_position: str = "prefix"  # "prefix" or "suffix"


@dataclass
class FormattingPreferences:
    """User formatting preferences."""
    
    currency_symbol: str = DEFAULT_CURRENCY_SYMBOL
    decimals_money: int = DEFAULT_DECIMAL_PLACES_MONEY
    decimals_percent: int = DEFAULT_DECIMAL_PLACES_PERCENT
    show_row_zero: bool = True  # For amortization tables


# Predefined currency configurations
CURRENCY_CONFIGS: Dict[str, CurrencyConfig] = {
    "$": CurrencyConfig(symbol="$", decimal_places=2),
    "MXN$": CurrencyConfig(symbol="MXN$", decimal_places=2),
    "USD$": CurrencyConfig(symbol="USD$", decimal_places=2),
    "€": CurrencyConfig(symbol="€", decimal_places=2),
    "£": CurrencyConfig(symbol="£", decimal_places=2),
}


def get_currency_config(symbol: str) -> CurrencyConfig:
    """
    Get currency configuration for a given symbol.
    
    Args:
        symbol: Currency symbol
        
    Returns:
        CurrencyConfig for the symbol, or default if not found
    """
    return CURRENCY_CONFIGS.get(symbol, CURRENCY_CONFIGS["$"])
