"""
Analysis service for loan sensitivity and scenario analysis.

This module provides advanced analysis functions for loan scenarios including:
- Sensitivity analysis: How parameter changes affect loan metrics
- Tornado analysis: Relative impact comparison of different variables
- Early payoff analysis: Comparing original vs. early payment schedules
- Payment frequency comparison: Analyzing different payment schedules

All functions return structured data suitable for visualization and export.
"""

from decimal import Decimal
from typing import Dict, List, Tuple, Optional
import pandas as pd

from models.loan import Loan, LoanParameters
from core.amortization import AmortizationSchedule
from core.calculations import calculate_monthly_payment


def sensitivity_analysis(
    base_loan: Loan,
    variable: str,
    min_value: Decimal,
    max_value: Decimal,
    num_steps: int = 10
) -> pd.DataFrame:
    """
    Perform sensitivity analysis by sweeping a parameter across a range.
    
    This function varies one loan parameter while keeping others constant,
    calculating how the change affects key loan metrics. This helps users
    understand which parameters have the most impact on their loan costs.
    
    Args:
        base_loan: Base loan configuration to analyze
        variable: Parameter to vary - one of: "principal", "annual_rate", "num_payments"
        min_value: Minimum value for the parameter sweep
        max_value: Maximum value for the parameter sweep
        num_steps: Number of steps in the sweep (default: 10)
        
    Returns:
        DataFrame with columns:
        - Variable Value: The parameter value for this step
        - Monthly Payment: Calculated monthly payment
        - Total Paid: Total amount paid over loan term
        - Total Interest: Total interest paid
        - Effective Annual Rate: TAE (only varies if rate is the variable)
        
    Raises:
        ValueError: If variable name is invalid or range is invalid
        
    Example:
        >>> base = Loan(LoanParameters(
        ...     principal=Decimal('100000'),
        ...     annual_rate=Decimal('0.12'),
        ...     num_payments=360
        ... )).calculate()
        >>> results = sensitivity_analysis(
        ...     base, "annual_rate",
        ...     Decimal('0.08'), Decimal('0.16'), 5
        ... )
        >>> print(results)
    """
    if variable not in ["principal", "annual_rate", "num_payments"]:
        raise ValueError(f"Invalid variable: {variable}. Must be one of: principal, annual_rate, num_payments")
    
    if min_value >= max_value:
        raise ValueError("min_value must be less than max_value")
    
    if num_steps < 2:
        raise ValueError("num_steps must be at least 2")
    
    # Calculate step size
    step_size = (max_value - min_value) / Decimal(num_steps - 1)
    
    results = []
    
    for i in range(num_steps):
        # Calculate current value
        if variable == "num_payments":
            # For num_payments, we need integer steps
            current_value = int(min_value + (max_value - min_value) * Decimal(i) / Decimal(num_steps - 1))
        else:
            current_value = min_value + step_size * Decimal(i)
        
        # Create loan with modified parameter
        params = LoanParameters(
            principal=current_value if variable == "principal" else base_loan.parameters.principal,
            annual_rate=current_value if variable == "annual_rate" else base_loan.parameters.annual_rate,
            num_payments=current_value if variable == "num_payments" else base_loan.parameters.num_payments
        )
        
        loan = Loan(params).calculate()
        
        # Collect metrics
        results.append({
            "Variable Value": float(current_value),
            "Monthly Payment": float(loan.metrics.monthly_payment),
            "Total Paid": float(loan.metrics.total_paid),
            "Total Interest": float(loan.metrics.total_interest),
            "Effective Annual Rate": float(loan.metrics.effective_annual_rate)
        })
    
    return pd.DataFrame(results)


