"""
Tests for the analysis service module.

This module tests the advanced analysis functions including sensitivity
analysis, tornado analysis, early payoff analysis, and payment frequency
comparison.
"""

import pytest
from decimal import Decimal
import pandas as pd

from services.analysis_service import (
    sensitivity_analysis,
    tornado_analysis,
    early_payoff_analysis,
    payment_frequency_comparison
)
from models.loan import Loan, LoanParameters


@pytest.fixture
def base_loan():
    """Create a base loan for testing."""
    params = LoanParameters(
        principal=Decimal('100000'),
        annual_rate=Decimal('0.12'),
        num_payments=360,
        name="Test Loan"
    )
    return Loan(params).calculate()


class TestSensitivityAnalysis:
    """Tests for sensitivity_analysis function."""
    
    def test_sensitivity_analysis_principal(self, base_loan):
        """Test sensitivity analysis varying principal."""
        result = sensitivity_analysis(
            base_loan,
            "principal",
            Decimal('80000'),
            Decimal('120000'),
            num_steps=5
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 5
        assert "Variable Value" in result.columns
        assert "Monthly Payment" in result.columns
        assert "Total Interest" in result.columns
        
        # Check that values are in ascending order
        assert result["Variable Value"].is_monotonic_increasing
        
        # Check that monthly payment increases with principal
        assert result["Monthly Payment"].is_monotonic_increasing
    
    def test_sensitivity_analysis_rate(self, base_loan):
        """Test sensitivity analysis varying interest rate."""
        result = sensitivity_analysis(
            base_loan,
            "annual_rate",
            Decimal('0.08'),
            Decimal('0.16'),
            num_steps=5
        )
        
        assert len(result) == 5
        # Monthly payment should increase with rate
        assert result["Monthly Payment"].is_monotonic_increasing
        # Total interest should increase with rate
        assert result["Total Interest"].is_monotonic_increasing
    
    def test_sensitivity_analysis_num_payments(self, base_loan):
        """Test sensitivity analysis varying number of payments."""
        result = sensitivity_analysis(
            base_loan,
            "num_payments",
            Decimal('240'),
            Decimal('480'),
            num_steps=5
        )
        
        assert len(result) == 5
        # Monthly payment should decrease with more payments
        assert result["Monthly Payment"].iloc[0] > result["Monthly Payment"].iloc[-1]
        # Total interest should increase with more payments
        assert result["Total Interest"].is_monotonic_increasing
    
    def test_sensitivity_analysis_invalid_variable(self, base_loan):
        """Test that invalid variable raises error."""
        with pytest.raises(ValueError, match="Invalid variable"):
            sensitivity_analysis(
                base_loan,
                "invalid_var",
                Decimal('100'),
                Decimal('200'),
                num_steps=5
            )
    
    def test_sensitivity_analysis_invalid_range(self, base_loan):
        """Test that invalid range raises error."""
        with pytest.raises(ValueError, match="min_value must be less than max_value"):
            sensitivity_analysis(
                base_loan,
                "principal",
                Decimal('200000'),
                Decimal('100000'),
                num_steps=5
            )


class TestTornadoAnalysis:
    """Tests for tornado_analysis function."""
    
    def test_tornado_analysis_basic(self, base_loan):
        """Test basic tornado analysis."""
        variables = {
            "principal": (Decimal('90000'), Decimal('110000')),
            "annual_rate": (Decimal('0.10'), Decimal('0.14')),
            "num_payments": (Decimal('300'), Decimal('420'))
        }
        
        result = tornado_analysis(base_loan, variables, "total_interest")
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "Variable" in result.columns
        assert "Range" in result.columns
        
        # Check that results are sorted by range (descending)
        assert result["Range"].is_monotonic_decreasing or len(result) == 1
    
    def test_tornado_analysis_monthly_payment(self, base_loan):
        """Test tornado analysis with monthly_payment metric."""
        variables = {
            "principal": (Decimal('90000'), Decimal('110000')),
            "annual_rate": (Decimal('0.10'), Decimal('0.14'))
        }
        
        result = tornado_analysis(base_loan, variables, "monthly_payment")
        
        assert len(result) == 2
        assert all(result["Range"] > 0)
    
    def test_tornado_analysis_invalid_metric(self, base_loan):
        """Test that invalid metric raises error."""
        variables = {"principal": (Decimal('90000'), Decimal('110000'))}
        
        with pytest.raises(ValueError, match="Invalid target_metric"):
            tornado_analysis(base_loan, variables, "invalid_metric")


class TestEarlyPayoffAnalysis:
    """Tests for early_payoff_analysis function."""
    
    def test_early_payoff_with_monthly_extra(self, base_loan):
        """Test early payoff with consistent monthly extra payments."""
        # Add $100 extra every month for first 120 months
        extra_schedule = {i: Decimal('100') for i in range(1, 121)}
        
        result = early_payoff_analysis(base_loan, extra_schedule)
        
        assert "original_schedule" in result
        assert "modified_schedule" in result
        assert "months_saved" in result
        assert "interest_saved" in result
        
        # Should save some months
        assert result["months_saved"] > 0
        
        # Should save some interest
        assert result["interest_saved"] > 0
        
        # Modified payoff should be earlier
        assert result["modified_payoff_month"] < result["original_payoff_month"]
    
    def test_early_payoff_with_lump_sum(self, base_loan):
        """Test early payoff with lump sum payment."""
        # Add $10,000 lump sum at month 60
        extra_schedule = {60: Decimal('10000')}
        
        result = early_payoff_analysis(base_loan, extra_schedule)
        
        assert result["months_saved"] > 0
        assert result["interest_saved"] > 0
        assert result["total_extra_payments"] == 10000.0
    
    def test_early_payoff_no_extra_payments(self, base_loan):
        """Test early payoff with no extra payments."""
        result = early_payoff_analysis(base_loan, {})
        
        # Should be identical schedules
        assert result["months_saved"] == 0
        assert result["interest_saved"] == 0.0
        assert result["total_extra_payments"] == 0.0


class TestPaymentFrequencyComparison:
    """Tests for payment_frequency_comparison function."""
    
    def test_payment_frequency_all_frequencies(self):
        """Test comparison with all frequencies."""
        result = payment_frequency_comparison(
            Decimal('100000'),
            Decimal('0.12'),
            30
        )
        
        assert isinstance(result, pd.DataFrame)
        assert len(result) == 3
        assert "Frequency" in result.columns
        assert "Payment Amount" in result.columns
        assert "Total Interest" in result.columns
        
        # Check all frequencies are present
        frequencies = set(result["Frequency"])
        assert frequencies == {"monthly", "bi-weekly", "weekly"}
    
    def test_payment_frequency_monthly_only(self):
        """Test comparison with only monthly frequency."""
        result = payment_frequency_comparison(
            Decimal('100000'),
            Decimal('0.12'),
            30,
            frequencies=["monthly"]
        )
        
        assert len(result) == 1
        assert result.iloc[0]["Frequency"] == "monthly"
        assert result.iloc[0]["Payments Per Year"] == 12
    
    def test_payment_frequency_more_frequent_saves_interest(self):
        """Test that more frequent payments save interest."""
        result = payment_frequency_comparison(
            Decimal('100000'),
            Decimal('0.12'),
            30
        )
        
        monthly_interest = result[result["Frequency"] == "monthly"]["Total Interest"].iloc[0]
        biweekly_interest = result[result["Frequency"] == "bi-weekly"]["Total Interest"].iloc[0]
        weekly_interest = result[result["Frequency"] == "weekly"]["Total Interest"].iloc[0]
        
        # More frequent payments should result in less total interest
        # (though the difference may be small depending on calculation method)
        assert biweekly_interest <= monthly_interest
        assert weekly_interest <= biweekly_interest
    
    def test_payment_frequency_invalid_frequency(self):
        """Test that invalid frequency raises error."""
        with pytest.raises(ValueError, match="Invalid frequency"):
            payment_frequency_comparison(
                Decimal('100000'),
                Decimal('0.12'),
                30,
                frequencies=["invalid"]
            )
    
    def test_payment_frequency_zero_rate(self):
        """Test payment frequency with zero interest rate."""
        result = payment_frequency_comparison(
            Decimal('100000'),
            Decimal('0'),
            30,
            frequencies=["monthly", "bi-weekly"]
        )
        
        # With zero interest, all frequencies should have same total paid
        assert len(result) == 2
        monthly_total = result[result["Frequency"] == "monthly"]["Total Paid"].iloc[0]
        biweekly_total = result[result["Frequency"] == "bi-weekly"]["Total Paid"].iloc[0]
        
        # Should be approximately equal (within rounding)
        assert abs(monthly_total - biweekly_total) < 1.0
