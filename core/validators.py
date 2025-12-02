"""
Input validation functions for loan calculations.

This module provides validation functions for all loan-related inputs,
ensuring data integrity and providing clear error messages for invalid inputs.

All validators return ValidationResult objects that indicate success or failure
with descriptive error messages.
"""

from decimal import Decimal
from typing import Optional


class ValidationResult:
    """
    Result of input validation.
    
    Attributes:
        is_valid: True if validation passed, False otherwise
        error_message: Descriptive error message if validation failed, None otherwise
    """
    
    def __init__(self, is_valid: bool, error_message: Optional[str] = None):
        """
        Initialize a ValidationResult.
        
        Args:
            is_valid: Whether the validation passed
            error_message: Error message if validation failed (optional)
        """
        self.is_valid = is_valid
        self.error_message = error_message
    
    def __bool__(self) -> bool:
        """Allow ValidationResult to be used in boolean context."""
        return self.is_valid
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        if self.is_valid:
            return "ValidationResult(valid)"
        return f"ValidationResult(invalid: {self.error_message})"


def validate_loan_inputs(
    principal: Decimal,
    annual_rate: Decimal,
    num_payments: int
) -> ValidationResult:
    """
    Validate loan calculation inputs.
    
    Checks that:
    - Principal is positive
    - Annual rate is within reasonable bounds (0% to 200%)
    - Number of payments is positive
    
    Args:
        principal: Loan amount
        annual_rate: Annual nominal interest rate as decimal (e.g., 0.12 for 12%)
        num_payments: Total number of monthly payments
        
    Returns:
        ValidationResult indicating success or failure with error message
        
    Examples:
        >>> validate_loan_inputs(Decimal('100000'), Decimal('0.12'), 360)
        ValidationResult(valid)
        
        >>> validate_loan_inputs(Decimal('-1000'), Decimal('0.12'), 360)
        ValidationResult(invalid: Loan amount must be greater than zero)
    """
    # Validate principal
    if principal <= 0:
        return ValidationResult(False, "Loan amount must be greater than zero")
    
    # Validate interest rate range
    rate_validation = validate_rate_range(annual_rate)
    if not rate_validation.is_valid:
        return rate_validation
    
    # Validate number of payments
    if num_payments <= 0:
        return ValidationResult(False, "Loan term must be at least 1 month")
    
    return ValidationResult(True)


def validate_payment_inputs(
    monthly_payment: Decimal,
    principal: Decimal,
    num_payments: int
) -> ValidationResult:
    """
    Validate that payment is sufficient to cover the loan.
    
    Checks that:
    - Monthly payment is positive
    - Total payments exceed principal (otherwise no positive rate exists)
    - Payment is sufficient to cover interest (for non-zero rates)
    
    Args:
        monthly_payment: Monthly payment amount
        principal: Loan amount
        num_payments: Total number of monthly payments
        
    Returns:
        ValidationResult indicating success or failure with error message
        
    Examples:
        >>> validate_payment_inputs(Decimal('1000'), Decimal('100000'), 360)
        ValidationResult(valid)
        
        >>> validate_payment_inputs(Decimal('100'), Decimal('100000'), 360)
        ValidationResult(invalid: Monthly payment of $100.00 is insufficient...)
    """
    # Validate monthly payment is positive
    if monthly_payment <= 0:
        return ValidationResult(False, "Monthly payment must be greater than zero")
    
    # Validate principal is positive
    if principal <= 0:
        return ValidationResult(False, "Loan amount must be greater than zero")
    
    # Validate number of payments is positive
    if num_payments <= 0:
        return ValidationResult(False, "Loan term must be at least 1 month")
    
    # Check that total payments exceed principal
    total_payments = monthly_payment * Decimal(num_payments)
    if total_payments < principal:
        return ValidationResult(
            False,
            f"Monthly payment of ${monthly_payment:.2f} is insufficient to cover "
            f"the loan. Total payments (${total_payments:.2f}) must exceed "
            f"loan amount (${principal:.2f})"
        )
    
    return ValidationResult(True)


def validate_rate_range(rate: Decimal) -> ValidationResult:
    """
    Validate that interest rate is within reasonable bounds.
    
    Checks that the annual rate is between 0% and 200%.
    Rates outside this range are likely data entry errors.
    
    Args:
        rate: Annual interest rate as decimal (e.g., 0.12 for 12%)
        
    Returns:
        ValidationResult indicating success or failure with error message
        
    Examples:
        >>> validate_rate_range(Decimal('0.12'))
        ValidationResult(valid)
        
        >>> validate_rate_range(Decimal('3.5'))
        ValidationResult(invalid: Interest rate must be between 0% and 200%)
    """
    if rate < 0:
        return ValidationResult(
            False,
            "Interest rate must be between 0% and 200%"
        )
    
    if rate > Decimal('2.0'):  # 200% annual rate
        return ValidationResult(
            False,
            "Interest rate must be between 0% and 200%"
        )
    
    return ValidationResult(True)


def validate_payment_capacity(
    monthly_payment: Decimal,
    annual_rate: Decimal,
    num_payments: int
) -> ValidationResult:
    """
    Validate payment capacity inputs for maximum loan calculation.
    
    Checks that:
    - Monthly payment is positive
    - Annual rate is within reasonable bounds
    - Number of payments is positive
    - Payment capacity exceeds minimum viable payment
    
    This validation is specifically for the payment capacity calculator
    feature (Requirement 9.2).
    
    Args:
        monthly_payment: Affordable monthly payment amount
        annual_rate: Annual nominal interest rate as decimal
        num_payments: Total number of monthly payments
        
    Returns:
        ValidationResult indicating success or failure with error message
        
    Examples:
        >>> validate_payment_capacity(Decimal('1000'), Decimal('0.12'), 360)
        ValidationResult(valid)
        
        >>> validate_payment_capacity(Decimal('0'), Decimal('0.12'), 360)
        ValidationResult(invalid: Payment capacity must be greater than zero)
    """
    # Validate monthly payment is positive
    if monthly_payment <= 0:
        return ValidationResult(
            False,
            "Payment capacity must be greater than zero"
        )
    
    # Validate interest rate range
    rate_validation = validate_rate_range(annual_rate)
    if not rate_validation.is_valid:
        return rate_validation
    
    # Validate number of payments
    if num_payments <= 0:
        return ValidationResult(False, "Loan term must be at least 1 month")
    
    return ValidationResult(True)
