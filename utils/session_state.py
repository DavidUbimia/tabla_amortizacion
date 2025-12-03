"""
Session state management utilities for Streamlit.
Provides type-safe helpers for getting and setting session state values.
"""

from typing import Any, Optional, TypeVar, Generic, Dict
import streamlit as st

from config.settings import SESSION_KEYS
from config.formatting import FormattingPreferences

T = TypeVar('T')


class SessionStateManager:
    """
    Manager for Streamlit session state with type safety and initialization.
    """
    
    @staticmethod
    def initialize() -> None:
        """
        Initialize all required session state keys with default values.
        Should be called once at application startup.
        """
        # Amortization table data
        if SESSION_KEYS["tabla"] not in st.session_state:
            st.session_state[SESSION_KEYS["tabla"]] = None
        
        # Monthly payment value
        if SESSION_KEYS["pago"] not in st.session_state:
            st.session_state[SESSION_KEYS["pago"]] = None
        
        # Input parameters
        if SESSION_KEYS["inputs"] not in st.session_state:
            st.session_state[SESSION_KEYS["inputs"]] = {}
        
        # Formatting configuration
        if SESSION_KEYS["cfg"] not in st.session_state:
            st.session_state[SESSION_KEYS["cfg"]] = FormattingPreferences()
        
        # Credit comparison data
        if SESSION_KEYS["creditos"] not in st.session_state:
            st.session_state[SESSION_KEYS["creditos"]] = []
        
        # Saved scenarios
        if SESSION_KEYS["escenarios_guardados"] not in st.session_state:
            st.session_state[SESSION_KEYS["escenarios_guardados"]] = []
        
        # Simulator base scenario
        if SESSION_KEYS["sim_base"] not in st.session_state:
            st.session_state[SESSION_KEYS["sim_base"]] = None
        
        # Sensitivity analysis base
        if SESSION_KEYS["sens_base"] not in st.session_state:
            st.session_state[SESSION_KEYS["sens_base"]] = None
    
    @staticmethod
    def get(key: str, default: Optional[T] = None) -> Optional[T]:
        """
        Get a value from session state with optional default.
        
        Args:
            key: Session state key
            default: Default value if key doesn't exist
            
        Returns:
            Value from session state or default
            
        Examples:
            >>> cfg = SessionStateManager.get("cfg", FormattingPreferences())
            >>> tabla = SessionStateManager.get("tabla")
        """
        return st.session_state.get(key, default)
    
    @staticmethod
    def set(key: str, value: Any) -> None:
        """
        Set a value in session state.
        
        Args:
            key: Session state key
            value: Value to store
            
        Examples:
            >>> SessionStateManager.set("tabla", df)
            >>> SessionStateManager.set("pago", Decimal("856.07"))
        """
        st.session_state[key] = value
    
    @staticmethod
    def has(key: str) -> bool:
        """
        Check if a key exists in session state.
        
        Args:
            key: Session state key
            
        Returns:
            True if key exists, False otherwise
            
        Examples:
            >>> if SessionStateManager.has("tabla"):
            ...     tabla = SessionStateManager.get("tabla")
        """
        return key in st.session_state
    
    @staticmethod
    def delete(key: str) -> None:
        """
        Delete a key from session state.
        
        Args:
            key: Session state key to delete
            
        Examples:
            >>> SessionStateManager.delete("tabla")
        """
        if key in st.session_state:
            del st.session_state[key]
    
    @staticmethod
    def clear_all() -> None:
        """
        Clear all session state keys.
        Useful for resetting the application state.
        
        Examples:
            >>> SessionStateManager.clear_all()
        """
        for key in list(st.session_state.keys()):
            del st.session_state[key]
        # Reinitialize with defaults
        SessionStateManager.initialize()
    
    @staticmethod
    def get_formatting_preferences() -> FormattingPreferences:
        """
        Get current formatting preferences from session state.
        
        Returns:
            FormattingPreferences object
            
        Examples:
            >>> prefs = SessionStateManager.get_formatting_preferences()
            >>> symbol = prefs.currency_symbol
        """
        return SessionStateManager.get(
            SESSION_KEYS["cfg"],
            FormattingPreferences()
        )
    
    @staticmethod
    def set_formatting_preferences(prefs: FormattingPreferences) -> None:
        """
        Set formatting preferences in session state.
        
        Args:
            prefs: FormattingPreferences object
            
        Examples:
            >>> prefs = FormattingPreferences(currency_symbol="€", decimals_money=2)
            >>> SessionStateManager.set_formatting_preferences(prefs)
        """
        SessionStateManager.set(SESSION_KEYS["cfg"], prefs)
    
    @staticmethod
    def get_saved_scenarios() -> list:
        """
        Get list of saved scenarios from session state.
        
        Returns:
            List of saved scenarios
            
        Examples:
            >>> scenarios = SessionStateManager.get_saved_scenarios()
        """
        return SessionStateManager.get(
            SESSION_KEYS["escenarios_guardados"],
            []
        )
    
    @staticmethod
    def add_scenario(scenario: Any) -> None:
        """
        Add a scenario to the saved scenarios list.
        
        Args:
            scenario: Scenario object to add
            
        Examples:
            >>> SessionStateManager.add_scenario(my_scenario)
        """
        scenarios = SessionStateManager.get_saved_scenarios()
        scenarios.append(scenario)
        SessionStateManager.set(SESSION_KEYS["escenarios_guardados"], scenarios)
    
    @staticmethod
    def clear_scenarios() -> None:
        """
        Clear all saved scenarios.
        
        Examples:
            >>> SessionStateManager.clear_scenarios()
        """
        SessionStateManager.set(SESSION_KEYS["escenarios_guardados"], [])


# Convenience functions for common operations
def init_session_state() -> None:
    """Initialize session state. Convenience wrapper."""
    SessionStateManager.initialize()


def get_state(key: str, default: Optional[T] = None) -> Optional[T]:
    """Get value from session state. Convenience wrapper."""
    return SessionStateManager.get(key, default)


def set_state(key: str, value: Any) -> None:
    """Set value in session state. Convenience wrapper."""
    SessionStateManager.set(key, value)


def has_state(key: str) -> bool:
    """Check if key exists in session state. Convenience wrapper."""
    return SessionStateManager.has(key)
