# Design Document

## Overview

This design document outlines the refactoring and enhancement of a Streamlit-based loan amortization calculator. The refactoring will transform the current monolithic page structure into a well-organized, modular architecture while maintaining all existing functionality and adding valuable new features.

The design emphasizes:
- **Separation of concerns** through a layered architecture
- **Numerical stability** using proven financial calculation algorithms
- **Performance optimization** via caching and vectorization
- **Enhanced user experience** with better validation, feedback, and visualization
- **Extensibility** to easily add new features and calculation types

## Architecture

### High-Level Structure

```
loan-calculator/
├── main.py                          # Entry point, navigation setup
├── config/
│   ├── __init__.py
│   ├── settings.py                  # App-wide constants and defaults
│   └── formatting.py                # Currency, decimal formatting configs
├── core/
│   ├── __init__.py
│   ├── calculations.py              # Core financial calculations
│   ├── amortization.py              # Amortization table logic
│   ├── rate_solver.py               # Interest rate calculation
│   └── validators.py                # Input validation logic
├── models/
│   ├── __init__.py
│   ├── loan.py                      # Loan data model
│   └── scenario.py                  # Scenario comparison model
├── services/
│   ├── __init__.py
│   ├── export_service.py            # CSV, Excel, PDF export
│   ├── scenario_service.py          # Scenario management
│   └── analysis_service.py          # Sensitivity and tornado analysis
├── ui/
│   ├── __init__.py
│   ├── components/
│   │   ├── __init__.py
│   │   ├── forms.py                 # Reusable form components
│   │   ├── charts.py                # Chart generation
│   │   ├── tables.py                # Table display utilities
│   │   └── metrics.py               # Metric display components
│   └── pages/
│       ├── __init__.py
│       ├── tabla_amortizacion.py    # Amortization table page
│       ├── tasa_creditos.py         # Rate comparison page
│       ├── simulador.py             # Scenario simulator page
│       ├── sensibilidad.py          # Sensitivity analysis page
│       ├── capacidad_pago.py        # NEW: Payment capacity page
│       └── pago_anticipado.py       # NEW: Early payment page
├── utils/
│   ├── __init__.py
│   ├── session_state.py             # Session state management
│   ├── formatters.py                # Number/currency formatting
│   └── helpers.py                   # General utility functions
└── tests/
    ├── __init__.py
    ├── test_calculations.py
    ├── test_amortization.py
    ├── test_rate_solver.py
    └── test_validators.py
```

### Architectural Layers

1. **Presentation Layer** (`ui/`): Streamlit pages and reusable UI components
2. **Service Layer** (`services/`): Business logic orchestration and complex operations
3. **Core Layer** (`core/`): Pure financial calculation functions
4. **Model Layer** (`models/`): Data structures and domain objects
5. **Utility Layer** (`utils/`, `config/`): Cross-cutting concerns

### Design Patterns

- **Repository Pattern**: For scenario storage and retrieval
- **Service Pattern**: For complex business operations
- **Factory Pattern**: For creating different export formats
- **Strategy Pattern**: For different calculation methods (e.g., amortization types)

## Components and Interfaces

### Core Calculations Module (`core/calculations.py`)

```python
from typing import Optional
from decimal import Decimal

def calculate_monthly_payment(
    principal: Decimal,
    annual_rate: Decimal,
    num_payments: int
) -> Decimal:
    """
    Calculate monthly payment for a loan using the annuity formula.
    
    Args:
        principal: Loan amount
        annual_rate: Annual nominal interest rate (as decimal, e.g., 0.12 for 12%)
        num_payments: Total number of monthly payments
        
    Returns:
        Monthly payment amount
        
    Raises:
        ValueError: If inputs are invalid
    """
    pass

def calculate_total_interest(
    principal: Decimal,
    monthly_payment: Decimal,
    num_payments: int
) -> Decimal:
    """Calculate total interest paid over loan term."""
    pass

def calculate_effective_annual_rate(monthly_rate: Decimal) -> Decimal:
    """Convert monthly rate to effective annual rate (TAE)."""
    pass

def calculate_max_loan_amount(
    monthly_payment: Decimal,
    annual_rate: Decimal,
    num_payments: int
) -> Decimal:
    """Calculate maximum loan amount based on payment capacity."""
    pass
```

### Amortization Module (`core/amortization.py`)

