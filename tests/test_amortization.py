"""
Tests for the amortization module.

This module tests the AmortizationSchedule class including:
- Basic schedule generation
- Final balance adjustment
- Extra payment scenarios
- Helper methods
"""

import pytest
from decimal import Decimal
from core.amortization import AmortizationSchedule
from core.calculations import calculate_monthly_payment


def test_basic_schedule_generation():
    """Test that a basic amortization schedule is generated correctly."""
    principal = Decimal('100000')
    annual_rate = Decimal('0.12')
    num_payments = 360
    
    # Calculate monthly payment
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    # Create schedule
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    df = schedule.generate()
    
    # Verify structure
    assert len(df) == num_payments + 1  # +1 for month 0
    assert list(df.columns) == ["Mes", "Pago", "Interés", "Abono a capital", "Saldo restante"]
    
    # Verify initial balance
    assert df.iloc[0]["Saldo restante"] == principal
    
    # Verify final balance is zero
    assert df.iloc[-1]["Saldo restante"] == Decimal('0')


def test_zero_final_balance():
    """Test that the final balance is exactly zero (no rounding errors)."""
    principal = Decimal('50000')
    annual_rate = Decimal('0.08')
    num_payments = 240
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    df = schedule.generate()
    
    # Final balance should be exactly zero
    final_balance = df.iloc[-1]["Saldo restante"]
    assert final_balance == Decimal('0')


def test_sum_of_principal_payments():
    """Test that sum of principal payments equals original principal."""
    principal = Decimal('75000')
    annual_rate = Decimal('0.10')
    num_payments = 180
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    df = schedule.generate()
    
    # Sum of principal payments (excluding month 0)
    total_principal_paid = df[df["Mes"] > 0]["Abono a capital"].sum()
    
    # Should equal original principal (within small rounding tolerance)
    assert abs(Decimal(str(total_principal_paid)) - principal) < Decimal('0.10')


def test_get_total_interest():
    """Test the get_total_interest helper method."""
    principal = Decimal('100000')
    annual_rate = Decimal('0.12')
    num_payments = 360
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    
    total_interest = schedule.get_total_interest()
    
    # Total interest should be positive
    assert total_interest > Decimal('0')
    
    # Verify it matches sum from schedule
    df = schedule.generate()
    schedule_interest = df[df["Mes"] > 0]["Interés"].sum()
    assert abs(total_interest - Decimal(str(schedule_interest))) < Decimal('0.01')


def test_get_payoff_month():
    """Test the get_payoff_month helper method."""
    principal = Decimal('100000')
    annual_rate = Decimal('0.12')
    num_payments = 360
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    
    payoff_month = schedule.get_payoff_month()
    
    # Should be the last month
    assert payoff_month == num_payments


def test_extra_payments_reduce_term():
    """Test that extra payments reduce the loan term."""
    principal = Decimal('100000')
    annual_rate = Decimal('0.12')
    num_payments = 360
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    # Create base schedule
    base_schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    base_payoff = base_schedule.get_payoff_month()
    
    # Create schedule with extra payments
    extra_payments = {
        12: Decimal('5000'),  # $5000 extra at month 12
        24: Decimal('5000'),  # $5000 extra at month 24
    }
    extra_schedule = base_schedule.with_extra_payments(extra_payments)
    extra_payoff = extra_schedule.get_payoff_month()
    
    # Extra payments should reduce payoff time
    assert extra_payoff < base_payoff


def test_extra_payments_reduce_interest():
    """Test that extra payments reduce total interest paid."""
    principal = Decimal('100000')
    annual_rate = Decimal('0.12')
    num_payments = 360
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    
    # Create base schedule
    base_schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    base_interest = base_schedule.get_total_interest()
    
    # Create schedule with extra payments
    extra_payments = {
        12: Decimal('5000'),
        24: Decimal('5000'),
    }
    extra_schedule = base_schedule.with_extra_payments(extra_payments)
    extra_interest = extra_schedule.get_total_interest()
    
    # Extra payments should reduce total interest
    assert extra_interest < base_interest


def test_zero_interest_loan():
    """Test amortization with zero interest rate."""
    principal = Decimal('12000')
    annual_rate = Decimal('0')
    num_payments = 12
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    df = schedule.generate()
    
    # With zero interest, all payments should be equal
    payments = df[df["Mes"] > 0]["Pago"]
    assert all(p == monthly_payment for p in payments)
    
    # All interest should be zero
    assert all(df[df["Mes"] > 0]["Interés"] == Decimal('0'))
    
    # Final balance should be zero
    assert df.iloc[-1]["Saldo restante"] == Decimal('0')


def test_single_payment_loan():
    """Test amortization with a single payment."""
    principal = Decimal('1000')
    annual_rate = Decimal('0.05')
    num_payments = 1
    
    monthly_payment = calculate_monthly_payment(principal, annual_rate, num_payments)
    schedule = AmortizationSchedule(principal, annual_rate, num_payments, monthly_payment)
    df = schedule.generate()
    
    # Should have 2 rows (month 0 and month 1)
    assert len(df) == 2
    
    # Final balance should be zero
    assert df.iloc[-1]["Saldo restante"] == Decimal('0')


if __name__ == "__main__":
    pytest.main([__file__, "-v"])
