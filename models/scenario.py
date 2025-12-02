"""
Scenario management models for loan comparison.

This module provides data structures for managing and comparing multiple
loan scenarios. It enables users to save different loan configurations
and compare them side-by-side to make informed borrowing decisions.

The module supports:
- Saving loan scenarios with descriptive names
- Comparing multiple scenarios across key metrics
- Identifying the best scenario based on user-selected criteria
"""

from dataclasses import dataclass, field
from datetime import datetime
from decimal import Decimal
from typing import List, Optional, Dict, Literal
import pandas as pd

from models.loan import Loan, LoanParameters


# Type alias for comparison criteria
ComparisonCriterion = Literal[
    "monthly_payment",
    "total_interest",
    "total_paid",
    "effective_annual_rate"
]


@dataclass
class Scenario:
    """
    A saved loan scenario with metadata.
    
    This dataclass represents a single loan scenario that has been saved
    for comparison. It includes the loan configuration, calculated metrics,
    and metadata like creation time and user-provided name.
    
    Attributes:
        id: Unique identifier for the scenario
        name: User-provided descriptive name
        loan: Loan object with parameters and calculations
        created_at: Timestamp when scenario was created
    """
    id: str
    name: str
    loan: Loan
    created_at: datetime = field(default_factory=datetime.now)
    
    def to_dict(self) -> Dict:
        """
        Convert scenario to dictionary for display or storage.
        
        Returns:
            Dictionary with scenario details and key metrics
        """
        metrics = self.loan.metrics
        return {
            "id": self.id,
            "name": self.name,
            "principal": self.loan.parameters.principal,
            "annual_rate": self.loan.parameters.annual_rate,
            "num_payments": self.loan.parameters.num_payments,
            "monthly_payment": metrics.monthly_payment,
            "total_paid": metrics.total_paid,
            "total_interest": metrics.total_interest,
            "monthly_rate": metrics.monthly_rate,
            "effective_annual_rate": metrics.effective_annual_rate,
            "created_at": self.created_at
        }


