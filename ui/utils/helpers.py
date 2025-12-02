"""
General utility functions and helpers.
Provides common functionality used across the application.
"""

from datetime import datetime
from typing import Any, Dict, List, Union
from decimal import Decimal
import pandas as pd


def generate_filename(
    report_type: str,
    extension: str,
    include_timestamp: bool = True
) -> str:
    """
    Generate a descriptive filename for exports.
    
    Args:
        report_type: Type of report (e.g., "amortization", "sensitivity")
        extension: File extension without dot (e.g., "csv", "pdf")
        include_timestamp: Whether to include timestamp in filename
        
    Returns:
        Formatted filename string
        
    Examples:
        >>> generate_filename("amortization", "csv")
        'amortization_2024-12-01_143022.csv'
        >>> generate_filename("sensitivity", "pdf", False)
        'sensitivity.pdf'
    """
    if include_timestamp:
        timestamp = datetime.now().strftime("%Y-%m-%d_%H%M%S")
        return f"{report_type}_{timestamp}.{extension}"
    else:
        return f"{report_type}.{extension}"


def format_datetime(
    dt: datetime,
    format_string: str = "%Y-%m-%d %H:%M:%S"
) -> str:
    """
    Format a datetime object to string.
    
    Args:
        dt: Datetime object to format
        format_string: Format string (default: ISO-like format)
        
    Returns:
        Formatted datetime string
        
    Examples:
        >>> dt = datetime(2024, 12, 1, 14, 30, 22)
        >>> format_datetime(dt)
        '2024-12-01 14:30:22'
        >>> format_datetime(dt, "%d/%m/%Y")
        '01/12/2024'
    """
    return dt.strftime(format_string)


def format_date(
    dt: datetime,
    format_string: str = "%Y-%m-%d"
) -> str:
    """
    Format a datetime object to date string.
    
    Args:
        dt: Datetime object to format
        format_string: Format string (default: ISO date format)
        
    Returns:
        Formatted date string
        
    Examples:
        >>> dt = datetime(2024, 12, 1, 14, 30, 22)
        >>> format_date(dt)
        '2024-12-01'
    """
    return dt.strftime(format_string)


def safe_decimal_conversion(value: Any) -> Decimal:
    """
    Safely convert a value to Decimal.
    
    Args:
        value: Value to convert (int, float, str, or Decimal)
        
    Returns:
        Decimal representation of the value
        
    Raises:
        ValueError: If value cannot be converted to Decimal
        
    Examples:
        >>> safe_decimal_conversion(100)
        Decimal('100')
        >>> safe_decimal_conversion("123.45")
        Decimal('123.45')
        >>> safe_decimal_conversion(12.5)
        Decimal('12.5')
    """
    if isinstance(value, Decimal):
        return value
    
    try:
        # Convert to string first to avoid float precision issues
        return Decimal(str(value))
    except Exception as e:
        raise ValueError(f"Cannot convert {value} to Decimal: {e}")


def dataframe_to_dict_list(df: pd.DataFrame) -> List[Dict[str, Any]]:
    """
    Convert a DataFrame to a list of dictionaries.
    
    Args:
        df: DataFrame to convert
        
    Returns:
        List of dictionaries, one per row
        
    Examples:
        >>> df = pd.DataFrame({'A': [1, 2], 'B': [3, 4]})
        >>> dataframe_to_dict_list(df)
        [{'A': 1, 'B': 3}, {'A': 2, 'B': 4}]
    """
    return df.to_dict('records')


def dict_list_to_dataframe(data: List[Dict[str, Any]]) -> pd.DataFrame:
    """
    Convert a list of dictionaries to a DataFrame.
    
    Args:
        data: List of dictionaries
        
    Returns:
        DataFrame with columns from dictionary keys
        
    Examples:
        >>> data = [{'A': 1, 'B': 3}, {'A': 2, 'B': 4}]
        >>> dict_list_to_dataframe(data)
           A  B
        0  1  3
        1  2  4
    """
    return pd.DataFrame(data)


