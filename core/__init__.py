"""
Core financial calculation modules.

This package provides the fundamental building blocks for loan calculations:
- calculations: Basic financial formulas (payment, interest, rates)
- amortization: Amortization schedule generation and manipulation
- rate_solver: Interest rate calculation using numerical methods
"""

from core.calculations import (
    calculate_monthly_payment,
    calculate_total_interest,
    calculate_effective_annual_rate,
    calculate_max_loan_amount,
    calculate_monthly_payment_from_percent,
    calculate_max_loan_amount_from_percent,
)

from core.amortization import AmortizationSchedule

from core.rate_solver import RateSolver

__all__ = [
    'calculate_monthly_payment',
    'calculate_total_interest',
    'calculate_effective_annual_rate',
    'calculate_max_loan_amount',
    'calculate_monthly_payment_from_percent',
    'calculate_max_loan_amount_from_percent',
    'AmortizationSchedule',
    'RateSolver',
]