class ScenarioComparison:
    """
    Manages comparison of multiple loan scenarios.
    
    This class provides functionality for comparing multiple loan scenarios
    side-by-side, identifying the best option based on various criteria,
    and generating comparison tables for display.
    
    The comparison supports multiple criteria:
    - Lowest monthly payment
    - Lowest total interest
    - Lowest total paid
    - Lowest effective annual rate
    
    Attributes:
        scenarios: List of Scenario objects to compare
        
    Example:
        >>> scenario1 = Scenario(id="1", name="Bank A", loan=loan1)
        >>> scenario2 = Scenario(id="2", name="Bank B", loan=loan2)
        >>> comparison = ScenarioComparison([scenario1, scenario2])
        >>> best = comparison.get_best_scenario("total_interest")
        >>> print(f"Best option: {best.name}")
        >>> df = comparison.to_dataframe()
        >>> print(df)
    """
    
    def __init__(self, scenarios: List[Scenario]):
        """
        Initialize a ScenarioComparison with a list of scenarios.
        
        Args:
            scenarios: List of Scenario objects to compare
            
        Raises:
            ValueError: If scenarios list is empty
        """
        if not scenarios:
            raise ValueError("Cannot create comparison with empty scenario list")
        
        self.scenarios = scenarios
    
    def get_best_scenario(
        self,
        criterion: ComparisonCriterion = "total_interest"
    ) -> Scenario:
        """
        Identify the best scenario based on the specified criterion.
        
        The "best" scenario is determined by finding the minimum value
        for the specified metric. For example:
        - "monthly_payment": Lowest monthly payment
        - "total_interest": Lowest total interest paid
        - "total_paid": Lowest total amount paid
        - "effective_annual_rate": Lowest effective annual rate
        
        Args:
            criterion: Metric to optimize ("monthly_payment", "total_interest",
                      "total_paid", or "effective_annual_rate")
                      
        Returns:
            Scenario object with the best (minimum) value for the criterion
            
        Raises:
            ValueError: If criterion is not recognized
            
        Example:
            >>> best = comparison.get_best_scenario("total_interest")
            >>> print(f"Lowest interest: {best.loan.metrics.total_interest}")
        """
        if not self.scenarios:
            raise ValueError("No scenarios to compare")
        
        # Map criterion to the corresponding metric attribute
        metric_getters = {
            "monthly_payment": lambda s: s.loan.metrics.monthly_payment,
            "total_interest": lambda s: s.loan.metrics.total_interest,
            "total_paid": lambda s: s.loan.metrics.total_paid,
            "effective_annual_rate": lambda s: s.loan.metrics.effective_annual_rate
        }
        
        if criterion not in metric_getters:
            raise ValueError(
                f"Invalid criterion '{criterion}'. Must be one of: "
                f"{', '.join(metric_getters.keys())}"
            )
        
        # Find scenario with minimum value for the criterion
        getter = metric_getters[criterion]
        best_scenario = min(self.scenarios, key=getter)
        
        return best_scenario
    
    def to_dataframe(
        self,
        include_parameters: bool = True,
        include_metrics: bool = True
    ) -> pd.DataFrame:
        """
        Generate a comparison table as a pandas DataFrame.
        
        Creates a DataFrame with one row per scenario, showing all key
        parameters and metrics for easy side-by-side comparison.
        
        Args:
            include_parameters: Whether to include input parameters
                               (principal, rate, term) in the table
            include_metrics: Whether to include calculated metrics
                            (payment, interest, etc.) in the table
                            
        Returns:
            DataFrame with scenario comparison data
            
        Example:
            >>> df = comparison.to_dataframe()
            >>> print(df[['name', 'monthly_payment', 'total_interest']])
        """
        rows = []
        
        for scenario in self.scenarios:
            row = {"name": scenario.name}
            
            if include_parameters:
                row.update({
                    "principal": scenario.loan.parameters.principal,
                    "annual_rate": scenario.loan.parameters.annual_rate,
                    "num_payments": scenario.loan.parameters.num_payments
                })
            
            if include_metrics:
                metrics = scenario.loan.metrics
                row.update({
                    "monthly_payment": metrics.monthly_payment,
                    "total_paid": metrics.total_paid,
                    "total_interest": metrics.total_interest,
                    "monthly_rate": metrics.monthly_rate,
                    "effective_annual_rate": metrics.effective_annual_rate
                })
            
            rows.append(row)
        
        return pd.DataFrame(rows)
    
    def get_comparison_summary(
        self,
        criterion: ComparisonCriterion = "total_interest"
    ) -> Dict:
        """
        Get a summary of the comparison including best scenario.
        
        Provides a structured summary that includes:
        - Total number of scenarios
        - Best scenario based on criterion
        - Range of values for key metrics
        
        Args:
            criterion: Metric to use for identifying best scenario
            
        Returns:
            Dictionary with comparison summary
            
        Example:
            >>> summary = comparison.get_comparison_summary("total_interest")
            >>> print(f"Best: {summary['best_scenario_name']}")
            >>> print(f"Savings vs worst: {summary['savings']}")
        """
        best = self.get_best_scenario(criterion)
        df = self.to_dataframe(include_parameters=False, include_metrics=True)
        
        # Calculate ranges for key metrics
        summary = {
            "num_scenarios": len(self.scenarios),
            "best_scenario_id": best.id,
            "best_scenario_name": best.name,
            "criterion": criterion,
            "monthly_payment_range": {
                "min": df["monthly_payment"].min(),
                "max": df["monthly_payment"].max(),
                "best": best.loan.metrics.monthly_payment
            },
            "total_interest_range": {
                "min": df["total_interest"].min(),
                "max": df["total_interest"].max(),
                "best": best.loan.metrics.total_interest
            },
            "total_paid_range": {
                "min": df["total_paid"].min(),
                "max": df["total_paid"].max(),
                "best": best.loan.metrics.total_paid
            }
        }
        
        # Calculate potential savings (difference between best and worst)
        if criterion == "total_interest":
            worst_interest = df["total_interest"].max()
            summary["savings"] = worst_interest - best.loan.metrics.total_interest
        elif criterion == "total_paid":
            worst_paid = df["total_paid"].max()
            summary["savings"] = worst_paid - best.loan.metrics.total_paid
        elif criterion == "monthly_payment":
            worst_payment = df["monthly_payment"].max()
            summary["savings_per_month"] = worst_payment - best.loan.metrics.monthly_payment
        
        return summary
    
    def highlight_best(
        self,
        criterion: ComparisonCriterion = "total_interest"
    ) -> pd.DataFrame:
        """
        Generate comparison DataFrame with best values highlighted.
        
        Creates a DataFrame where the best (minimum) value for each metric
        is marked, making it easy to identify the optimal choice.
        
        Args:
            criterion: Primary criterion for identifying best scenario
            
        Returns:
            DataFrame with an additional 'is_best' column indicating
            the best scenario based on the criterion
            
        Example:
            >>> df = comparison.highlight_best("total_interest")
            >>> best_row = df[df['is_best']]
            >>> print(best_row['name'].values[0])
        """
        df = self.to_dataframe()
        best = self.get_best_scenario(criterion)
        
        # Add column indicating which scenario is best
        df["is_best"] = df.index.map(
            lambda i: self.scenarios[i].id == best.id
        )
        
        return df
    
    def __len__(self) -> int:
        """Return number of scenarios in comparison."""
        return len(self.scenarios)
    
    def __repr__(self) -> str:
        """String representation for debugging."""
        return f"ScenarioComparison({len(self.scenarios)} scenarios)"
