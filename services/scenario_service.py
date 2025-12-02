"""
Scenario management service for loan comparison.

This module provides a service layer for managing loan scenarios in the
application. It handles CRUD operations for scenarios and provides
comparison functionality.

The ScenarioRepository uses Streamlit's session state as the storage
backend, making scenarios persist across page navigation within a session.
"""

from typing import List, Optional, Dict
from datetime import datetime
import uuid
import streamlit as st

from models.scenario import Scenario, ScenarioComparison, ComparisonCriterion
from models.loan import Loan


# Session state key for storing scenarios
SCENARIOS_KEY = "saved_scenarios"


class ScenarioRepository:
    """
    Repository for managing loan scenarios in session state.
    
    This class provides CRUD (Create, Read, Update, Delete) operations
    for loan scenarios. It uses Streamlit's session state as the storage
    backend, which persists data across page navigation within a session.
    
    The repository pattern abstracts the storage mechanism, making it
    easy to switch to a different backend (e.g., database, file system)
    in the future without changing the service interface.
    
    Example:
        >>> repo = ScenarioRepository()
        >>> scenario = Scenario(id="1", name="Bank A", loan=loan)
        >>> repo.save(scenario)
        >>> all_scenarios = repo.get_all()
        >>> repo.delete("1")
    """
    
    def __init__(self):
        """Initialize the repository and ensure session state is set up."""
        self._ensure_initialized()
    
    def _ensure_initialized(self) -> None:
        """Ensure the scenarios list exists in session state."""
        if SCENARIOS_KEY not in st.session_state:
            st.session_state[SCENARIOS_KEY] = []
    
    def save(self, scenario: Scenario) -> None:
        """
        Save a scenario to the repository.
        
        If a scenario with the same ID already exists, it will be replaced.
        Otherwise, the scenario will be added to the list.
        
        Args:
            scenario: Scenario object to save
            
        Example:
            >>> repo = ScenarioRepository()
            >>> scenario = Scenario(id="1", name="Option A", loan=loan)
            >>> repo.save(scenario)
        """
        self._ensure_initialized()
        
        scenarios = st.session_state[SCENARIOS_KEY]
        
        # Check if scenario with this ID already exists
        existing_index = None
        for i, existing_scenario in enumerate(scenarios):
            if existing_scenario.id == scenario.id:
                existing_index = i
                break
        
        if existing_index is not None:
            # Replace existing scenario
            scenarios[existing_index] = scenario
        else:
            # Add new scenario
            scenarios.append(scenario)
        
        st.session_state[SCENARIOS_KEY] = scenarios
    
    def get_all(self) -> List[Scenario]:
        """
        Retrieve all saved scenarios.
        
        Returns:
            List of all Scenario objects in the repository
            
        Example:
            >>> repo = ScenarioRepository()
            >>> scenarios = repo.get_all()
            >>> print(f"Found {len(scenarios)} scenarios")
        """
        self._ensure_initialized()
        return st.session_state[SCENARIOS_KEY].copy()
    
    def get_by_id(self, scenario_id: str) -> Optional[Scenario]:
        """
        Retrieve a specific scenario by ID.
        
        Args:
            scenario_id: Unique identifier of the scenario
            
        Returns:
            Scenario object if found, None otherwise
            
        Example:
            >>> repo = ScenarioRepository()
            >>> scenario = repo.get_by_id("abc-123")
            >>> if scenario:
            ...     print(scenario.name)
        """
        self._ensure_initialized()
        
        for scenario in st.session_state[SCENARIOS_KEY]:
            if scenario.id == scenario_id:
                return scenario
        
        return None
    
    def delete(self, scenario_id: str) -> bool:
        """
        Delete a scenario by ID.
        
        Args:
            scenario_id: Unique identifier of the scenario to delete
            
        Returns:
            True if scenario was found and deleted, False otherwise
            
        Example:
            >>> repo = ScenarioRepository()
            >>> success = repo.delete("abc-123")
            >>> if success:
            ...     print("Scenario deleted")
        """
        self._ensure_initialized()
        
        scenarios = st.session_state[SCENARIOS_KEY]
        original_length = len(scenarios)
        
        # Filter out the scenario with matching ID
        scenarios = [s for s in scenarios if s.id != scenario_id]
        
        st.session_state[SCENARIOS_KEY] = scenarios
        
        # Return True if a scenario was actually removed
        return len(scenarios) < original_length
    
    def clear_all(self) -> int:
        """
        Delete all scenarios from the repository.
        
        Returns:
            Number of scenarios that were deleted
            
        Example:
            >>> repo = ScenarioRepository()
            >>> count = repo.clear_all()
            >>> print(f"Deleted {count} scenarios")
        """
        self._ensure_initialized()
        
        count = len(st.session_state[SCENARIOS_KEY])
        st.session_state[SCENARIOS_KEY] = []
        
        return count
    
    def count(self) -> int:
        """
        Get the number of saved scenarios.
        
        Returns:
            Number of scenarios in the repository
            
        Example:
            >>> repo = ScenarioRepository()
            >>> print(f"You have {repo.count()} saved scenarios")
        """
        self._ensure_initialized()
        return len(st.session_state[SCENARIOS_KEY])
    
    def exists(self, scenario_id: str) -> bool:
        """
        Check if a scenario with the given ID exists.
        
        Args:
            scenario_id: Unique identifier to check
            
        Returns:
            True if scenario exists, False otherwise
            
        Example:
            >>> repo = ScenarioRepository()
            >>> if repo.exists("abc-123"):
            ...     print("Scenario found")
        """
        return self.get_by_id(scenario_id) is not None


