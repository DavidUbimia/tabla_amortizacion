# Requirements Document

## Introduction

This document outlines the requirements for refactoring and enhancing an existing Python Streamlit loan amortization calculator application. The current application calculates loan payment schedules, amortization tables, and effective interest rates across four main pages. The refactoring aims to improve code organization, numerical stability, performance, user experience, and add valuable new features while maintaining all existing functionality.

## Glossary

- **Streamlit App**: The web application framework used to build the loan calculator interface
- **Amortization Table**: A detailed schedule showing the breakdown of each loan payment into principal and interest components
- **TAE (Tasa Anual Efectiva)**: Annual Effective Rate - the true annual interest rate accounting for compounding
- **Nominal Rate**: The stated annual interest rate without compounding adjustments
- **Monthly Rate**: The interest rate applied per monthly payment period
- **Principal**: The original loan amount borrowed
- **Payment Schedule**: The sequence of payments over the loan term
- **Sensitivity Analysis**: Analysis showing how changes in input parameters affect output metrics
- **Tornado Chart**: A visualization showing the relative impact of different variables on a target metric
- **Scenario Comparison**: Side-by-side comparison of different loan configurations
- **Numerical Stability**: The property of calculations remaining accurate despite floating-point arithmetic limitations

## Requirements

### Requirement 1

**User Story:** As a developer maintaining the application, I want well-organized modular code, so that I can easily understand, test, and extend the functionality.

#### Acceptance Criteria

1. WHEN the codebase is organized THEN the system SHALL separate business logic, UI components, and utility functions into distinct modules
2. WHEN functions are defined THEN the system SHALL include type hints for all parameters and return values
3. WHEN modules are created THEN the system SHALL follow a clear directory structure with separate folders for core logic, UI pages, and utilities
4. WHEN code is written THEN the system SHALL include docstrings following a consistent format for all public functions and classes
5. WHEN constants are used THEN the system SHALL define them in a centralized configuration module

### Requirement 2

**User Story:** As a user performing loan calculations, I want accurate and stable numerical results, so that I can trust the calculations for financial decision-making.

#### Acceptance Criteria

1. WHEN floating-point calculations are performed THEN the system SHALL use appropriate precision thresholds to handle rounding errors
2. WHEN the final payment is calculated THEN the system SHALL adjust it to eliminate residual balance errors
3. WHEN interest rates are computed iteratively THEN the system SHALL use numerically stable algorithms that converge reliably
4. WHEN division by zero conditions could occur THEN the system SHALL handle them gracefully with appropriate default values
5. WHEN monetary values are displayed THEN the system SHALL round consistently to the configured decimal places

### Requirement 3

**User Story:** As a user working with large loan datasets, I want fast calculation performance, so that I can analyze multiple scenarios without delays.

#### Acceptance Criteria

1. WHEN amortization tables are generated THEN the system SHALL compute them efficiently for loans up to 600 months
2. WHEN sensitivity analysis sweeps are performed THEN the system SHALL calculate results for at least 50 parameter variations within 5 seconds
3. WHEN dataframes are created THEN the system SHALL use vectorized operations where possible instead of row-by-row iteration
4. WHEN calculations are cached THEN the system SHALL store results in session state to avoid redundant computation
5. WHEN large tables are displayed THEN the system SHALL use pagination or lazy loading for tables exceeding 100 rows

### Requirement 4

**User Story:** As a user interacting with the application, I want an intuitive and responsive interface, so that I can efficiently perform loan analysis tasks.

#### Acceptance Criteria

1. WHEN forms are submitted THEN the system SHALL provide immediate visual feedback indicating processing status
2. WHEN errors occur THEN the system SHALL display clear, actionable error messages with suggestions for resolution
3. WHEN input validation fails THEN the system SHALL highlight the problematic fields and explain the constraints
4. WHEN results are displayed THEN the system SHALL organize them in logical sections with clear headings and visual hierarchy
5. WHEN the user navigates between pages THEN the system SHALL preserve relevant context and state information

### Requirement 5

**User Story:** As a user analyzing loan options, I want to export results in multiple formats, so that I can share and further analyze the data in other tools.

#### Acceptance Criteria

1. WHEN export buttons are clicked THEN the system SHALL generate files in CSV, Excel, and PDF formats
2. WHEN CSV files are exported THEN the system SHALL include headers and use UTF-8 encoding with BOM for international character support
3. WHEN Excel files are exported THEN the system SHALL include multiple sheets for raw data, formatted views, and summary metrics
4. WHEN PDF files are exported THEN the system SHALL include input parameters, results summary, and formatted tables with proper pagination
5. WHEN files are downloaded THEN the system SHALL use descriptive filenames including the report type and timestamp

