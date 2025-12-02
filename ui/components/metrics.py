"""
Metric display components for loan data.

This module provides reusable metric components for displaying
key loan metrics using Streamlit's st.metric widget with proper
formatting and delta calculations.
"""

from typing import Optional, List, Dict
from decimal import Decimal
import streamlit as st

from utils.formatters import format_currency, format_percentage
from models.loan import LoanMetrics


def display_loan_metrics(
    monthly_payment: Decimal,
    total_paid: Decimal,
    total_interest: Decimal,
    annual_rate: Decimal,
    currency_symbol: str = "$",
    decimals_money: int = 2,
    decimals_percent: int = 2,
    principal: Optional[Decimal] = None
) -> None:
    """
    Display loan metrics in columns using st.metric.
    
    Shows the key financial metrics for a loan in a clean,
    organized layout with proper formatting.
    
    Args:
        monthly_payment: Monthly payment amount
        total_paid: Total amount to be paid over loan term
        total_interest: Total interest to be paid
        annual_rate: Annual interest rate (as decimal, e.g., 0.12 for 12%)
        currency_symbol: Currency symbol for formatting
        decimals_money: Decimal places for monetary values
        decimals_percent: Decimal places for percentages
        principal: Optional principal amount (for additional context)
        
    Example:
        >>> display_loan_metrics(
        ...     Decimal('856.07'),
        ...     Decimal('102728.40'),
        ...     Decimal('2728.40'),
        ...     Decimal('0.12'),
        ...     '$', 2, 2
        ... )
    """
    # Determine number of columns based on whether principal is provided
    if principal is not None:
        col1, col2, col3, col4, col5 = st.columns(5)
    else:
        col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Pago mensual",
            format_currency(monthly_payment, currency_symbol, decimals_money)
        )
    
    with col2:
        st.metric(
            "Tasa nominal anual",
            format_percentage(annual_rate, decimals_percent)
        )
    
    with col3:
        st.metric(
            "Total a pagar",
            format_currency(total_paid, currency_symbol, decimals_money)
        )
    
    with col4:
        st.metric(
            "Total de intereses",
            format_currency(total_interest, currency_symbol, decimals_money)
        )
    
    if principal is not None:
        with col5:
            st.metric(
                "Monto del crédito",
                format_currency(principal, currency_symbol, decimals_money)
            )


def display_loan_metrics_from_object(
    metrics: LoanMetrics,
    principal: Decimal,
    currency_symbol: str = "$",
    decimals_money: int = 2,
    decimals_percent: int = 2
) -> None:
    """
    Display loan metrics from a LoanMetrics object.
    
    Convenience function that accepts a LoanMetrics object
    instead of individual values.
    
    Args:
        metrics: LoanMetrics object with calculated values
        principal: Loan principal amount
        currency_symbol: Currency symbol for formatting
        decimals_money: Decimal places for monetary values
        decimals_percent: Decimal places for percentages
        
    Example:
        >>> loan = Loan(params).calculate()
        >>> display_loan_metrics_from_object(
        ...     loan.metrics,
        ...     loan.parameters.principal
        ... )
    """
    display_loan_metrics(
        metrics.monthly_payment,
        metrics.total_paid,
        metrics.total_interest,
        metrics.monthly_rate * 12,  # Convert monthly to annual
        currency_symbol,
        decimals_money,
        decimals_percent,
        principal
    )


def display_comparison_metrics(
    scenarios: List[Dict],
    best_scenario_id: str,
    metric_names: Optional[List[str]] = None,
    currency_symbol: str = "$",
    decimals_money: int = 2,
    decimals_percent: int = 2
) -> None:
    """
    Display comparison metrics with delta from best scenario.
    
    Shows key metrics for multiple scenarios with deltas indicating
    how much worse each scenario is compared to the best one.
    
    Args:
        scenarios: List of scenario dictionaries with metrics
        best_scenario_id: ID of the best scenario
        metric_names: List of metric names to display (defaults to key metrics)
        currency_symbol: Currency symbol for formatting
        decimals_money: Decimal places for monetary values
        decimals_percent: Decimal places for percentages
        
    Example:
        >>> display_comparison_metrics(
        ...     [scenario1.to_dict(), scenario2.to_dict()],
        ...     best_scenario_id='1'
        ... )
    """
    if metric_names is None:
        metric_names = ['monthly_payment', 'total_interest', 'total_paid']
    
    # Find best scenario values
    best_scenario = next((s for s in scenarios if s['id'] == best_scenario_id), None)
    if not best_scenario:
        st.error("Best scenario not found")
        return
    
    # Display each scenario
    for scenario in scenarios:
        st.markdown(f"### {scenario['name']}")
        
        cols = st.columns(len(metric_names))
        
        for idx, metric_name in enumerate(metric_names):
            with cols[idx]:
                value = scenario.get(metric_name)
                best_value = best_scenario.get(metric_name)
                
                if value is None or best_value is None:
                    continue
                
                # Calculate delta
                delta = value - best_value if scenario['id'] != best_scenario_id else None
                
                # Format based on metric type
                if 'rate' in metric_name:
                    formatted_value = format_percentage(value, decimals_percent)
                    formatted_delta = format_percentage(delta, decimals_percent) if delta else None
                else:
                    formatted_value = format_currency(value, currency_symbol, decimals_money)
                    formatted_delta = format_currency(delta, currency_symbol, decimals_money) if delta else None
                
                # Display metric
                label = metric_name.replace('_', ' ').title()
                st.metric(
                    label,
                    formatted_value,
                    delta=formatted_delta,
                    delta_color="inverse" if delta else "off"  # Higher is worse for costs
                )
        
        st.divider()


