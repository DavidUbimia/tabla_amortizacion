"""
Chart components for visualizing loan data.

This module provides reusable chart components for displaying
loan amortization schedules, payment breakdowns, and sensitivity
analysis results using Streamlit's built-in charting capabilities.
"""

from typing import Optional
import pandas as pd
import streamlit as st


def display_balance_chart(
    schedule: pd.DataFrame,
    title: str = "Saldo restante por mes",
    x_label: str = "Mes",
    y_label: str = "Saldo restante"
) -> None:
    """
    Display remaining balance line chart.
    
    Shows how the loan balance decreases over time as payments are made.
    This visualization helps users understand the payoff trajectory.
    
    Args:
        schedule: Amortization schedule DataFrame with 'Mes' and 'Saldo restante' columns
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        
    Example:
        >>> display_balance_chart(loan.schedule)
    """
    st.markdown(f"**{title}**")
    
    # Prepare data for charting
    chart_data = schedule.set_index("Mes")["Saldo restante"]
    
    # Display line chart
    st.line_chart(
        data=chart_data,
        x_label=x_label,
        y_label=y_label
    )


def display_payment_breakdown_chart(
    schedule: pd.DataFrame,
    title: str = "Descomposición del pago",
    x_label: str = "Mes",
    y_label: str = "Monto"
) -> None:
    """
    Display stacked area chart of interest vs principal payments.
    
    Shows how each payment is split between interest and principal
    over the life of the loan. This helps users visualize how the
    proportion shifts over time (more interest early, more principal later).
    
    Args:
        schedule: Amortization schedule DataFrame with 'Mes', 'Interés', 
                 and 'Abono a capital' columns
        title: Chart title
        x_label: X-axis label
        y_label: Y-axis label
        
    Example:
        >>> display_payment_breakdown_chart(loan.schedule)
    """
    st.markdown(f"**{title}**")
    
    # Prepare data for charting (exclude row 0 if present)
    chart_data = schedule[schedule["Mes"] > 0].set_index("Mes")[["Interés", "Abono a capital"]]
    
    # Display stacked area chart
    st.area_chart(
        data=chart_data,
        x_label=x_label,
        y_label=y_label
    )


def display_tornado_chart(
    sensitivity_data: pd.DataFrame,
    metric_name: str,
    title: Optional[str] = None,
    variable_col: str = "Variable",
    impact_col: str = "Impacto"
) -> None:
    """
    Display tornado chart for sensitivity analysis.
    
    A tornado chart shows the relative impact of different variables
    on a target metric, sorted by magnitude. This helps identify which
    parameters have the most significant effect on loan outcomes.
    
    Args:
        sensitivity_data: DataFrame with variables and their impact values
        metric_name: Name of the metric being analyzed (e.g., "Total Interest")
        title: Chart title (auto-generated if None)
        variable_col: Name of column containing variable names
        impact_col: Name of column containing impact values
        
    Example:
        >>> tornado_data = pd.DataFrame({
        ...     'Variable': ['Tasa', 'Plazo', 'Monto'],
        ...     'Impacto': [5000, 3000, 1000]
        ... })
        >>> display_tornado_chart(tornado_data, "Total Interest")
    """
    if title is None:
        title = f"Análisis de sensibilidad: {metric_name}"
    
    st.markdown(f"**{title}**")
    
    # Sort by impact magnitude (descending)
    sorted_data = sensitivity_data.sort_values(by=impact_col, ascending=False)
    
    # Display horizontal bar chart
    st.bar_chart(
        data=sorted_data.set_index(variable_col)[impact_col],
        horizontal=True
    )


