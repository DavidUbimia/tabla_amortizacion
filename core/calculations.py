"""
Core financial calculation functions using Decimal for numerical precision.

This module provides fundamental loan calculation functions including:
- Monthly payment calculation
- Total interest calculation
- Effective annual rate conversion
- Maximum loan amount calculation (inverse calculation)

All monetary calculations use Python's Decimal type to avoid floating-point
precision errors common in financial calculations.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Union


def calculate_monthly_payment(
    principal: Decimal,
    annual_rate: Decimal,
    num_payments: int
) -> Decimal:
    """
    Calculate monthly payment for a loan using the annuity formula.
    
    Uses the standard amortization formula:
    P = M * [r(1+r)^n / ((1+r)^n - 1)]
    
    Where:
    - P = monthly payment
    - M = principal (loan amount)
    - r = monthly interest rate
    - n = number of payments
    
    Args:
        principal: Loan amount (must be positive)
        annual_rate: Annual nominal interest rate as decimal (e.g., Decimal('0.12') for 12%)
        num_payments: Total number of monthly payments (must be positive)
        
    Returns:
        Monthly payment amount as Decimal
        
    Raises:
        ValueError: If inputs are invalid (negative principal, non-positive num_payments)
        
    Examples:
        >>> calculate_monthly_payment(Decimal('100000'), Decimal('0.12'), 360)
        Decimal('1028.61')
    """
    if num_payments <= 0:
        raise ValueError("Number of payments must be positive")
    if principal < 0:
        raise ValueError("Principal must be non-negative")
    if principal == 0:
        return Decimal('0')
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / Decimal('12')
    
    # Handle zero interest rate case
    if monthly_rate == 0:
        return principal / Decimal(num_payments)
    
    # Apply annuity formula: P = M * [r(1+r)^n / ((1+r)^n - 1)]
    one_plus_r = Decimal('1') + monthly_rate
    factor = one_plus_r ** num_payments
    
    payment = principal * (monthly_rate * factor) / (factor - Decimal('1'))
    
    # Round to 2 decimal places (cents)
    return payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_total_interest(
    principal: Decimal,
    monthly_payment: Decimal,
    num_payments: int
) -> Decimal:
    """
    Calculate total interest paid over the loan term.
    
    Total interest = (monthly payment × number of payments) - principal
    
    Args:
        principal: Original loan amount
        monthly_payment: Monthly payment amount
        num_payments: Total number of monthly payments
        
    Returns:
        Total interest paid as Decimal
        
    Examples:
        >>> calculate_total_interest(Decimal('100000'), Decimal('1028.61'), 360)
        Decimal('270299.60')
    """
    total_paid = monthly_payment * Decimal(num_payments)
    total_interest = total_paid - principal
    
    return total_interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


def calculate_effective_annual_rate(monthly_rate: Decimal) -> Decimal:
    """
    Convert monthly interest rate to effective annual rate (TAE).
    
    The effective annual rate accounts for compounding:
    TAE = (1 + r_monthly)^12 - 1
    
    Args:
        monthly_rate: Monthly interest rate as decimal (e.g., Decimal('0.01') for 1%)
        
    Returns:
        Effective annual rate as decimal
        
    Examples:
        >>> calculate_effective_annual_rate(Decimal('0.01'))
        Decimal('0.1268')  # 12.68% effective annual rate
    """
    one_plus_monthly = Decimal('1') + monthly_rate
    effective_annual = one_plus_monthly ** 12 - Decimal('1')
    
    # Round to 6 decimal places for rate precision
    return effective_annual.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)


def calculate_max_loan_amount(
    monthly_payment: Decimal,
    annual_rate: Decimal,
    num_payments: int
) -> Decimal:
    """
    Calculate maximum loan amount based on payment capacity (inverse calculation).
    
    This is the inverse of calculate_monthly_payment. Given a desired monthly
    payment, it calculates the maximum principal that can be borrowed.
    
    Rearranging the annuity formula:
    M = P * [(1+r)^n - 1] / [r(1+r)^n]
    
    Where:
    - M = principal (what we're solving for)
    - P = monthly payment
    - r = monthly interest rate
    - n = number of payments
    
    Args:
        monthly_payment: Affordable monthly payment amount
        annual_rate: Annual nominal interest rate as decimal
        num_payments: Total number of monthly payments
        
    Returns:
        Maximum loan amount as Decimal
        
    Raises:
        ValueError: If inputs are invalid
        
    Examples:
        >>> calculate_max_loan_amount(Decimal('1028.61'), Decimal('0.12'), 360)
        Decimal('100000.00')
    """
    if num_payments <= 0:
        raise ValueError("Number of payments must be positive")
    if monthly_payment <= 0:
        raise ValueError("Monthly payment must be positive")
    
    # Convert annual rate to monthly rate
    monthly_rate = annual_rate / Decimal('12')
    
    # Handle zero interest rate case
    if monthly_rate == 0:
        max_loan = monthly_payment * Decimal(num_payments)
        return max_loan.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    # Apply inverse annuity formula: M = P * [(1+r)^n - 1] / [r(1+r)^n]
    one_plus_r = Decimal('1') + monthly_rate
    factor = one_plus_r ** num_payments
    
    max_loan = monthly_payment * (factor - Decimal('1')) / (monthly_rate * factor)
    
    # Round to 2 decimal places
    return max_loan.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)


# Convenience functions for working with percentage inputs
def calculate_monthly_payment_from_percent(
    principal: Union[Decimal, float],
    annual_rate_percent: Union[Decimal, float],
    num_payments: int
) -> Decimal:
    """
    Convenience wrapper that accepts annual rate as percentage (e.g., 12.0 for 12%).
    
    Args:
        principal: Loan amount
        annual_rate_percent: Annual rate as percentage (e.g., 12.0 for 12%)
        num_payments: Number of payments
        
    Returns:
        Monthly payment amount
    """
    principal_dec = Decimal(str(principal))
    annual_rate_dec = Decimal(str(annual_rate_percent)) / Decimal('100')
    return calculate_monthly_payment(principal_dec, annual_rate_dec, num_payments)


def calculate_max_loan_amount_from_percent(
    monthly_payment: Union[Decimal, float],
    annual_rate_percent: Union[Decimal, float],
    num_payments: int
) -> Decimal:
    """
    Convenience wrapper that accepts annual rate as percentage (e.g., 12.0 for 12%).
    
    Args:
        monthly_payment: Affordable monthly payment
        annual_rate_percent: Annual rate as percentage (e.g., 12.0 for 12%)
        num_payments: Number of payments
        
    Returns:
        Maximum loan amount
    """
    payment_dec = Decimal(str(monthly_payment))
    annual_rate_dec = Decimal(str(annual_rate_percent)) / Decimal('100')
    return calculate_max_loan_amount(payment_dec, annual_rate_dec, num_payments)