def clamp(value: Union[int, float, Decimal], min_val: Union[int, float, Decimal], 
          max_val: Union[int, float, Decimal]) -> Union[int, float, Decimal]:
    """
    Clamp a value between minimum and maximum bounds.
    
    Args:
        value: Value to clamp
        min_val: Minimum allowed value
        max_val: Maximum allowed value
        
    Returns:
        Clamped value
        
    Examples:
        >>> clamp(5, 0, 10)
        5
        >>> clamp(-5, 0, 10)
        0
        >>> clamp(15, 0, 10)
        10
    """
    return max(min_val, min(value, max_val))


def percentage_to_decimal(percentage: Union[float, Decimal]) -> Decimal:
    """
    Convert a percentage value to decimal representation.
    
    Args:
        percentage: Percentage value (e.g., 12.5 for 12.5%)
        
    Returns:
        Decimal representation (e.g., 0.125)
        
    Examples:
        >>> percentage_to_decimal(12.5)
        Decimal('0.125')
        >>> percentage_to_decimal(100)
        Decimal('1.0')
    """
    if not isinstance(percentage, Decimal):
        percentage = Decimal(str(percentage))
    return percentage / Decimal('100')


def decimal_to_percentage(decimal: Union[float, Decimal]) -> Decimal:
    """
    Convert a decimal value to percentage representation.
    
    Args:
        decimal: Decimal value (e.g., 0.125)
        
    Returns:
        Percentage representation (e.g., 12.5)
        
    Examples:
        >>> decimal_to_percentage(0.125)
        Decimal('12.5')
        >>> decimal_to_percentage(1.0)
        Decimal('100')
    """
    if not isinstance(decimal, Decimal):
        decimal = Decimal(str(decimal))
    return decimal * Decimal('100')


def truncate_dataframe(df: pd.DataFrame, max_rows: int = 100) -> pd.DataFrame:
    """
    Truncate a DataFrame to a maximum number of rows.
    
    Args:
        df: DataFrame to truncate
        max_rows: Maximum number of rows to keep
        
    Returns:
        Truncated DataFrame
        
    Examples:
        >>> df = pd.DataFrame({'A': range(200)})
        >>> truncated = truncate_dataframe(df, 100)
        >>> len(truncated)
        100
    """
    if len(df) > max_rows:
        return df.head(max_rows)
    return df


def merge_dicts(*dicts: Dict[str, Any]) -> Dict[str, Any]:
    """
    Merge multiple dictionaries into one.
    Later dictionaries override earlier ones for duplicate keys.
    
    Args:
        *dicts: Variable number of dictionaries to merge
        
    Returns:
        Merged dictionary
        
    Examples:
        >>> merge_dicts({'a': 1}, {'b': 2}, {'a': 3})
        {'a': 3, 'b': 2}
    """
    result = {}
    for d in dicts:
        result.update(d)
    return result


def is_numeric(value: Any) -> bool:
    """
    Check if a value is numeric (int, float, or Decimal).
    
    Args:
        value: Value to check
        
    Returns:
        True if numeric, False otherwise
        
    Examples:
        >>> is_numeric(123)
        True
        >>> is_numeric("123")
        False
        >>> is_numeric(Decimal("123.45"))
        True
    """
    return isinstance(value, (int, float, Decimal))


def round_to_cents(value: Union[float, Decimal]) -> Decimal:
    """
    Round a monetary value to cents (2 decimal places).
    
    Args:
        value: Monetary value to round
        
    Returns:
        Rounded Decimal value
        
    Examples:
        >>> round_to_cents(123.456)
        Decimal('123.46')
        >>> round_to_cents(Decimal("99.994"))
        Decimal('99.99')
    """
    if not isinstance(value, Decimal):
        value = Decimal(str(value))
    return value.quantize(Decimal('0.01'))