```python
from typing import List, Dict
from decimal import Decimal
import pandas as pd

class AmortizationSchedule:
    """Represents a complete amortization schedule."""
    
    def __init__(
        self,
        principal: Decimal,
        annual_rate: Decimal,
        num_payments: int,
        monthly_payment: Decimal
    ):
        self.principal = principal
        self.annual_rate = annual_rate
        self.num_payments = num_payments
        self.monthly_payment = monthly_payment
        self._schedule: Optional[pd.DataFrame] = None
        
    def generate(self) -> pd.DataFrame:
        """Generate the complete amortization schedule."""
        pass
        
    def with_extra_payments(
        self,
        extra_payment_schedule: Dict[int, Decimal]
    ) -> 'AmortizationSchedule':
        """Create new schedule with extra payments applied."""
        pass
        
    def get_payoff_month(self) -> int:
        """Get the month when loan is fully paid off."""
        pass
        
    def get_total_interest(self) -> Decimal:
        """Get total interest paid over loan term."""
        pass
```

### Rate Solver Module (`core/rate_solver.py`)

```python
from typing import Optional
from decimal import Decimal

class RateSolver:
    """Solves for interest rate using numerical methods."""
    
    def __init__(
        self,
        precision: Decimal = Decimal('1e-10'),
        max_iterations: int = 200
    ):
        self.precision = precision
        self.max_iterations = max_iterations
        
    def solve_monthly_rate(
        self,
        principal: Decimal,
        monthly_payment: Decimal,
        num_payments: int
    ) -> Optional[Decimal]:
        """
        Solve for monthly interest rate using bisection method.
        
        Returns None if no valid rate exists.
        """
        pass
        
    def _present_value(
        self,
        payment: Decimal,
        rate: Decimal,
        periods: int
    ) -> Decimal:
        """Calculate present value of annuity."""
        pass
```

### Validators Module (`core/validators.py`)

```python
from typing import Tuple, Optional
from decimal import Decimal

class ValidationResult:
    """Result of input validation."""
    
    def __init__(self, is_valid: bool, error_message: Optional[str] = None):
        self.is_valid = is_valid
        self.error_message = error_message

def validate_loan_inputs(
    principal: Decimal,
    annual_rate: Decimal,
    num_payments: int
) -> ValidationResult:
    """Validate loan calculation inputs."""
    pass

def validate_payment_inputs(
    monthly_payment: Decimal,
    principal: Decimal,
    num_payments: int
) -> ValidationResult:
    """Validate that payment is sufficient to cover loan."""
    pass

def validate_rate_range(rate: Decimal) -> ValidationResult:
    """Validate that interest rate is within reasonable bounds."""
    pass
```

### Loan Model (`models/loan.py`)

```python
from dataclasses import dataclass
from decimal import Decimal
from typing import Optional
import pandas as pd

@dataclass
class LoanParameters:
    """Input parameters for a loan."""
    principal: Decimal
    annual_rate: Decimal
    num_payments: int
    name: Optional[str] = None
    
@dataclass
class LoanMetrics:
    """Calculated metrics for a loan."""
    monthly_payment: Decimal
    total_paid: Decimal
    total_interest: Decimal
    monthly_rate: Decimal
    effective_annual_rate: Decimal
    
class Loan:
    """Complete loan representation with parameters and calculations."""
    
    def __init__(self, parameters: LoanParameters):
        self.parameters = parameters
        self._metrics: Optional[LoanMetrics] = None
        self._schedule: Optional[pd.DataFrame] = None
        
    def calculate(self) -> 'Loan':
        """Perform all loan calculations."""
        pass
        
    @property
    def metrics(self) -> LoanMetrics:
        """Get calculated metrics (calculates if needed)."""
        pass
        
    @property
    def schedule(self) -> pd.DataFrame:
        """Get amortization schedule (generates if needed)."""
        pass
```

### Export Service (`services/export_service.py`)

```python
from typing import Protocol
from io import BytesIO
import pandas as pd

class ExportStrategy(Protocol):
    """Interface for export strategies."""
    
    def export(self, data: pd.DataFrame, metadata: dict) -> BytesIO:
        """Export data to specific format."""
        pass

class CSVExporter:
    """Export to CSV format."""
    
    def export(self, data: pd.DataFrame, metadata: dict) -> BytesIO:
        pass

class ExcelExporter:
    """Export to Excel with multiple sheets."""
    
    def export(self, data: pd.DataFrame, metadata: dict) -> BytesIO:
        pass

class PDFExporter:
    """Export to PDF with formatting."""
    
    def export(self, data: pd.DataFrame, metadata: dict) -> BytesIO:
        pass

class ExportService:
    """Manages export operations."""
    
    def __init__(self):
        self.exporters = {
            'csv': CSVExporter(),
            'excel': ExcelExporter(),
            'pdf': PDFExporter()
        }
        
    def export(
        self,
        format: str,
        data: pd.DataFrame,
        metadata: dict
    ) -> BytesIO:
        """Export data in specified format."""
        pass
```

