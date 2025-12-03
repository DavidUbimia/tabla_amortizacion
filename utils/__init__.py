"""
Utility modules for the loan calculator application.
"""

from utils.formatters import (
    format_currency,
    format_percentage,
    format_number,
    style_amort,
)

from utils.session_state import (
    SessionStateManager,
    init_session_state,
    get_state,
    set_state,
    has_state,
)

from utils.helpers import (
    generate_filename,
    format_datetime,
    format_date,
    safe_decimal_conversion,
    dataframe_to_dict_list,
    dict_list_to_dataframe,
    clamp,
    percentage_to_decimal,
    decimal_to_percentage,
    truncate_dataframe,
    merge_dicts,
    is_numeric,
    round_to_cents,
)

__all__ = [
    # Formatters
    "format_currency",
    "format_percentage",
    "format_number",
    "style_amort",
    # Session state
    "SessionStateManager",
    "init_session_state",
    "get_state",
    "set_state",
    "has_state",
    # Helpers
    "generate_filename",
    "format_datetime",
    "format_date",
    "safe_decimal_conversion",
    "dataframe_to_dict_list",
    "dict_list_to_dataframe",
    "clamp",
    "percentage_to_decimal",
    "decimal_to_percentage",
    "truncate_dataframe",
    "merge_dicts",
    "is_numeric",
    "round_to_cents",
]
