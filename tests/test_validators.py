"""
Unit tests for core/validators.py

Tests validation functions for loan inputs, payment inputs, rate ranges,
and payment capacity.
"""

import pytest
from decimal import Decimal
from core.validators import (
    ValidationResult,
    validate_loan_inputs,
    validate_payment_inputs,
    validate_rate_range,
    validate_payment_capacity
)


class TestValidationResult:
    """Tests for ValidationResult class."""
    
    def test_valid_result(self):
        """Test creating a valid ValidationResult."""
        result = ValidationResult(True)
        assert result.is_valid
        assert result.error_message is None
        assert bool(result) is True
    
    def test_invalid_result(self):
        """Test creating an invalid ValidationResult."""
        result = ValidationResult(False, "Test error")
        assert not result.is_valid
        assert result.error_message == "Test error"
        assert bool(result) is False
    
    def test_repr(self):
        """Test string representation."""
        valid = ValidationResult(True)
        assert "valid" in repr(valid)
        
        invalid = ValidationResult(False, "Error message")
        assert "invalid" in repr(invalid)
        assert "Error message" in repr(invalid)


class TestValidateLoanInputs:
    """Tests for validate_loan_inputs function."""
    
    def test_valid_inputs(self):
        """Test validation passes for valid inputs."""
        result = validate_loan_inputs(
            Decimal('100000'),
            Decimal('0.12'),
            360
        )
        assert result.is_valid
        assert result.error_message is None
    
    def test_zero_principal(self):
        """Test validation fails for zero principal."""
        result = validate_loan_inputs(
            Decimal('0'),
            Decimal('0.12'),
            360
        )
        assert not result.is_valid
        assert "greater than zero" in result.error_message
    
    def test_negative_principal(self):
        """Test validation fails for negative principal."""
        result = validate_loan_inputs(
            Decimal('-1000'),
            Decimal('0.12'),
            360
        )
        assert not result.is_valid
        assert "greater than zero" in result.error_message
    
    def test_negative_rate(self):
        """Test validation fails for negative rate."""
        result = validate_loan_inputs(
            Decimal('100000'),
            Decimal('-0.05'),
            360
        )
        assert not result.is_valid
        assert "between 0% and 200%" in result.error_message
    
    def test_excessive_rate(self):
        """Test validation fails for rate > 200%."""
        result = validate_loan_inputs(
            Decimal('100000'),
            Decimal('3.0'),  # 300%
            360
        )
        assert not result.is_valid
        assert "between 0% and 200%" in result.error_message
    
    def test_zero_payments(self):
        """Test validation fails for zero payments."""
        result = validate_loan_inputs(
            Decimal('100000'),
            Decimal('0.12'),
            0
        )
        assert not result.is_valid
        assert "at least 1 month" in result.error_message
    
    def test_negative_payments(self):
        """Test validation fails for negative payments."""
        result = validate_loan_inputs(
            Decimal('100000'),
            Decimal('0.12'),
            -12
        )
        assert not result.is_valid
        assert "at least 1 month" in result.error_message
    
    def test_zero_rate(self):
        """Test validation passes for zero rate."""
        result = validate_loan_inputs(
            Decimal('100000'),
            Decimal('0'),
            360
        )
        assert result.is_valid