### UI Components (`ui/components/`)

```python
# forms.py
import streamlit as st
from decimal import Decimal
from typing import Tuple

def loan_input_form(
    defaults: dict = None
) -> Tuple[Decimal, Decimal, int]:
    """Reusable loan input form component."""
    pass

def format_preferences_form(current_config: dict) -> dict:
    """Reusable formatting preferences form."""
    pass

# charts.py
import pandas as pd
import streamlit as st

def display_balance_chart(schedule: pd.DataFrame) -> None:
    """Display remaining balance line chart."""
    pass

def display_payment_breakdown_chart(schedule: pd.DataFrame) -> None:
    """Display stacked area chart of interest vs principal."""
    pass

def display_tornado_chart(
    sensitivity_data: pd.DataFrame,
    metric_name: str
) -> None:
    """Display tornado chart for sensitivity analysis."""
    pass

# metrics.py
def display_loan_metrics(
    monthly_payment: Decimal,
    total_paid: Decimal,
    total_interest: Decimal,
    annual_rate: Decimal
) -> None:
    """Display loan metrics in columns."""
    pass
```

## Data Models

### Loan Data Structure

```python
{
    "parameters": {
        "principal": Decimal,
        "annual_rate": Decimal,
        "num_payments": int,
        "name": str
    },
    "metrics": {
        "monthly_payment": Decimal,
        "total_paid": Decimal,
        "total_interest": Decimal,
        "monthly_rate": Decimal,
        "effective_annual_rate": Decimal
    },
    "schedule": pd.DataFrame  # Columns: Mes, Pago, Interés, Abono a capital, Saldo restante
}
```

### Scenario Comparison Structure

```python
{
    "scenarios": [
        {
            "id": str,
            "name": str,
            "loan": Loan,
            "created_at": datetime
        }
    ],
    "comparison_metrics": ["monthly_payment", "total_interest", "effective_annual_rate"]
}
```

### Sensitivity Analysis Structure

```python
{
    "base_loan": Loan,
    "variable": str,  # "principal", "annual_rate", or "num_payments"
    "range": {
        "min": Decimal,
        "max": Decimal,
        "step": Decimal
    },
    "results": pd.DataFrame  # Columns: Variable Value, Monthly Payment, Total Paid, Total Interest
}
```

## Correctness Properties

*A property is a characteristic or behavior that should hold true across all valid executions of a system-essentially, a formal statement about what the system should do. Properties serve as the bridge between human-readable specifications and machine-verifiable correctness guarantees.*

### Property 1: Numerical precision in calculations
*For any* valid loan parameters (principal, rate, term), when calculations are performed, the results should be within acceptable precision bounds (e.g., ±0.01 for monetary values).
**Validates: Requirements 2.1**

### Property 2: Zero final balance
*For any* generated amortization schedule, the final balance (after the last payment) should be exactly zero or within a negligible epsilon (< 0.01).
**Validates: Requirements 2.2**

### Property 3: Rate solver convergence
*For any* valid loan with payment > (principal / num_payments), the rate solver should converge to a valid monthly rate within the specified maximum iterations.
**Validates: Requirements 2.3**

### Property 4: Consistent rounding
*For any* monetary value and configured decimal precision, all formatted displays of that value should use the same rounding to the specified decimal places.
**Validates: Requirements 2.5**

### Property 5: Filename format consistency
*For any* export operation, the generated filename should match the pattern: `{report_type}_{timestamp}.{extension}` where timestamp is in ISO format.
**Validates: Requirements 5.5**

### Property 6: Scenario completeness
*For any* saved scenario, it should contain all required fields: name, principal, annual_rate, num_payments, monthly_payment, total_paid, total_interest, monthly_rate, and effective_annual_rate.
**Validates: Requirements 6.1**

### Property 7: Scenario comparison completeness
*For any* set of saved scenarios, the comparison table should include all scenarios with all key metrics (monthly_payment, total_interest, effective_annual_rate).
**Validates: Requirements 6.2**

### Property 8: Best scenario identification
*For any* set of scenarios and a selected criterion (e.g., lowest total_interest), the identified "best" scenario should have the minimum (or maximum, depending on criterion) value for that metric.
**Validates: Requirements 6.3**