### Requirement 6

**User Story:** As a user comparing multiple loan scenarios, I want to save and compare different configurations side-by-side, so that I can make informed borrowing decisions.

#### Acceptance Criteria

1. WHEN a scenario is saved THEN the system SHALL store all input parameters and calculated metrics in session state
2. WHEN multiple scenarios exist THEN the system SHALL display them in a comparison table with all key metrics
3. WHEN scenarios are compared THEN the system SHALL highlight the best option based on user-selected criteria
4. WHEN scenarios are managed THEN the system SHALL allow users to delete individual scenarios or clear all scenarios
5. WHEN the application is refreshed THEN the system SHALL persist saved scenarios using browser session storage

### Requirement 7

**User Story:** As a user performing sensitivity analysis, I want to visualize how parameter changes affect loan metrics, so that I can understand the relationships and risks.

#### Acceptance Criteria

1. WHEN sensitivity analysis is run THEN the system SHALL generate line charts showing metric changes across parameter ranges
2. WHEN tornado analysis is performed THEN the system SHALL display horizontal bar charts showing relative impact of each variable
3. WHEN charts are displayed THEN the system SHALL include axis labels, titles, and legends for clarity
4. WHEN multiple metrics are analyzed THEN the system SHALL allow users to select which metric to visualize
5. WHEN charts are interactive THEN the system SHALL support hover tooltips showing exact values

### Requirement 8

**User Story:** As a user with specific formatting preferences, I want to customize display settings, so that the application matches my regional and personal preferences.

#### Acceptance Criteria

1. WHEN currency symbols are configured THEN the system SHALL apply them consistently across all monetary displays
2. WHEN decimal precision is set THEN the system SHALL format all numbers according to the specified precision
3. WHEN formatting preferences are changed THEN the system SHALL update all displayed values immediately
4. WHEN the application is reopened THEN the system SHALL remember the user's formatting preferences
5. WHEN different pages are visited THEN the system SHALL maintain consistent formatting across all pages

### Requirement 9

**User Story:** As a user analyzing loan affordability, I want to calculate maximum loan amounts based on payment capacity, so that I can determine realistic borrowing limits.

#### Acceptance Criteria

1. WHEN maximum loan amount is requested THEN the system SHALL calculate the principal based on affordable monthly payment, interest rate, and term
2. WHEN payment capacity is specified THEN the system SHALL validate that it exceeds the minimum viable payment
3. WHEN loan limits are calculated THEN the system SHALL display the maximum borrowable amount with full amortization details
4. WHEN multiple payment capacities are tested THEN the system SHALL allow quick recalculation without re-entering all parameters
5. WHEN results are shown THEN the system SHALL include warnings if the calculated loan amount is unusually high or low

### Requirement 10

**User Story:** As a user evaluating early payment options, I want to simulate extra payments and payoff scenarios, so that I can understand the interest savings potential.

#### Acceptance Criteria

1. WHEN extra payments are specified THEN the system SHALL recalculate the amortization schedule with reduced term and interest
2. WHEN lump sum payments are added THEN the system SHALL show the impact on remaining balance and total interest
3. WHEN payment frequency changes THEN the system SHALL adjust the schedule for bi-weekly or weekly payments
4. WHEN early payoff is simulated THEN the system SHALL calculate the savings compared to the original schedule
5. WHEN multiple prepayment strategies are compared THEN the system SHALL display them side-by-side with savings metrics

### Requirement 11

**User Story:** As a user working with the application, I want helpful guidance and documentation, so that I can understand features and use them effectively.

#### Acceptance Criteria

1. WHEN help icons are clicked THEN the system SHALL display contextual tooltips explaining the feature or field
2. WHEN the help section is accessed THEN the system SHALL provide examples and use cases for each calculation type
3. WHEN errors occur THEN the system SHALL include links to relevant help documentation
4. WHEN new features are added THEN the system SHALL highlight them with brief introductory messages
5. WHEN formulas are used THEN the system SHALL provide an option to view the mathematical formulas and assumptions

### Requirement 12

**User Story:** As a user analyzing loans in different currencies, I want to handle multiple currencies and exchange rates, so that I can compare international loan options.

#### Acceptance Criteria

1. WHEN a currency is selected THEN the system SHALL apply the appropriate symbol and formatting conventions
2. WHEN exchange rates are provided THEN the system SHALL convert loan amounts and payments between currencies
3. WHEN multiple currencies are used THEN the system SHALL clearly label which currency each value represents
4. WHEN currency conversion is performed THEN the system SHALL display the exchange rate and conversion timestamp
5. WHEN results are exported THEN the system SHALL include currency information in all output formats
