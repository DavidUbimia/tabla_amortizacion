"""
Table display components for loan data.

This module provides reusable table components for displaying
amortization schedules, scenario comparisons, and analysis results
with consistent formatting and styling.
"""

from typing import Optional, List
from decimal import Decimal
import pandas as pd
import streamlit as st

from utils.formatters import format_currency, format_percentage, style_amort


def display_amortization_table(
    schedule: pd.DataFrame,
    currency_symbol: str = "$",
    decimals: int = 2,
    show_row_zero: bool = True,
    title: str = "Tabla de amortización",
    use_container_width: bool = True
) -> None:
    """
    Display formatted amortization table.
    
    Shows the complete payment schedule with proper currency formatting
    and optional row zero (initial balance) display.
    
    Args:
        schedule: Amortization schedule DataFrame with columns:
                 Mes, Pago, Interés, Abono a capital, Saldo restante
        currency_symbol: Currency symbol for formatting
        decimals: Number of decimal places for monetary values
        show_row_zero: Whether to show row 0 (initial balance)
        title: Table title/header
        use_container_width: Whether table should use full container width
        
    Example:
        >>> display_amortization_table(loan.schedule, "$", 2)
    """
    st.subheader(title)
    
    # Option to show/hide row 0
    if not show_row_zero:
        schedule = schedule[schedule["Mes"] != 0].reset_index(drop=True)
    
    # Apply styling and display
    st.dataframe(
        style_amort(schedule, currency_symbol, decimals),
        use_container_width=use_container_width,
        hide_index=True
    )


def display_scenario_comparison(
    comparison_df: pd.DataFrame,
    currency_symbol: str = "$",
    decimals_money: int = 2,
    decimals_percent: int = 2,
    highlight_best: Optional[str] = None,
    title: str = "Comparación de escenarios"
) -> None:
    """
    Display scenario comparison table with formatting.
    
    Shows multiple loan scenarios side-by-side with all key metrics,
    optionally highlighting the best scenario based on a criterion.
    
    Args:
        comparison_df: DataFrame with scenario comparison data
        currency_symbol: Currency symbol for formatting
        decimals_money: Decimal places for monetary values
        decimals_percent: Decimal places for percentages
        highlight_best: Column name to use for highlighting best value (optional)
        title: Table title
        
    Example:
        >>> display_scenario_comparison(
        ...     comparison.to_dataframe(),
        ...     highlight_best='total_interest'
        ... )
    """
    st.subheader(title)
    
    # Create a copy for formatting
    display_df = comparison_df.copy()
    
    # Format columns based on their type
    format_dict = {}
    
    for col in display_df.columns:
        if col in ['principal', 'monthly_payment', 'total_paid', 'total_interest']:
            # Format as currency
            display_df[col] = display_df[col].apply(
                lambda x: format_currency(x, currency_symbol, decimals_money)
            )
        elif col in ['annual_rate', 'monthly_rate', 'effective_annual_rate']:
            # Format as percentage
            display_df[col] = display_df[col].apply(
                lambda x: format_percentage(x, decimals_percent)
            )
        elif col == 'num_payments':
            # Format as integer
            display_df[col] = display_df[col].astype(int)
    
    # Highlight best row if specified
    if highlight_best and 'is_best' in display_df.columns:
        # Use styling to highlight
        def highlight_row(row):
            if row.get('is_best', False):
                return ['background-color: #d4edda'] * len(row)
            return [''] * len(row)
        
        styled_df = display_df.style.apply(highlight_row, axis=1)
        st.dataframe(styled_df, use_container_width=True, hide_index=True)
    else:
        st.dataframe(display_df, use_container_width=True, hide_index=True)


def display_sensitivity_results(
    sensitivity_df: pd.DataFrame,
    variable_name: str,
    metric_name: str,
    currency_symbol: str = "$",
    decimals: int = 2,
    title: Optional[str] = None
) -> None:
    """
    Display sensitivity analysis results table.
    
    Shows how a metric changes across a range of input values,
    with proper formatting based on the metric type.
    
    Args:
        sensitivity_df: DataFrame with sensitivity analysis results
        variable_name: Name of the variable being varied
        metric_name: Name of the metric being measured
        currency_symbol: Currency symbol for formatting
        decimals: Decimal places for formatting
        title: Table title (auto-generated if None)
        
    Example:
        >>> display_sensitivity_results(
        ...     sens_df, 'Tasa (%)', 'Pago mensual', '$', 2
        ... )
    """
    if title is None:
        title = f"Análisis de sensibilidad: {metric_name} vs {variable_name}"
    
    st.subheader(title)
    
    # Create formatted copy
    display_df = sensitivity_df.copy()
    
    # Format based on column names/types
    for col in display_df.columns:
        if 'pago' in col.lower() or 'monto' in col.lower() or 'interes' in col.lower():
            # Monetary values
            display_df[col] = display_df[col].apply(
                lambda x: format_currency(x, currency_symbol, decimals)
            )
        elif 'tasa' in col.lower() or '%' in col:
            # Percentage values
            display_df[col] = display_df[col].apply(
                lambda x: format_percentage(Decimal(str(x)) / 100, decimals)
                if isinstance(x, (int, float)) and x > 1 else format_percentage(x, decimals)
            )
    
    st.dataframe(display_df, use_container_width=True, hide_index=True)