### Property 9: Scenario deletion correctness
*For any* list of scenarios, after deleting a specific scenario, the remaining list should contain all other scenarios and not contain the deleted one.
**Validates: Requirements 6.4**

### Property 10: Currency symbol consistency
*For any* configured currency symbol, all monetary value displays throughout the application should use that exact symbol.
**Validates: Requirements 8.1**

### Property 11: Decimal precision consistency
*For any* configured decimal precision, all formatted numeric displays should show exactly that many decimal places.
**Validates: Requirements 8.2**

### Property 12: Loan capacity calculation round-trip
*For any* valid interest rate and term, if we calculate the maximum loan amount from a payment capacity P, then calculate the monthly payment for that loan amount, we should get back approximately P (within rounding error).
**Validates: Requirements 9.1**

### Property 13: Payment capacity validation
*For any* payment capacity that is less than or equal to zero, or less than the minimum viable payment (principal * monthly_rate), the validation should fail.
**Validates: Requirements 9.2**

### Property 14: Extra payment balance reduction
*For any* amortization schedule with extra payments, the balance after applying an extra payment should equal the balance before minus the extra payment amount.
**Validates: Requirements 10.1**

### Property 15: Lump sum payment impact
*For any* amortization schedule, when a lump sum payment L is applied at month M, the balance at month M should be reduced by exactly L (or to zero if L exceeds the balance).
**Validates: Requirements 10.2**

### Property 16: Payment frequency consistency
*For any* loan, the total amount paid should be approximately the same regardless of payment frequency (monthly, bi-weekly, weekly), accounting for the different number of payments and compounding.
**Validates: Requirements 10.3**

### Property 17: Early payoff savings calculation
*For any* two amortization schedules (original and with early payoff), the savings should equal the difference in total interest paid between the two schedules.
**Validates: Requirements 10.4**

### Property 18: Currency conversion round-trip
*For any* amount A in currency C1, if we convert to currency C2 using exchange rate R, then convert back to C1 using rate 1/R, we should get back approximately A (within rounding error).
**Validates: Requirements 12.2**

## Error Handling

### Input Validation Errors

1. **Invalid Principal**: Principal must be positive
   - Error: "Loan amount must be greater than zero"
   - Recovery: Prompt user to enter valid amount

2. **Invalid Interest Rate**: Rate must be between 0% and 200%
   - Error: "Interest rate must be between 0% and 200%"
   - Recovery: Suggest typical range (5-30%)

3. **Invalid Term**: Number of payments must be positive integer
   - Error: "Loan term must be at least 1 month"
   - Recovery: Suggest common terms (12, 24, 36, 60, 120 months)

4. **Insufficient Payment**: Payment must exceed interest-only payment
   - Error: "Monthly payment of ${payment} is insufficient to cover interest. Minimum required: ${min_payment}"
   - Recovery: Display minimum viable payment

### Calculation Errors

1. **Rate Solver Non-Convergence**: Rate solver fails to converge
   - Error: "Unable to calculate interest rate. Please verify that total payments exceed loan amount"
   - Recovery: Check input validity, suggest adjusting parameters

2. **Numerical Overflow**: Calculations exceed numeric limits
   - Error: "Calculation resulted in overflow. Please use smaller values"
   - Recovery: Suggest reducing principal or term

3. **Division by Zero**: Attempting division by zero
   - Error: "Invalid calculation parameters"
   - Recovery: Use safe defaults (e.g., zero rate → simple division)

### Export Errors

1. **Export Generation Failure**: Unable to create export file
   - Error: "Failed to generate {format} file: {reason}"
   - Recovery: Retry with different format, check data validity

2. **Large Dataset Warning**: Dataset too large for efficient export
   - Warning: "Exporting {rows} rows may take a moment"
   - Recovery: Offer to export subset or use pagination

### Session State Errors

1. **Missing State**: Required session state not found
   - Error: "Session data not found. Please recalculate"
   - Recovery: Redirect to input form

2. **Corrupted State**: Session state contains invalid data
   - Error: "Session data corrupted. Resetting to defaults"
   - Recovery: Clear corrupted state, reinitialize

## Testing Strategy

### Unit Testing

The application will use **pytest** as the testing framework with the following test organization:

#### Core Calculation Tests (`tests/test_calculations.py`)
- Test monthly payment calculation with known values
- Test edge cases: zero interest, very high interest, single payment
- Test total interest calculation accuracy
- Test effective annual rate conversion
- Test maximum loan amount calculation