def tornado_analysis(
    base_loan: Loan,
    variables: Dict[str, Tuple[Decimal, Decimal]],
    target_metric: str = "total_interest"
) -> pd.DataFrame:
    """
    Perform tornado analysis to compare relative impact of variables.
    
    Tornado analysis shows which parameters have the largest impact on a
    target metric by varying each parameter by a fixed percentage and
    measuring the resulting change in the metric.
    
    Args:
        base_loan: Base loan configuration
        variables: Dictionary mapping variable names to (min, max) tuples
                  Example: {
                      "principal": (Decimal('90000'), Decimal('110000')),
                      "annual_rate": (Decimal('0.10'), Decimal('0.14'))
                  }
        target_metric: Metric to analyze - one of: "monthly_payment", "total_interest", "total_paid"
        
    Returns:
        DataFrame with columns:
        - Variable: Parameter name
        - Low Value: Minimum value tested
        - High Value: Maximum value tested
        - Low Impact: Target metric value at low parameter value
        - High Impact: Target metric value at high parameter value
        - Range: Absolute difference (High Impact - Low Impact)
        
        Sorted by Range (descending) to show most impactful variables first
        
    Raises:
        ValueError: If target_metric is invalid
        
    Example:
        >>> results = tornado_analysis(
        ...     base_loan,
        ...     {
        ...         "principal": (Decimal('90000'), Decimal('110000')),
        ...         "annual_rate": (Decimal('0.10'), Decimal('0.14')),
        ...         "num_payments": (300, 420)
        ...     },
        ...     target_metric="total_interest"
        ... )
    """
    valid_metrics = ["monthly_payment", "total_interest", "total_paid"]
    if target_metric not in valid_metrics:
        raise ValueError(f"Invalid target_metric: {target_metric}. Must be one of: {valid_metrics}")
    
    results = []
    
    for var_name, (low_val, high_val) in variables.items():
        if var_name not in ["principal", "annual_rate", "num_payments"]:
            raise ValueError(f"Invalid variable: {var_name}")
        
        # Calculate metric at low value
        low_params = LoanParameters(
            principal=low_val if var_name == "principal" else base_loan.parameters.principal,
            annual_rate=low_val if var_name == "annual_rate" else base_loan.parameters.annual_rate,
            num_payments=int(low_val) if var_name == "num_payments" else base_loan.parameters.num_payments
        )
        low_loan = Loan(low_params).calculate()
        
        # Calculate metric at high value
        high_params = LoanParameters(
            principal=high_val if var_name == "principal" else base_loan.parameters.principal,
            annual_rate=high_val if var_name == "annual_rate" else base_loan.parameters.annual_rate,
            num_payments=int(high_val) if var_name == "num_payments" else base_loan.parameters.num_payments
        )
        high_loan = Loan(high_params).calculate()
        
        # Extract target metric
        low_impact = getattr(low_loan.metrics, target_metric)
        high_impact = getattr(high_loan.metrics, target_metric)
        
        results.append({
            "Variable": var_name,
            "Low Value": float(low_val),
            "High Value": float(high_val),
            "Low Impact": float(low_impact),
            "High Impact": float(high_impact),
            "Range": float(abs(high_impact - low_impact))
        })
    
    # Sort by range (descending) to show most impactful first
    df = pd.DataFrame(results)
    df = df.sort_values("Range", ascending=False).reset_index(drop=True)
    
    return df


def early_payoff_analysis(
    base_loan: Loan,
    extra_payment_schedule: Dict[int, Decimal]
) -> Dict[str, any]:
    """
    Analyze the impact of extra payments on loan payoff.
    
    This function compares the original loan schedule with a schedule that
    includes extra payments, calculating the savings in interest and time.
    
    Args:
        base_loan: Original loan without extra payments
        extra_payment_schedule: Dictionary mapping month numbers to extra payment amounts
                               Example: {1: Decimal('100')} means $100 extra every month
                               Or: {6: Decimal('1000'), 12: Decimal('1000')} for lump sums
        
    Returns:
        Dictionary containing:
        - original_schedule: DataFrame of original amortization schedule
        - modified_schedule: DataFrame with extra payments applied
        - original_payoff_month: Month when original loan is paid off
        - modified_payoff_month: Month when loan with extra payments is paid off
        - months_saved: Number of months saved
        - original_total_interest: Total interest on original schedule
        - modified_total_interest: Total interest with extra payments
        - interest_saved: Amount of interest saved
        - total_extra_payments: Sum of all extra payments made
        - net_savings: Interest saved minus extra payments made
        
    Example:
        >>> # Add $100 extra payment every month
        >>> extra_schedule = {i: Decimal('100') for i in range(1, 361)}
        >>> analysis = early_payoff_analysis(base_loan, extra_schedule)
        >>> print(f"Months saved: {analysis['months_saved']}")
        >>> print(f"Interest saved: ${analysis['interest_saved']}")
    """
    # Ensure base loan is calculated
    if base_loan._metrics is None:
        base_loan.calculate()
    
    # Get original schedule
    original_amort = base_loan.amortization_schedule
    original_schedule = original_amort.generate()
    original_payoff_month = original_amort.get_payoff_month()
    original_total_interest = original_amort.get_total_interest()
    
    # Generate modified schedule with extra payments
    modified_amort = original_amort.with_extra_payments(extra_payment_schedule)
    modified_schedule = modified_amort.get_schedule()
    modified_payoff_month = modified_amort.get_payoff_month()
    modified_total_interest = modified_amort.get_total_interest()
    
    # Calculate savings
    months_saved = original_payoff_month - modified_payoff_month
    interest_saved = original_total_interest - modified_total_interest
    
    # Calculate total extra payments made
    # Only count extra payments up to the modified payoff month
    total_extra_payments = Decimal('0')
    for month, amount in extra_payment_schedule.items():
        if month <= modified_payoff_month:
            total_extra_payments += amount
    
    # Net savings = interest saved - extra payments made
    # (This can be negative if you pay more extra than you save in interest)
    net_savings = interest_saved - total_extra_payments
    
    return {
        "original_schedule": original_schedule,
        "modified_schedule": modified_schedule,
        "original_payoff_month": original_payoff_month,
        "modified_payoff_month": modified_payoff_month,
        "months_saved": months_saved,
        "original_total_interest": float(original_total_interest),
        "modified_total_interest": float(modified_total_interest),
        "interest_saved": float(interest_saved),
        "total_extra_payments": float(total_extra_payments),
        "net_savings": float(net_savings)
    }