class TestValidatePaymentInputs:
    """Tests for validate_payment_inputs function."""
    
    def test_valid_inputs(self):
        """Test validation passes for valid inputs."""
        result = validate_payment_inputs(
            Decimal('1000'),
            Decimal('100000'),
            360
        )
        assert result.is_valid
    
    def test_zero_payment(self):
        """Test validation fails for zero payment."""
        result = validate_payment_inputs(
            Decimal('0'),
            Decimal('100000'),
            360
        )
        assert not result.is_valid
        assert "greater than zero" in result.error_message
    
    def test_negative_payment(self):
        """Test validation fails for negative payment."""
        result = validate_payment_inputs(
            Decimal('-500'),
            Decimal('100000'),
            360
        )
        assert not result.is_valid
        assert "greater than zero" in result.error_message
    
    def test_insufficient_total_payments(self):
        """Test validation fails when total payments < principal."""
        result = validate_payment_inputs(
            Decimal('100'),  # $100/month for 360 months = $36,000 total
            Decimal('100000'),  # Principal is $100,000
            360
        )
        assert not result.is_valid
        assert "insufficient" in result.error_message.lower()
        assert "Total payments" in result.error_message
    
    def test_insufficient_for_interest(self):
        """Test validation fails when total payments don't cover principal."""
        result = validate_payment_inputs(
            Decimal('10'),  # Very small payment: $10 * 360 = $3,600 total
            Decimal('100000'),  # Principal is $100,000
            360
        )
        assert not result.is_valid
        assert "insufficient" in result.error_message.lower()
        assert "Total payments" in result.error_message
    
    def test_zero_principal(self):
        """Test validation fails for zero principal."""
        result = validate_payment_inputs(
            Decimal('1000'),
            Decimal('0'),
            360
        )
        assert not result.is_valid
        assert "greater than zero" in result.error_message
    
    def test_zero_num_payments(self):
        """Test validation fails for zero payments."""
        result = validate_payment_inputs(
            Decimal('1000'),
            Decimal('100000'),
            0
        )
        assert not result.is_valid
        assert "at least 1 month" in result.error_message


class TestValidateRateRange:
    """Tests for validate_rate_range function."""
    
    def test_valid_rate(self):
        """Test validation passes for typical rates."""
        assert validate_rate_range(Decimal('0.05')).is_valid
        assert validate_rate_range(Decimal('0.12')).is_valid
        assert validate_rate_range(Decimal('0.30')).is_valid
    
    def test_zero_rate(self):
        """Test validation passes for zero rate."""
        result = validate_rate_range(Decimal('0'))
        assert result.is_valid
    
    def test_boundary_rate(self):
        """Test validation passes for boundary rate (200%)."""
        result = validate_rate_range(Decimal('2.0'))
        assert result.is_valid
    
    def test_negative_rate(self):
        """Test validation fails for negative rate."""
        result = validate_rate_range(Decimal('-0.05'))
        assert not result.is_valid
        assert "between 0% and 200%" in result.error_message
    
    def test_excessive_rate(self):
        """Test validation fails for rate > 200%."""
        result = validate_rate_range(Decimal('2.5'))
        assert not result.is_valid
        assert "between 0% and 200%" in result.error_message


class TestValidatePaymentCapacity:
    """Tests for validate_payment_capacity function."""
    
    def test_valid_inputs(self):
        """Test validation passes for valid payment capacity."""
        result = validate_payment_capacity(
            Decimal('1000'),
            Decimal('0.12'),
            360
        )
        assert result.is_valid
    
    def test_zero_payment(self):
        """Test validation fails for zero payment capacity."""
        result = validate_payment_capacity(
            Decimal('0'),
            Decimal('0.12'),
            360
        )
        assert not result.is_valid
        assert "greater than zero" in result.error_message
    
    def test_negative_payment(self):
        """Test validation fails for negative payment capacity."""
        result = validate_payment_capacity(
            Decimal('-500'),
            Decimal('0.12'),
            360
        )
        assert not result.is_valid
        assert "greater than zero" in result.error_message
    
    def test_invalid_rate(self):
        """Test validation fails for invalid rate."""
        result = validate_payment_capacity(
            Decimal('1000'),
            Decimal('3.0'),  # 300%
            360
        )
        assert not result.is_valid
        assert "between 0% and 200%" in result.error_message
    
    def test_zero_num_payments(self):
        """Test validation fails for zero payments."""
        result = validate_payment_capacity(
            Decimal('1000'),
            Decimal('0.12'),
            0
        )
        assert not result.is_valid
        assert "at least 1 month" in result.error_message
    
    def test_very_small_payment_capacity(self):
        """Test validation passes even for very small payment capacity."""
        # Note: The validator allows any positive payment capacity.
        # The actual loan calculation will determine if it's viable.
        result = validate_payment_capacity(
            Decimal('1'),  # $1/month
            Decimal('0.12'),  # 12% annual
            360
        )
        assert result.is_valid
    
    def test_zero_rate_with_small_payment(self):
        """Test validation passes for zero rate even with small payment."""
        result = validate_payment_capacity(
            Decimal('10'),
            Decimal('0'),
            360
        )
        assert result.is_valid
