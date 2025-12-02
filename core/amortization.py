"""
Amortization schedule generation and manipulation.

This module provides the AmortizationSchedule class for generating and working
with loan amortization schedules. It handles:
- Standard amortization schedule generation
- Final payment adjustment for zero balance
- Extra payment scenarios (recurring and lump sum)
- Schedule analysis (payoff month, total interest)

All monetary calculations use Python's Decimal type for precision.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Dict, Optional
import pandas as pd


class AmortizationSchedule:
    """
    Represents a complete loan amortization schedule.
    
    This class generates and manages amortization schedules for loans,
    including support for extra payments and early payoff scenarios.
    
    Attributes:
        principal: Original loan amount
        annual_rate: Annual nominal interest rate (as decimal, e.g., 0.12 for 12%)
        num_payments: Total number of scheduled monthly payments
        monthly_payment: Regular monthly payment amount
    """
    
    def __init__(
        self,
        principal: Decimal,
        annual_rate: Decimal,
        num_payments: int,
        monthly_payment: Decimal
    ):
        """
        Initialize an AmortizationSchedule.
        
        Args:
            principal: Loan amount (must be positive)
            annual_rate: Annual nominal interest rate as decimal
            num_payments: Total number of monthly payments
            monthly_payment: Regular monthly payment amount
            
        Raises:
            ValueError: If inputs are invalid
        """
        if principal < 0:
            raise ValueError("Principal must be non-negative")
        if num_payments <= 0:
            raise ValueError("Number of payments must be positive")
        if monthly_payment < 0:
            raise ValueError("Monthly payment must be non-negative")
            
        self.principal = principal
        self.annual_rate = annual_rate
        self.num_payments = num_payments
        self.monthly_payment = monthly_payment
        self._schedule: Optional[pd.DataFrame] = None
        
    def generate(self) -> pd.DataFrame:
        """
        Generate the complete amortization schedule.
        
        Creates a DataFrame with columns:
        - Mes: Payment number (0 = initial, 1-n = payment periods)
        - Pago: Payment amount for that period
        - Interés: Interest portion of payment
        - Abono a capital: Principal portion of payment
        - Saldo restante: Remaining balance after payment
        
        The final payment is automatically adjusted to ensure zero balance,
        eliminating rounding errors.
        
        Returns:
            DataFrame containing the complete amortization schedule
        """
        if self._schedule is not None:
            return self._schedule
            
        # Calculate monthly interest rate
        monthly_rate = self.annual_rate / Decimal('12')
        
        # Initialize balance
        balance = self.principal
        
        # Create initial row (month 0)
        rows = [{
            "Mes": 0,
            "Pago": Decimal('0'),
            "Interés": Decimal('0'),
            "Abono a capital": Decimal('0'),
            "Saldo restante": balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        }]
        
        # Generate schedule for each payment period
        for month in range(1, self.num_payments + 1):
            # Calculate interest for current period
            interest = balance * monthly_rate if monthly_rate > 0 else Decimal('0')
            
            # Calculate principal payment
            principal_payment = self.monthly_payment - interest
            
            # Adjust final payment to eliminate residual balance
            if principal_payment > balance or month == self.num_payments:
                principal_payment = balance
                actual_payment = interest + principal_payment
            else:
                actual_payment = self.monthly_payment
            
            # Update balance
            balance = balance - principal_payment
            
            # Ensure balance doesn't go negative due to rounding
            if balance < Decimal('0.01'):
                balance = Decimal('0')
            
            # Add row to schedule
            rows.append({
                "Mes": month,
                "Pago": actual_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "Interés": interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "Abono a capital": principal_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "Saldo restante": balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            })
            
            # Stop if loan is paid off
            if balance == Decimal('0'):
                break
        
        self._schedule = pd.DataFrame(rows)
        return self._schedule

    def with_extra_payments(
        self,
        extra_payment_schedule: Dict[int, Decimal]
    ) -> 'AmortizationSchedule':
        """
        Create a new schedule with extra payments applied.
        
        This method generates a new amortization schedule that includes
        additional payments at specified months. Extra payments reduce
        the principal balance, which shortens the loan term and reduces
        total interest paid.
        
        Args:
            extra_payment_schedule: Dictionary mapping month numbers to extra payment amounts
                                   Example: {6: Decimal('1000'), 12: Decimal('500')}
                                   means $1000 extra at month 6, $500 extra at month 12
        
        Returns:
            New AmortizationSchedule instance with extra payments applied
            
        Note:
            The returned schedule will have a different structure - it generates
            its own schedule with the extra payments incorporated. The num_payments
            may be shorter if the loan is paid off early.
        """
        # Calculate monthly interest rate
        monthly_rate = self.annual_rate / Decimal('12')
        
        # Initialize balance
        balance = self.principal
        
        # Create initial row (month 0)
        rows = [{
            "Mes": 0,
            "Pago": Decimal('0'),
            "Interés": Decimal('0'),
            "Abono a capital": Decimal('0'),
            "Saldo restante": balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
        }]
        
        # Generate schedule with extra payments
        month = 1
        while balance > Decimal('0.01') and month <= self.num_payments:
            # Calculate interest for current period
            interest = balance * monthly_rate if monthly_rate > 0 else Decimal('0')
            
            # Start with regular payment
            total_payment = self.monthly_payment
            
            # Add extra payment if scheduled for this month
            extra_payment = extra_payment_schedule.get(month, Decimal('0'))
            total_payment += extra_payment
            
            # Calculate principal payment
            principal_payment = total_payment - interest
            
            # Don't pay more than remaining balance
            if principal_payment > balance:
                principal_payment = balance
                total_payment = interest + principal_payment
            
            # Update balance
            balance = balance - principal_payment
            
            # Ensure balance doesn't go negative
            if balance < Decimal('0.01'):
                balance = Decimal('0')
            
            # Add row to schedule
            rows.append({
                "Mes": month,
                "Pago": total_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "Interés": interest.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "Abono a capital": principal_payment.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
                "Saldo restante": balance.quantize(Decimal('0.01'), rounding=ROUND_HALF_UP),
            })
            
            month += 1
        
        # Create a new schedule instance with the modified data
        new_schedule = AmortizationSchedule(
            self.principal,
            self.annual_rate,
            month - 1,  # Actual number of payments made
            self.monthly_payment
        )
        new_schedule._schedule = pd.DataFrame(rows)
        
        return new_schedule
    
    def get_payoff_month(self) -> int:
        """
        Get the month when the loan is fully paid off.
        
        Returns:
            Month number when balance reaches zero (last payment month)
        """
        schedule = self.generate()
        # Find the last row where balance is > 0, then add 1
        # Or find the first row where balance is 0
        zero_balance_rows = schedule[schedule["Saldo restante"] == 0]
        if len(zero_balance_rows) > 0:
            return int(zero_balance_rows.iloc[0]["Mes"])
        # If no zero balance found, return the last month
        return int(schedule.iloc[-1]["Mes"])
    
    def get_total_interest(self) -> Decimal:
        """
        Get total interest paid over the loan term.
        
        Returns:
            Total interest paid as Decimal
        """
        schedule = self.generate()
        # Sum all interest payments (excluding month 0)
        total_interest = schedule[schedule["Mes"] > 0]["Interés"].sum()
        return Decimal(str(total_interest)).quantize(Decimal('0.01'), rounding=ROUND_HALF_UP)
    
    def get_schedule(self) -> pd.DataFrame:
        """
        Get the amortization schedule DataFrame.
        
        This is a convenience method that calls generate() if needed.
        
        Returns:
            DataFrame containing the amortization schedule
        """
        return self.generate()
