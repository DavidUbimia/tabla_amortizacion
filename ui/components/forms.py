"""
Reusable form components for the loan calculator UI.

This module provides standardized form components that can be reused
across different pages, ensuring consistent user experience and
reducing code duplication.
"""

from decimal import Decimal
from typing import Tuple, Dict, Optional
import streamlit as st

from core.validators import (
    validate_loan_inputs,
    validate_payment_inputs,
    validate_payment_capacity,
    ValidationResult
)
from config.settings import (
    DEFAULT_PRINCIPAL,
    DEFAULT_ANNUAL_RATE,
    DEFAULT_NUM_PAYMENTS,
    MIN_PRINCIPAL,
    MAX_PRINCIPAL,
    MIN_ANNUAL_RATE,
    MAX_ANNUAL_RATE,
    MIN_NUM_PAYMENTS,
    MAX_NUM_PAYMENTS,
    SUPPORTED_CURRENCIES,
    DEFAULT_CURRENCY_SYMBOL,
    DEFAULT_DECIMAL_PLACES_MONEY,
    DEFAULT_DECIMAL_PLACES_PERCENT
)


def loan_input_form(
    defaults: Optional[Dict] = None,
    form_key: str = "loan_form"
) -> Tuple[Optional[Decimal], Optional[Decimal], Optional[int]]:
    """
    Reusable loan input form component.
    
    Displays a standardized form for entering loan parameters with
    validation and error handling. Returns None values if form is
    not submitted or validation fails.
    
    Args:
        defaults: Dictionary with default values for 'principal', 'annual_rate', 'num_payments'
        form_key: Unique key for the form (required if multiple forms on same page)
        
    Returns:
        Tuple of (principal, annual_rate, num_payments) if form is valid and submitted,
        (None, None, None) otherwise
        
    Example:
        >>> principal, rate, payments = loan_input_form()
        >>> if principal is not None:
        ...     # Process the loan
        ...     loan = Loan(LoanParameters(principal, rate, payments))
    """
    # Set defaults
    if defaults is None:
        defaults = {
            "principal": float(DEFAULT_PRINCIPAL),
            "annual_rate": float(DEFAULT_ANNUAL_RATE),
            "num_payments": DEFAULT_NUM_PAYMENTS
        }
    
    with st.form(form_key, border=True):
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            annual_rate_input = st.number_input(
                "Tasa de interés anual (% nominal)",
                min_value=float(MIN_ANNUAL_RATE),
                max_value=float(MAX_ANNUAL_RATE),
                step=0.1,
                value=defaults.get("annual_rate", float(DEFAULT_ANNUAL_RATE)),
                format="%.2f",
                help="Tasa nominal anual. La frecuencia de pagos se asume mensual.",
            )
        
        with col2:
            principal_input = st.number_input(
                "Monto del crédito",
                min_value=float(MIN_PRINCIPAL),
                max_value=float(MAX_PRINCIPAL),
                step=100.0,
                value=defaults.get("principal", float(DEFAULT_PRINCIPAL)),
                format="%.2f",
                help="Monto total del préstamo o crédito."
            )
        
        with col3:
            num_payments_input = st.number_input(
                "Número de pagos (meses)",
                min_value=MIN_NUM_PAYMENTS,
                max_value=MAX_NUM_PAYMENTS,
                step=12,
                value=defaults.get("num_payments", DEFAULT_NUM_PAYMENTS),
                help="Plazo en meses (por ejemplo, 12, 24, 36...).",
            )
        
        submitted = st.form_submit_button(
            "Calcular",
            use_container_width=True,
            type="primary"
        )
    
    if submitted:
        # Convert to Decimal for validation
        principal = Decimal(str(principal_input))
        annual_rate = Decimal(str(annual_rate_input)) / Decimal('100')  # Convert percentage to decimal
        num_payments = int(num_payments_input)
        
        # Validate inputs
        validation = validate_loan_inputs(principal, annual_rate, num_payments)
        
        if validation.is_valid:
            return principal, annual_rate, num_payments
        else:
            st.error(f"❌ {validation.error_message}")
            return None, None, None
    
    return None, None, None


def format_preferences_form(
    current_config: Optional[Dict] = None
) -> Dict:
    """
    Reusable formatting preferences form.
    
    Displays a form for configuring display formatting preferences
    such as currency symbol and decimal precision. Updates are
    applied immediately.
    
    Args:
        current_config: Dictionary with current settings for 'currency_symbol',
                       'decimals_money', 'decimals_percent'
                       
    Returns:
        Dictionary with updated configuration
        
    Example:
        >>> config = format_preferences_form(st.session_state.cfg)
        >>> st.session_state.cfg = config
    """
    if current_config is None:
        current_config = {
            "currency_symbol": DEFAULT_CURRENCY_SYMBOL,
            "decimals_money": DEFAULT_DECIMAL_PLACES_MONEY,
            "decimals_percent": DEFAULT_DECIMAL_PLACES_PERCENT
        }
    
    st.subheader("Preferencias de formato")
    
    col1, col2, col3 = st.columns(3)
    
    with col1:
        currency_symbol = st.selectbox(
            "Símbolo de moneda",
            options=SUPPORTED_CURRENCIES,
            index=SUPPORTED_CURRENCIES.index(current_config.get("currency_symbol", DEFAULT_CURRENCY_SYMBOL))
            if current_config.get("currency_symbol") in SUPPORTED_CURRENCIES else 0,
            help="Sólo afecta presentación (no el cálculo)."
        )
    
    with col2:
        decimals_money = st.number_input(
            "Decimales para moneda",
            min_value=0,
            max_value=4,
            value=current_config.get("decimals_money", DEFAULT_DECIMAL_PLACES_MONEY),
            step=1,
            help="Número de decimales para valores monetarios."
        )
    
    with col3:
        decimals_percent = st.number_input(
            "Decimales para porcentajes",
            min_value=0,
            max_value=4,
            value=current_config.get("decimals_percent", DEFAULT_DECIMAL_PLACES_PERCENT),
            step=1,
            help="Número de decimales para tasas y porcentajes."
        )
    
    # Check if any changes were made
    config_changed = (
        currency_symbol != current_config.get("currency_symbol") or
        decimals_money != current_config.get("decimals_money") or
        decimals_percent != current_config.get("decimals_percent")
    )
    
    if config_changed:
        st.success("✅ Formato actualizado.")
    
    return {
        "currency_symbol": currency_symbol,
        "decimals_money": int(decimals_money),
        "decimals_percent": int(decimals_percent)
    }


