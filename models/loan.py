"""
Loan data models and domain objects.

This module provides data structures for representing loans and their
calculated metrics. It integrates the core calculation modules to provide
a high-level interface for loan operations.

The Loan class uses lazy calculation - metrics and schedules are only
computed when accessed, improving performance for scenarios where not
all data is needed.
"""

from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
import pandas as pd

from core.calculations import (
    calculate_monthly_payment,
    calculate_total_interest,
    calculate_effective_annual_rate
)
from core.amortization import AmortizationSchedule
from core.validators import validate_loan_inputs


@dataclass
class LoanParameters:
    """
    Input parameters for a loan.
    
    This dataclass encapsulates all the input parameters needed to
    define a loan. It provides a clean interface for passing loan
    configuration between components.
    
    Attributes:
        principal: Original loan amount (must be positive)
        annual_rate: Annual nominal interest rate as decimal (e.g., 0.12 for 12%)
        num_payments: Total number of monthly payments (must be positive)
        name: Optional descriptive name for the loan (e.g., "Bank A - 30 years")
    """
    principal: Decimal
    annual_rate: Decimal
    num_payments: int
    name: Optional[str] = None
    
    def __post_init__(self):
        """Validate parameters after initialization."""
        validation = validate_loan_inputs(self.principal, self.annual_rate, self.num_payments)
        if not validation.is_valid:
            raise ValueError(validation.error_message)


@dataclass
class LoanMetrics:
    """
    Calculated metrics for a loan.
    
    This dataclass contains all the key financial metrics calculated
    from the loan parameters. These metrics are typically displayed
    to users for comparison and decision-making.
    
    Attributes:
        monthly_payment: Regular monthly payment amount
        total_paid: Total amount paid over the loan term (principal + interest)
        total_interest: Total interest paid over the loan term
        monthly_rate: Monthly interest rate as decimal
        effective_annual_rate: Effective annual rate (TAE) accounting for compounding
    """
    monthly_payment: Decimal
    total_paid: Decimal
    total_interest: Decimal
    monthly_rate: Decimal
    effective_annual_rate: Decimal


class Loan:
    """
    Complete loan representation with parameters and calculations.
    
    This class provides a high-level interface for working with loans.
    It encapsulates loan parameters and lazily calculates metrics and
    amortization schedules on demand.
    
    The lazy calculation pattern improves performance by only computing
    values when they are actually needed. For example, if you only need
    the monthly payment, the full amortization schedule won't be generated.
    
    Attributes:
        parameters: LoanParameters object with input values
        
    Example:
        >>> params = LoanParameters(
        ...     principal=Decimal('100000'),
        ...     annual_rate=Decimal('0.12'),
        ...     num_payments=360,
        ...     name="30-year mortgage"
        ... )
        >>> loan = Loan(params)
        >>> loan.calculate()
        >>> print(loan.metrics.monthly_payment)
        1028.61
        >>> schedule = loan.schedule
        >>> print(len(schedule))
        361  # 360 payments + initial row
    """
    
    def __init__(self, parameters: LoanParameters):
        """
        Initialize a Loan with the given parameters.
        
        Args:
            parameters: LoanParameters object containing loan configuration
            
        Raises:
            ValueError: If parameters are invalid (via LoanParameters validation)
        """
        self.parameters = parameters
        self._metrics: Optional[LoanMetrics] = None
        self._schedule: Optional[pd.DataFrame] = None
        self._amortization_schedule: Optional[AmortizationSchedule] = None
    
    def calculate(self) -> 'Loan':
        """
        Perform all loan calculations.
        
        This method calculates the loan metrics (monthly payment, total interest, etc.)
        and stores them for later access. It does not generate the full amortization
        schedule unless explicitly requested via the schedule property.
        
        Returns:
            Self (for method chaining)
            
        Example:
            >>> loan = Loan(params).calculate()
            >>> print(loan.metrics.monthly_payment)
        """
        if self._metrics is not None:
            return self  # Already calculated
        
        # Calculate monthly payment
        monthly_payment = calculate_monthly_payment(
            self.parameters.principal,
            self.parameters.annual_rate,
            self.parameters.num_payments
        )
        
        # Calculate monthly rate
        monthly_rate = self.parameters.annual_rate / Decimal('12')
        
        # Calculate effective annual rate
        effective_annual_rate = calculate_effective_annual_rate(monthly_rate)
        
        # Calculate total interest
        total_interest = calculate_total_interest(
            self.parameters.principal,
            monthly_payment,
            self.parameters.num_payments
        )
        
        # Calculate total paid
        total_paid = self.parameters.principal + total_interest
        
        # Store metrics
        self._metrics = LoanMetrics(
            monthly_payment=monthly_payment,
            total_paid=total_paid,
            total_interest=total_interest,
            monthly_rate=monthly_rate,
            effective_annual_rate=effective_annual_rate
        )
        
        return self
    
    @property
    def metrics(self) -> LoanMetrics:
        """
        Get calculated metrics (calculates if needed).
        
        This property provides lazy access to loan metrics. If metrics
        haven't been calculated yet, they will be computed on first access.
        
        Returns:
            LoanMetrics object with all calculated values
            
        Example:
            >>> loan = Loan(params)
            >>> # Metrics are calculated automatically on first access
            >>> payment = loan.metrics.monthly_payment
        """
        if self._metrics is None:
            self.calculate()
        return self._metrics
    
    @property
    def schedule(self) -> pd.DataFrame:
        """
        Get amortization schedule (generates if needed).
        
        This property provides lazy access to the full amortization schedule.
        The schedule is only generated when first accessed, which can save
        significant computation time if only summary metrics are needed.
        
        Returns:
            DataFrame with columns: Mes, Pago, Interés, Abono a capital, Saldo restante
            
        Example:
            >>> loan = Loan(params)
            >>> schedule = loan.schedule
            >>> print(schedule.head())
        """
        if self._schedule is None:
            # Ensure metrics are calculated first (we need monthly_payment)
            if self._metrics is None:
                self.calculate()
            
            # Create amortization schedule
            self._amortization_schedule = AmortizationSchedule(
                self.parameters.principal,
                self.parameters.annual_rate,
                self.parameters.num_payments,
                self._metrics.monthly_payment
            )
            
            # Generate the schedule
            self._schedule = self._amortization_schedule.generate()
        
        return self._schedule
    
    @property
    def amortization_schedule(self) -> AmortizationSchedule:
        """
        Get the AmortizationSchedule object.
        
        This property provides access to the underlying AmortizationSchedule
        object, which can be useful for advanced operations like applying
        extra payments.
        
        Returns:
            AmortizationSchedule object
            
        Example:
            >>> loan = Loan(params)
            >>> amort = loan.amortization_schedule
            >>> payoff_month = amort.get_payoff_month()
        """
        if self._amortization_schedule is None:
            # Trigger schedule generation
            _ = self.schedule
        
        return self._amortization_schedule
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        name_str = f" '{self.parameters.name}'" if self.parameters.name else ""
        return (
            f"Loan{name_str}(principal={self.parameters.principal}, "
            f"rate={self.parameters.annual_rate:.4f}, "
            f"payments={self.parameters.num_payments})"
        )