def payment_frequency_comparison(
    principal: Decimal,
    annual_rate: Decimal,
    years: int,
    frequencies: Optional[List[str]] = None
) -> pd.DataFrame:
    """
    Compare different payment frequencies (monthly, bi-weekly, weekly).
    
    This function calculates loan schedules for different payment frequencies,
    showing how more frequent payments can reduce interest and shorten the
    loan term due to more frequent compounding and principal reduction.
    
    Args:
        principal: Loan amount
        annual_rate: Annual nominal interest rate as decimal
        years: Loan term in years
        frequencies: List of frequencies to compare. Options: "monthly", "bi-weekly", "weekly"
                    Default: ["monthly", "bi-weekly", "weekly"]
        
    Returns:
        DataFrame with columns:
        - Frequency: Payment frequency
        - Payments Per Year: Number of payments per year
        - Total Payments: Total number of payments over loan term
        - Payment Amount: Amount of each payment
        - Total Paid: Total amount paid over loan term
        - Total Interest: Total interest paid
        - Effective Annual Rate: TAE
        - Years to Payoff: Actual years to pay off (may be less than term)
        
    Note:
        - Monthly: 12 payments per year
        - Bi-weekly: 26 payments per year (every 2 weeks)
        - Weekly: 52 payments per year
        
        Bi-weekly and weekly payments result in more payments per year,
        which reduces the principal faster and saves interest.
        
    Example:
        >>> comparison = payment_frequency_comparison(
        ...     Decimal('100000'),
        ...     Decimal('0.12'),
        ...     30
        ... )
        >>> print(comparison)
    """
    if frequencies is None:
        frequencies = ["monthly", "bi-weekly", "weekly"]
    
    # Validate frequencies
    valid_frequencies = ["monthly", "bi-weekly", "weekly"]
    for freq in frequencies:
        if freq not in valid_frequencies:
            raise ValueError(f"Invalid frequency: {freq}. Must be one of: {valid_frequencies}")
    
    results = []
    
    for frequency in frequencies:
        if frequency == "monthly":
            payments_per_year = 12
            num_payments = years * 12
            period_rate = annual_rate / Decimal('12')
        elif frequency == "bi-weekly":
            payments_per_year = 26
            num_payments = years * 26
            # Bi-weekly rate: annual rate / 26
            period_rate = annual_rate / Decimal('26')
        elif frequency == "weekly":
            payments_per_year = 52
            num_payments = years * 52
            # Weekly rate: annual rate / 52
            period_rate = annual_rate / Decimal('52')
        
        # Calculate payment amount for this frequency
        if period_rate == 0:
            payment_amount = principal / Decimal(num_payments)
        else:
            one_plus_r = Decimal('1') + period_rate
            factor = one_plus_r ** num_payments
            payment_amount = principal * (period_rate * factor) / (factor - Decimal('1'))
            payment_amount = payment_amount.quantize(Decimal('0.01'))
        
        # Calculate total paid and interest
        total_paid = payment_amount * Decimal(num_payments)
        total_interest = total_paid - principal
        
        # Calculate effective annual rate
        # EAR = (1 + period_rate)^periods_per_year - 1
        effective_annual_rate = ((Decimal('1') + period_rate) ** payments_per_year) - Decimal('1')
        
        # Calculate actual years to payoff (same as term for standard amortization)
        years_to_payoff = Decimal(num_payments) / Decimal(payments_per_year)
        
        results.append({
            "Frequency": frequency,
            "Payments Per Year": payments_per_year,
            "Total Payments": num_payments,
            "Payment Amount": float(payment_amount),
            "Total Paid": float(total_paid),
            "Total Interest": float(total_interest),
            "Effective Annual Rate": float(effective_annual_rate),
            "Years to Payoff": float(years_to_payoff)
        })
    
    return pd.DataFrame(results)