#### Amortization Tests (`tests/test_amortization.py`)
- Test schedule generation for various loan terms
- Test final balance is zero
- Test sum of principal payments equals original principal
- Test sum of all payments equals total paid
- Test extra payment application
- Test early payoff scenarios

#### Rate Solver Tests (`tests/test_rate_solver.py`)
- Test convergence for valid inputs
- Test non-convergence detection for invalid inputs
- Test accuracy against known rate examples
- Test edge cases: zero rate, very high rate

#### Validator Tests (`tests/test_validators.py`)
- Test validation of valid inputs returns success
- Test validation of invalid inputs returns appropriate errors
- Test boundary conditions
- Test error message clarity

### Property-Based Testing

The application will use **Hypothesis** for property-based testing in Python. Each correctness property will be implemented as a property-based test.

**Configuration:**
- Minimum 100 test iterations per property
- Use Hypothesis strategies for generating valid loan parameters
- Custom strategies for realistic financial values (e.g., principals between $1,000 and $10,000,000)

**Property Test Examples:**

```python
from hypothesis import given, strategies as st
from decimal import Decimal

@given(
    principal=st.decimals(min_value=1000, max_value=10000000, places=2),
    annual_rate=st.decimals(min_value=0.01, max_value=0.50, places=4),
    num_payments=st.integers(min_value=6, max_value=600)
)
def test_property_zero_final_balance(principal, annual_rate, num_payments):
    """
    Property 2: Zero final balance
    Feature: loan-calculator-refactor, Property 2: Zero final balance
    """
    schedule = generate_amortization_schedule(principal, annual_rate, num_payments)
    final_balance = schedule.iloc[-1]['Saldo restante']
    assert abs(final_balance) < Decimal('0.01')

@given(
    monthly_payment=st.decimals(min_value=100, max_value=100000, places=2),
    annual_rate=st.decimals(min_value=0.01, max_value=0.50, places=4),
    num_payments=st.integers(min_value=6, max_value=600)
)
def test_property_loan_capacity_round_trip(monthly_payment, annual_rate, num_payments):
    """
    Property 12: Loan capacity calculation round-trip
    Feature: loan-calculator-refactor, Property 12: Loan capacity calculation round-trip
    """
    max_loan = calculate_max_loan_amount(monthly_payment, annual_rate, num_payments)
    calculated_payment = calculate_monthly_payment(max_loan, annual_rate, num_payments)
    assert abs(calculated_payment - monthly_payment) < Decimal('0.10')
```

### Integration Testing

- Test complete workflows: input → calculation → display → export
- Test navigation between pages with state preservation
- Test scenario save/load/delete operations
- Test export generation for all formats

### UI Testing

- Manual testing checklist for UI/UX requirements
- Visual regression testing for chart rendering
- Accessibility testing (WCAG compliance)
- Responsive design testing (different screen sizes)

### Performance Testing

- Benchmark amortization generation for 600-month loans
- Benchmark sensitivity analysis with 50+ variations
- Memory profiling for large datasets
- Load testing for concurrent users (if deployed)

## Implementation Notes

### Numerical Stability Considerations

1. **Use Decimal for Financial Calculations**: Python's `Decimal` type provides exact decimal arithmetic, avoiding floating-point errors
2. **Bisection Method for Rate Solving**: More stable than Newton-Raphson for this problem
3. **Final Payment Adjustment**: Always adjust the last payment to ensure zero balance
4. **Epsilon Comparisons**: Use small epsilon (1e-10) for rate convergence, larger (0.01) for monetary comparisons

### Performance Optimizations

1. **Vectorized Operations**: Use pandas vectorized operations for schedule generation
2. **Lazy Calculation**: Calculate metrics only when accessed (property pattern)
3. **Memoization**: Cache expensive calculations in session state
4. **Efficient Data Structures**: Use pandas DataFrames for tabular data

### Streamlit-Specific Patterns

1. **Session State Management**: Centralize session state access through utility functions
2. **Form Submission**: Use `st.form` to batch inputs and reduce reruns
3. **Caching**: Use `@st.cache_data` for pure functions with expensive computations
4. **Component Reusability**: Extract common UI patterns into reusable functions

### Migration Strategy

1. **Phase 1**: Refactor core calculations into new module structure
2. **Phase 2**: Update existing pages to use new core modules
3. **Phase 3**: Extract UI components into reusable functions
4. **Phase 4**: Add new features (payment capacity, early payment)
5. **Phase 5**: Enhance exports and add multi-currency support

### Backward Compatibility

- Maintain existing page URLs and navigation structure
- Preserve session state keys where possible
- Support legacy export formats
- Gradual migration of formatting preferences