def display_summary_table(
    data: dict,
    currency_symbol: str = "$",
    decimals: int = 2,
    title: str = "Resumen"
) -> None:
    """
    Display summary table from dictionary data.
    
    Converts a dictionary of key-value pairs into a formatted
    table for display. Useful for showing totals, summaries, etc.
    
    Args:
        data: Dictionary with label: value pairs
        currency_symbol: Currency symbol for formatting
        decimals: Decimal places for formatting
        title: Table title
        
    Example:
        >>> display_summary_table({
        ...     'Total a pagar': Decimal('120000'),
        ...     'Total interés': Decimal('20000')
        ... })
    """
    st.subheader(title)
    
    # Convert to DataFrame
    df = pd.DataFrame([data])
    
    # Format monetary columns
    formatted_data = {}
    for key, value in data.items():
        if isinstance(value, (Decimal, float, int)):
            formatted_data[key] = format_currency(value, currency_symbol, decimals)
        else:
            formatted_data[key] = value
    
    df_formatted = pd.DataFrame([formatted_data])
    
    st.dataframe(df_formatted, use_container_width=True, hide_index=True)


def display_totals_table(
    schedule: pd.DataFrame,
    currency_symbol: str = "$",
    decimals: int = 2,
    title: str = "Totales"
) -> None:
    """
    Display totals table from amortization schedule.
    
    Calculates and displays total payments and total interest
    from an amortization schedule.
    
    Args:
        schedule: Amortization schedule DataFrame
        currency_symbol: Currency symbol for formatting
        decimals: Decimal places for formatting
        title: Table title
        
    Example:
        >>> display_totals_table(loan.schedule, "$", 2)
    """
    st.subheader(title)
    
    # Calculate totals
    total_paid = float(schedule["Pago"].sum())
    total_interest = float(schedule["Interés"].sum())
    
    # Create totals DataFrame
    totals_data = {
        "Total monto a pagar": format_currency(total_paid, currency_symbol, decimals),
        "Total interés a pagar": format_currency(total_interest, currency_symbol, decimals)
    }
    
    df_totals = pd.DataFrame([totals_data])
    
    st.dataframe(df_totals, use_container_width=True, hide_index=True)


def display_comparison_summary(
    scenarios: List[dict],
    best_scenario_id: str,
    currency_symbol: str = "$",
    decimals: int = 2,
    title: str = "Resumen de comparación"
) -> None:
    """
    Display comparison summary highlighting the best scenario.
    
    Shows a summary of all scenarios with the best one highlighted.
    
    Args:
        scenarios: List of scenario dictionaries
        best_scenario_id: ID of the best scenario to highlight
        currency_symbol: Currency symbol for formatting
        decimals: Decimal places for formatting
        title: Table title
        
    Example:
        >>> display_comparison_summary(
        ...     [scenario1.to_dict(), scenario2.to_dict()],
        ...     best_scenario_id='1'
        ... )
    """
    st.subheader(title)
    
    # Convert to DataFrame
    df = pd.DataFrame(scenarios)
    
    # Add best indicator
    df['Es mejor'] = df['id'] == best_scenario_id
    
    # Format monetary columns
    for col in ['principal', 'monthly_payment', 'total_paid', 'total_interest']:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: format_currency(x, currency_symbol, decimals)
            )
    
    # Format percentage columns
    for col in ['annual_rate', 'monthly_rate', 'effective_annual_rate']:
        if col in df.columns:
            df[col] = df[col].apply(
                lambda x: format_percentage(x, decimals)
            )
    
    # Highlight best row
    def highlight_best_row(row):
        if row.get('Es mejor', False):
            return ['background-color: #d4edda'] * len(row)
        return [''] * len(row)
    
    styled_df = df.style.apply(highlight_best_row, axis=1)
    st.dataframe(styled_df, use_container_width=True, hide_index=True)


def display_paginated_table(
    df: pd.DataFrame,
    page_size: int = 50,
    title: Optional[str] = None
) -> None:
    """
    Display large table with pagination.
    
    For tables with many rows, displays them in pages to improve
    performance and usability.
    
    Args:
        df: DataFrame to display
        page_size: Number of rows per page
        title: Table title (optional)
        
    Example:
        >>> display_paginated_table(large_schedule, page_size=50)
    """
    if title:
        st.subheader(title)
    
    total_rows = len(df)
    total_pages = (total_rows + page_size - 1) // page_size
    
    if total_pages > 1:
        # Add page selector
        page = st.selectbox(
            "Página",
            options=range(1, total_pages + 1),
            format_func=lambda x: f"Página {x} de {total_pages}"
        )
        
        # Calculate slice
        start_idx = (page - 1) * page_size
        end_idx = min(start_idx + page_size, total_rows)
        
        # Display page
        st.dataframe(df.iloc[start_idx:end_idx], use_container_width=True, hide_index=True)
        
        st.caption(f"Mostrando filas {start_idx + 1} a {end_idx} de {total_rows}")
    else:
        # Display all rows
        st.dataframe(df, use_container_width=True, hide_index=True)