def save_scenario(loan: Loan, name: str) -> Scenario:
    """
    Save a loan as a named scenario.
    
    This is a convenience function that creates a Scenario object from
    a Loan and saves it to the repository. It automatically generates
    a unique ID and timestamp.
    
    Args:
        loan: Loan object to save
        name: Descriptive name for the scenario
        
    Returns:
        The created Scenario object
        
    Raises:
        ValueError: If name is empty or loan is invalid
        
    Example:
        >>> loan = Loan(params).calculate()
        >>> scenario = save_scenario(loan, "Bank A - 30 years")
        >>> print(f"Saved scenario: {scenario.id}")
    """
    if not name or not name.strip():
        raise ValueError("Scenario name cannot be empty")
    
    if loan is None:
        raise ValueError("Loan cannot be None")
    
    # Ensure loan is calculated
    if loan._metrics is None:
        loan.calculate()
    
    # Generate unique ID
    scenario_id = str(uuid.uuid4())
    
    # Create scenario
    scenario = Scenario(
        id=scenario_id,
        name=name.strip(),
        loan=loan,
        created_at=datetime.now()
    )
    
    # Save to repository
    repo = ScenarioRepository()
    repo.save(scenario)
    
    return scenario


def delete_scenario(scenario_id: str) -> bool:
    """
    Delete a scenario by ID.
    
    This is a convenience function that wraps the repository's delete method.
    
    Args:
        scenario_id: Unique identifier of the scenario to delete
        
    Returns:
        True if scenario was found and deleted, False otherwise
        
    Example:
        >>> success = delete_scenario("abc-123")
        >>> if success:
        ...     st.success("Scenario deleted")
        ... else:
        ...     st.error("Scenario not found")
    """
    repo = ScenarioRepository()
    return repo.delete(scenario_id)


def clear_all_scenarios() -> int:
    """
    Delete all saved scenarios.
    
    This is a convenience function that wraps the repository's clear_all method.
    Use with caution as this operation cannot be undone.
    
    Returns:
        Number of scenarios that were deleted
        
    Example:
        >>> count = clear_all_scenarios()
        >>> st.info(f"Deleted {count} scenarios")
    """
    repo = ScenarioRepository()
    return repo.clear_all()


def get_comparison_data(
    criterion: ComparisonCriterion = "total_interest"
) -> Optional[ScenarioComparison]:
    """
    Get comparison data for all saved scenarios.
    
    This function retrieves all saved scenarios and creates a
    ScenarioComparison object for analysis. If no scenarios are saved,
    it returns None.
    
    Args:
        criterion: Metric to use for identifying best scenario
                  ("monthly_payment", "total_interest", "total_paid",
                   or "effective_annual_rate")
                   
    Returns:
        ScenarioComparison object if scenarios exist, None otherwise
        
    Example:
        >>> comparison = get_comparison_data("total_interest")
        >>> if comparison:
        ...     best = comparison.get_best_scenario()
        ...     st.write(f"Best option: {best.name}")
        ...     df = comparison.to_dataframe()
        ...     st.dataframe(df)
        ... else:
        ...     st.info("No scenarios saved yet")
    """
    repo = ScenarioRepository()
    scenarios = repo.get_all()
    
    if not scenarios:
        return None
    
    return ScenarioComparison(scenarios)


def get_all_scenarios() -> List[Scenario]:
    """
    Get all saved scenarios.
    
    This is a convenience function that wraps the repository's get_all method.
    
    Returns:
        List of all Scenario objects
        
    Example:
        >>> scenarios = get_all_scenarios()
        >>> for scenario in scenarios:
        ...     st.write(f"{scenario.name}: ${scenario.loan.metrics.monthly_payment}")
    """
    repo = ScenarioRepository()
    return repo.get_all()


def get_scenario_count() -> int:
    """
    Get the number of saved scenarios.
    
    This is a convenience function that wraps the repository's count method.
    
    Returns:
        Number of scenarios in the repository
        
    Example:
        >>> count = get_scenario_count()
        >>> st.sidebar.write(f"Saved scenarios: {count}")
    """
    repo = ScenarioRepository()
    return repo.count()


def scenario_exists(scenario_id: str) -> bool:
    """
    Check if a scenario with the given ID exists.
    
    This is a convenience function that wraps the repository's exists method.
    
    Args:
        scenario_id: Unique identifier to check
        
    Returns:
        True if scenario exists, False otherwise
        
    Example:
        >>> if scenario_exists("abc-123"):
        ...     st.write("Scenario found")
    """
    repo = ScenarioRepository()
    return repo.exists(scenario_id)
