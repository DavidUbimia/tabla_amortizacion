"""
Tests for the rate solver module.

This module tests the RateSolver class including:
- Basic rate solving
- Convergence behavior
- Edge cases (zero rate, insufficient payments)
- Accuracy against known examples
"""

import pytest
from decimal import Decimal
from core.rate_solver import RateSolver
from core.calculations import calculate_monthly_payment


def test_basic_rate_solving():
    """Test that rate solver finds correct rate for known loan."""
    principal = Decimal('100000')
    annual_rate = Decimal('0.12')
    num_payments = 360
    
    # Calculate payment for known rate
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    # Solve for rate
    solver = RateSolver()
    solved_monthly_rate = solver.solve_monthly_rate(principal, monthly_payment, num_payments)
    
    # Should recover the original monthly rate (0.12 / 12 = 0.01)
    expected_monthly_rate = annual_rate / Decimal('12')
    assert solved_monthly_rate is not None
    assert abs(solved_monthly_rate - expected_monthly_rate) < Decimal('0.0001')


def test_solve_annual_rate():
    """Test solving for annual nominal rate."""
    principal = Decimal('50000')
    annual_rate = Decimal('0.08')
    num_payments = 240
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    solver = RateSolver()
    solved_annual_rate = solver.solve_annual_rate(principal, monthly_payment, num_payments)
    
    assert solved_annual_rate is not None
    assert abs(solved_annual_rate - annual_rate) < Decimal('0.0001')


def test_solve_effective_annual_rate():
    """Test solving for effective annual rate (TAE)."""
    principal = Decimal('75000')
    annual_rate = Decimal('0.10')
    num_payments = 180
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    solver = RateSolver()
    solved_tae = solver.solve_effective_annual_rate(principal, monthly_payment, num_payments)
    
    # Calculate expected TAE: (1 + 0.10/12)^12 - 1
    monthly_rate = annual_rate / Decimal('12')
    expected_tae = (Decimal('1') + monthly_rate) ** 12 - Decimal('1')
    
    assert solved_tae is not None
    assert abs(solved_tae - expected_tae) < Decimal('0.0001')


def test_zero_interest_rate():
    """Test that solver correctly identifies zero interest rate."""
    principal = Decimal('12000')
    num_payments = 12
    monthly_payment = principal / Decimal(num_payments)  # No interest
    
    solver = RateSolver()
    solved_rate = solver.solve_monthly_rate(principal, monthly_payment, num_payments)
    
    assert solved_rate is not None
    assert solved_rate == Decimal('0')


def test_insufficient_payments():
    """Test that solver returns None when payments are insufficient."""
    principal = Decimal('100000')
    monthly_payment = Decimal('100')  # Way too small
    num_payments = 360
    
    solver = RateSolver()
    solved_rate = solver.solve_monthly_rate(principal, monthly_payment, num_payments)
    
    # Should return None because total payments < principal
    assert solved_rate is None


def test_high_interest_rate():
    """Test solver with high interest rate."""
    principal = Decimal('10000')
    annual_rate = Decimal('0.30')  # 30% annual
    num_payments = 60
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    solver = RateSolver()
    solved_monthly_rate = solver.solve_monthly_rate(principal, monthly_payment, num_payments)
    
    expected_monthly_rate = annual_rate / Decimal('12')
    assert solved_monthly_rate is not None
    assert abs(solved_monthly_rate - expected_monthly_rate) < Decimal('0.0001')


def test_short_term_loan():
    """Test solver with short-term loan (6 months)."""
    principal = Decimal('5000')
    annual_rate = Decimal('0.06')
    num_payments = 6
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    solver = RateSolver()
    solved_monthly_rate = solver.solve_monthly_rate(principal, monthly_payment, num_payments)
    
    expected_monthly_rate = annual_rate / Decimal('12')
    assert solved_monthly_rate is not None
    assert abs(solved_monthly_rate - expected_monthly_rate) < Decimal('0.0001')


def test_long_term_loan():
    """Test solver with long-term loan (30 years)."""
    principal = Decimal('250000')
    annual_rate = Decimal('0.045')
    num_payments = 360
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    solver = RateSolver()
    solved_monthly_rate = solver.solve_monthly_rate(principal, monthly_payment, num_payments)
    
    expected_monthly_rate = annual_rate / Decimal('12')
    assert solved_monthly_rate is not None
    assert abs(solved_monthly_rate - expected_monthly_rate) < Decimal('0.0001')


def test_convergence_with_custom_precision():
    """Test that custom precision settings work correctly."""
    principal = Decimal('100000')
    annual_rate = Decimal('0.12')
    num_payments = 360
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    # Use lower precision
    solver = RateSolver(precision=Decimal('1e-6'))
    solved_rate = solver.solve_monthly_rate(principal, monthly_payment, num_payments)
    
    expected_monthly_rate = annual_rate / Decimal('12')
    assert solved_rate is not None
    # Should still be reasonably accurate
    assert abs(solved_rate - expected_monthly_rate) < Decimal('0.001')


def test_invalid_inputs():
    """Test that solver handles invalid inputs correctly."""
    solver = RateSolver()
    
    # Zero principal
    assert solver.solve_monthly_rate(Decimal('0'), Decimal('1000'), 12) is None
    
    # Negative principal
    assert solver.solve_monthly_rate(Decimal('-1000'), Decimal('100'), 12) is None
    
    # Zero payment
    assert solver.solve_monthly_rate(Decimal('10000'), Decimal('0'), 12) is None
    
    # Zero periods
    assert solver.solve_monthly_rate(Decimal('10000'), Decimal('1000'), 0) is None


def test_present_value_calculation():
    """Test the internal present value calculation."""
    solver = RateSolver()
    
    # Test with known values
    payment = Decimal('1000')
    rate = Decimal('0.01')  # 1% per period
    periods = 12
    
    pv = solver._present_value(payment, rate, periods)
    
    # Calculate expected PV manually
    # PV = 1000 * [1 - (1.01)^(-12)] / 0.01
    discount_factor = (Decimal('1.01') ** (-12))
    expected_pv = payment * (Decimal('1') - discount_factor) / rate
    
    assert abs(pv - expected_pv) < Decimal('0.01')


def test_present_value_zero_rate():
    """Test present value calculation with zero rate."""
    solver = RateSolver()
    
    payment = Decimal('1000')
    rate = Decimal('0')
    periods = 12
    
    pv = solver._present_value(payment, rate, periods)
    
    # With zero rate, PV = payment * periods
    expected_pv = payment * Decimal(periods)
    assert pv == expected_pv


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