def display_sensitivity_chart(
    sensitivity_data: pd.DataFrame,
    variable_name: str,
    metric_name: str,
    title: Optional[str] = None,
    x_col: str = "Valor",
    y_col: str = "Resultado"
) -> None:
    """
    Display line chart for sensitivity analysis.
    
    Shows how a target metric changes as a single input variable
    is varied across a range. This helps users understand the
    relationship between inputs and outputs.
    
    Args:
        sensitivity_data: DataFrame with variable values and resulting metrics
        variable_name: Name of the variable being varied (e.g., "Tasa de interés")
        metric_name: Name of the metric being measured (e.g., "Pago mensual")
        title: Chart title (auto-generated if None)
        x_col: Name of column containing variable values
        y_col: Name of column containing metric values
        
    Example:
        >>> sens_data = pd.DataFrame({
        ...     'Valor': [10.0, 11.0, 12.0, 13.0],
        ...     'Resultado': [856, 878, 900, 922]
        ... })
        >>> display_sensitivity_chart(sens_data, "Tasa (%)", "Pago mensual")
    """
    if title is None:
        title = f"Sensibilidad: {metric_name} vs {variable_name}"
    
    st.markdown(f"**{title}**")
    
    # Display line chart
    st.line_chart(
        data=sensitivity_data.set_index(x_col)[y_col],
        x_label=variable_name,
        y_label=metric_name
    )


def display_comparison_chart(
    comparison_data: pd.DataFrame,
    metric_col: str,
    name_col: str = "name",
    title: Optional[str] = None
) -> None:
    """
    Display bar chart comparing scenarios.
    
    Shows a side-by-side comparison of a specific metric across
    multiple loan scenarios, making it easy to identify the best option.
    
    Args:
        comparison_data: DataFrame with scenario names and metric values
        metric_col: Name of column containing the metric to compare
        name_col: Name of column containing scenario names
        title: Chart title (auto-generated if None)
        
    Example:
        >>> comparison_df = pd.DataFrame({
        ...     'name': ['Banco A', 'Banco B', 'Banco C'],
        ...     'total_interest': [50000, 45000, 48000]
        ... })
        >>> display_comparison_chart(comparison_df, 'total_interest')
    """
    if title is None:
        title = f"Comparación: {metric_col}"
    
    st.markdown(f"**{title}**")
    
    # Display bar chart
    st.bar_chart(
        data=comparison_data.set_index(name_col)[metric_col]
    )


def display_dual_line_chart(
    data1: pd.DataFrame,
    data2: pd.DataFrame,
    label1: str,
    label2: str,
    title: str,
    x_label: str = "Mes",
    y_label: str = "Valor"
) -> None:
    """
    Display two line charts side by side for comparison.
    
    Useful for comparing two different scenarios or strategies
    (e.g., original schedule vs. early payoff schedule).
    
    Args:
        data1: First DataFrame with index and values
        data2: Second DataFrame with index and values
        label1: Label for first dataset
        label2: Label for second dataset
        title: Overall title
        x_label: X-axis label
        y_label: Y-axis label
        
    Example:
        >>> display_dual_line_chart(
        ...     original_schedule.set_index('Mes')['Saldo restante'],
        ...     early_payoff_schedule.set_index('Mes')['Saldo restante'],
        ...     'Original', 'Con pagos extra',
        ...     'Comparación de saldos'
        ... )
    """
    st.markdown(f"**{title}**")
    
    col1, col2 = st.columns(2)
    
    with col1:
        st.caption(label1)
        st.line_chart(data=data1, x_label=x_label, y_label=y_label)
    
    with col2:
        st.caption(label2)
        st.line_chart(data=data2, x_label=x_label, y_label=y_label)


def display_stacked_comparison_chart(
    schedule1: pd.DataFrame,
    schedule2: pd.DataFrame,
    label1: str,
    label2: str,
    title: str = "Comparación de escenarios",
    value_col: str = "Saldo restante"
) -> None:
    """
    Display overlaid line charts for direct comparison.
    
    Shows two schedules on the same chart for easy visual comparison.
    
    Args:
        schedule1: First amortization schedule
        schedule2: Second amortization schedule
        label1: Label for first schedule
        label2: Label for second schedule
        title: Chart title
        value_col: Column to plot from schedules
        
    Example:
        >>> display_stacked_comparison_chart(
        ...     original_schedule, early_payoff_schedule,
        ...     'Original', 'Con pagos extra'
        ... )
    """
    st.markdown(f"**{title}**")
    
    # Combine data for overlaid chart
    combined = pd.DataFrame({
        label1: schedule1.set_index("Mes")[value_col],
        label2: schedule2.set_index("Mes")[value_col]
    })
    
    st.line_chart(data=combined, x_label="Mes", y_label=value_col)