def display_savings_metrics(
    original_total_interest: Decimal,
    new_total_interest: Decimal,
    original_term: int,
    new_term: int,
    currency_symbol: str = "$",
    decimals: int = 2
) -> None:
    """
    Display savings metrics comparing two scenarios.
    
    Shows the savings in interest and time when comparing
    an original loan to an optimized version (e.g., with extra payments).
    
    Args:
        original_total_interest: Total interest in original scenario
        new_total_interest: Total interest in new scenario
        original_term: Original loan term in months
        new_term: New loan term in months
        currency_symbol: Currency symbol for formatting
        decimals: Decimal places for formatting
        
    Example:
        >>> display_savings_metrics(
        ...     Decimal('50000'),
        ...     Decimal('35000'),
        ...     360,
        ...     280
        ... )
    """
    interest_savings = original_total_interest - new_total_interest
    time_savings = original_term - new_term
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        st.metric(
            "Ahorro en intereses",
            format_currency(interest_savings, currency_symbol, decimals),
            delta=format_currency(-interest_savings, currency_symbol, decimals),
            delta_color="normal"
        )
    
    with col2:
        st.metric(
            "Meses ahorrados",
            f"{time_savings} meses",
            delta=f"-{time_savings} meses",
            delta_color="normal"
        )
    
    with col3:
        savings_percent = (interest_savings / original_total_interest * 100) if original_total_interest > 0 else 0
        st.metric(
            "Ahorro porcentual",
            f"{savings_percent:.1f}%",
            delta=f"-{savings_percent:.1f}%",
            delta_color="normal"
        )


def display_capacity_metrics(
    max_loan_amount: Decimal,
    monthly_payment: Decimal,
    annual_rate: Decimal,
    num_payments: int,
    currency_symbol: str = "$",
    decimals_money: int = 2,
    decimals_percent: int = 2
) -> None:
    """
    Display payment capacity calculation metrics.
    
    Shows the maximum loan amount that can be afforded based
    on payment capacity, along with related metrics.
    
    Args:
        max_loan_amount: Maximum affordable loan amount
        monthly_payment: Affordable monthly payment
        annual_rate: Interest rate (as decimal)
        num_payments: Loan term in months
        currency_symbol: Currency symbol for formatting
        decimals_money: Decimal places for monetary values
        decimals_percent: Decimal places for percentages
        
    Example:
        >>> display_capacity_metrics(
        ...     Decimal('100000'),
        ...     Decimal('1000'),
        ...     Decimal('0.12'),
        ...     360
        ... )
    """
    total_to_pay = monthly_payment * Decimal(num_payments)
    total_interest = total_to_pay - max_loan_amount
    
    col1, col2, col3, col4 = st.columns(4)
    
    with col1:
        st.metric(
            "Monto máximo del crédito",
            format_currency(max_loan_amount, currency_symbol, decimals_money)
        )
    
    with col2:
        st.metric(
            "Capacidad de pago mensual",
            format_currency(monthly_payment, currency_symbol, decimals_money)
        )
    
    with col3:
        st.metric(
            "Total a pagar",
            format_currency(total_to_pay, currency_symbol, decimals_money)
        )
    
    with col4:
        st.metric(
            "Total de intereses",
            format_currency(total_interest, currency_symbol, decimals_money)
        )


def display_rate_comparison_metrics(
    scenarios: List[Dict],
    currency_symbol: str = "$",
    decimals_money: int = 2,
    decimals_percent: int = 2
) -> None:
    """
    Display metrics for comparing different interest rates.
    
    Shows a comparison of loans with different rates,
    highlighting the impact of rate differences.
    
    Args:
        scenarios: List of scenario dictionaries with rate information
        currency_symbol: Currency symbol for formatting
        decimals_money: Decimal places for monetary values
        decimals_percent: Decimal places for percentages
        
    Example:
        >>> display_rate_comparison_metrics([
        ...     {'name': 'Banco A', 'annual_rate': 0.12, 'monthly_payment': 856},
        ...     {'name': 'Banco B', 'annual_rate': 0.10, 'monthly_payment': 790}
        ... ])
    """
    if not scenarios:
        return
    
    # Find best (lowest) rate
    best_scenario = min(scenarios, key=lambda s: s.get('annual_rate', float('inf')))
    
    for scenario in scenarios:
        st.markdown(f"### {scenario['name']}")
        
        col1, col2, col3 = st.columns(3)
        
        with col1:
            rate = scenario.get('annual_rate', 0)
            st.metric(
                "Tasa anual",
                format_percentage(rate, decimals_percent)
            )
        
        with col2:
            payment = scenario.get('monthly_payment', 0)
            st.metric(
                "Pago mensual",
                format_currency(payment, currency_symbol, decimals_money)
            )
        
        with col3:
            total_interest = scenario.get('total_interest', 0)
            best_interest = best_scenario.get('total_interest', 0)
            delta = total_interest - best_interest if scenario != best_scenario else None
            
            st.metric(
                "Total intereses",
                format_currency(total_interest, currency_symbol, decimals_money),
                delta=format_currency(delta, currency_symbol, decimals_money) if delta else None,
                delta_color="inverse"
            )
        
        st.divider()