def scenario_save_form(
    form_key: str = "save_scenario_form"
) -> Optional[str]:
    """
    Reusable scenario save form.
    
    Displays a simple form for saving a loan scenario with a
    descriptive name. Returns the scenario name if submitted,
    None otherwise.
    
    Args:
        form_key: Unique key for the form
        
    Returns:
        Scenario name if form is submitted and valid, None otherwise
        
    Example:
        >>> scenario_name = scenario_save_form()
        >>> if scenario_name:
        ...     # Save the scenario
        ...     scenario_service.save_scenario(scenario_name, loan)
    """
    with st.form(form_key, border=True):
        st.markdown("**Guardar escenario**")
        
        scenario_name = st.text_input(
            "Nombre del escenario",
            placeholder="Ej: Banco A - 30 años",
            help="Ingresa un nombre descriptivo para identificar este escenario."
        )
        
        col1, col2 = st.columns([1, 1])
        with col1:
            submitted = st.form_submit_button(
                "💾 Guardar",
                use_container_width=True,
                type="primary"
            )
        with col2:
            cancel = st.form_submit_button(
                "Cancelar",
                use_container_width=True
            )
    
    if submitted:
        if scenario_name and scenario_name.strip():
            return scenario_name.strip()
        else:
            st.error("❌ Por favor ingresa un nombre para el escenario.")
            return None
    
    return None


def payment_capacity_form(
    defaults: Optional[Dict] = None,
    form_key: str = "payment_capacity_form"
) -> Tuple[Optional[Decimal], Optional[Decimal], Optional[int]]:
    """
    Form for payment capacity calculator.
    
    Similar to loan_input_form but focused on calculating maximum
    loan amount from payment capacity.
    
    Args:
        defaults: Dictionary with default values for 'monthly_payment', 'annual_rate', 'num_payments'
        form_key: Unique key for the form
        
    Returns:
        Tuple of (monthly_payment, annual_rate, num_payments) if valid and submitted,
        (None, None, None) otherwise
    """
    if defaults is None:
        defaults = {
            "monthly_payment": 1000.0,
            "annual_rate": float(DEFAULT_ANNUAL_RATE),
            "num_payments": DEFAULT_NUM_PAYMENTS
        }
    
    with st.form(form_key, border=True):
        col1, col2, col3 = st.columns([1, 1, 1])
        
        with col1:
            monthly_payment_input = st.number_input(
                "Capacidad de pago mensual",
                min_value=1.0,
                max_value=1000000.0,
                step=100.0,
                value=defaults.get("monthly_payment", 1000.0),
                format="%.2f",
                help="Monto máximo que puedes pagar mensualmente."
            )
        
        with col2:
            annual_rate_input = st.number_input(
                "Tasa de interés anual (% nominal)",
                min_value=float(MIN_ANNUAL_RATE),
                max_value=float(MAX_ANNUAL_RATE),
                step=0.1,
                value=defaults.get("annual_rate", float(DEFAULT_ANNUAL_RATE)),
                format="%.2f",
                help="Tasa nominal anual esperada."
            )
        
        with col3:
            num_payments_input = st.number_input(
                "Número de pagos (meses)",
                min_value=MIN_NUM_PAYMENTS,
                max_value=MAX_NUM_PAYMENTS,
                step=12,
                value=defaults.get("num_payments", DEFAULT_NUM_PAYMENTS),
                help="Plazo deseado en meses."
            )
        
        submitted = st.form_submit_button(
            "Calcular monto máximo",
            use_container_width=True,
            type="primary"
        )
    
    if submitted:
        # Convert to Decimal
        monthly_payment = Decimal(str(monthly_payment_input))
        annual_rate = Decimal(str(annual_rate_input)) / Decimal('100')
        num_payments = int(num_payments_input)
        
        # Validate
        validation = validate_payment_capacity(monthly_payment, annual_rate, num_payments)
        
        if validation.is_valid:
            return monthly_payment, annual_rate, num_payments
        else:
            st.error(f"❌ {validation.error_message}")
            return None, None, None
    
    return None, None, None


def display_validation_error(validation: ValidationResult) -> None:
    """
    Display validation error message in a consistent format.
    
    Args:
        validation: ValidationResult object with error information
    """
    if not validation.is_valid and validation.error_message:
        st.error(f"❌ {validation.error_message}")
