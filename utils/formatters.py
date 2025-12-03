"""
Formatting utilities for currency, numbers, and percentages.
Provides consistent formatting across the application.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union
import pandas as pd

from config.formatting import CurrencyConfig, get_currency_config


def format_currency(
    value: Union[Decimal, float, int],
    symbol: str = "$",
    precision: int = 2
) -> str:
    """
    Format a monetary value with currency symbol and consistent rounding.
    
    Args:
        value: The monetary value to format
        symbol: Currency symbol to use
        precision: Number of decimal places
        
    Returns:
        Formatted currency string (e.g., "$1,234.56")
        
    Examples:
        >>> format_currency(Decimal("1234.567"), "$", 2)
        '$1,234.57'
        >>> format_currency(1000, "€", 2)
        '€1,000.00'
    """
    # Convert to Decimal for consistent rounding
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    
    # Round to specified precision using ROUND_HALF_UP (banker's rounding alternative)
    quantizer = Decimal(10) ** -precision
    rounded_value = value.quantize(quantizer, rounding=ROUND_HALF_UP)
    
    # Get currency config
    config = get_currency_config(symbol)
    
    # Format with thousands separator
    formatted = f"{rounded_value:,.{precision}f}"
    
    # Apply currency symbol based on position
    if config.symbol_position == "prefix":
        return f"{config.symbol}{formatted}"
    else:
        return f"{formatted}{config.symbol}"


def format_percentage(
    value: Union[Decimal, float],
    precision: int = 2,
    include_symbol: bool = True
) -> str:
    """
    Format a percentage value with consistent rounding.
    
    Args:
        value: The percentage value (as decimal, e.g., 0.12 for 12%)
        precision: Number of decimal places
        include_symbol: Whether to include the % symbol
        
    Returns:
        Formatted percentage string (e.g., "12.00%")
        
    Examples:
        >>> format_percentage(Decimal("0.1234"), 2)
        '12.34%'
        >>> format_percentage(0.05, 1, False)
        '5.0'
    """
    # Convert to Decimal for consistent rounding
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    
    # Convert to percentage
    percentage = value * 100
    
    # Round to specified precision
    quantizer = Decimal(10) ** -precision
    rounded_percentage = percentage.quantize(quantizer, rounding=ROUND_HALF_UP)
    
    # Format
    formatted = f"{rounded_percentage:.{precision}f}"
    
    if include_symbol:
        return f"{formatted}%"
    return formatted


def format_number(
    value: Union[Decimal, float, int],
    precision: int = 2,
    use_thousands_separator: bool = True
) -> str:
    """
    Format a numeric value with consistent rounding.
    
    Args:
        value: The numeric value to format
        precision: Number of decimal places
        use_thousands_separator: Whether to use thousands separator
        
    Returns:
        Formatted number string
        
    Examples:
        >>> format_number(Decimal("1234.567"), 2)
        '1,234.57'
        >>> format_number(1000, 0, False)
        '1000'
    """
    # Convert to Decimal for consistent rounding
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    
    # Round to specified precision
    quantizer = Decimal(10) ** -precision
    rounded_value = value.quantize(quantizer, rounding=ROUND_HALF_UP)
    
    # Format
    if use_thousands_separator:
        return f"{rounded_value:,.{precision}f}"
    else:
        return f"{rounded_value:.{precision}f}"


def style_amort(
    df: pd.DataFrame,
    symbol: str = "$",
    decimals: int = 2
):
    """
    Apply formatting styles to an amortization table DataFrame.
    
    This function is used for pandas Styler formatting to display
    amortization tables with proper currency and number formatting.
    
    Args:
        df: Amortization table DataFrame with columns:
            - Mes (month number)
            - Pago (payment amount)
            - Interés (interest amount)
            - Abono a capital (principal payment)
            - Saldo restante (remaining balance)
        symbol: Currency symbol to use
        decimals: Number of decimal places for monetary values
        
    Returns:
        Styled DataFrame ready for display
        
    Examples:
        >>> df = pd.DataFrame({
        ...     'Mes': [0, 1],
        ...     'Pago': [0.0, 856.07],
        ...     'Interés': [0.0, 100.0],
        ...     'Abono a capital': [0.0, 756.07],
        ...     'Saldo restante': [10000.0, 9243.93]
        ... })
        >>> styled = style_amort(df, "$", 2)
    """
    def fmt_money(x, s=symbol, d=decimals):
        """Format a single monetary value."""
        try:
            return f"{s}{x:,.{d}f}"
        except Exception:
            return x
    
    # Apply formatting to each column
    return df.style.format({
        "Mes": "{:,.0f}",
        "Pago": fmt_money,
        "Interés": fmt_money,
        "Abono a capital": fmt_money,
        "Saldo restante": fmt_money
    })
