# Implementation Plan

## Current State Analysis

The existing codebase is a **working Streamlit loan calculator** with:
- ✅ 4 functional pages: tabla_amortizacion.py, tasa_creditos.py, simulador.py, sensibilidad.py
- ✅ Core calculations in functions.py (monthly payment, amortization table, rate solver)
- ✅ Export functionality (CSV, Excel, PDF) implemented in each page
- ✅ Working UI with forms, charts, and formatting preferences
- ✅ Session state management for scenarios and preferences

**Refactoring Goals:**
- Reorganize monolithic code into modular architecture (config/, core/, models/, services/, ui/, utils/, tests/)
- Improve numerical stability using Decimal type
- Extract reusable UI components
- Add new features: payment capacity calculator and early payment simulator
- Implement property-based testing for correctness validation
- Add multi-currency support

## Phase 1: Foundation and Core Logic

- [x] 1. Set up project structure and configuration



  - Create new directory structure (config/, core/, models/, services/, ui/, utils/, tests/)
  - Create __init__.py files for all packages
  - Set up configuration module with constants and defaults
  - Update requirements.txt with new dependencies (pytest, hypothesis)
  - _Requirements: 1.1, 1.3, 1.5_

- [x] 2. Implement core calculation modules




  - [x] 2.1 Create core/calculations.py with type-hinted functions


    - Migrate calculate_monthly_payment() from functions.py using Decimal for precision
    - Implement calculate_total_interest()
    - Implement calculate_effective_annual_rate()
    - Implement calculate_max_loan_amount() (inverse calculation)
    - Add comprehensive docstrings and type hints
    - _Requirements: 2.1, 9.1_

  - [ ]* 2.2 Write property test for monthly payment calculation
    - **Property 1: Numerical precision in calculations**
    - **Validates: Requirements 2.1**

  - [ ]* 2.3 Write property test for loan capacity round-trip
    - **Property 12: Loan capacity calculation round-trip**
    - **Validates: Requirements 9.1**

- [x] 3. Implement amortization module




  - [x] 3.1 Create core/amortization.py with AmortizationSchedule class


    - Migrate tabla_amortizacion() logic from functions.py into AmortizationSchedule class
    - Use Decimal for all monetary calculations
    - Implement schedule generation with proper balance tracking
    - Implement final payment adjustment for zero balance (already exists in functions.py)
    - Implement with_extra_payments() method for early payment scenarios
    - Implement helper methods (get_payoff_month, get_total_interest)
    - _Requirements: 2.2, 10.1, 10.2_

  - [ ]* 3.2 Write property test for zero final balance
    - **Property 2: Zero final balance**
    - **Validates: Requirements 2.2**

  - [ ]* 3.3 Write property test for extra payment balance reduction
    - **Property 14: Extra payment balance reduction**
    - **Validates: Requirements 10.1**

  - [ ]* 3.4 Write property test for lump sum payment impact
    - **Property 15: Lump sum payment impact**
    - **Validates: Requirements 10.2**

- [x] 4. Implement rate solver module




  - [x] 4.1 Create core/rate_solver.py with RateSolver class


    - Migrate calcular_tasa() and _pv_anualidad() from functions.py
    - Refactor into RateSolver class with configurable precision and max_iterations
    - Use Decimal for numerical stability
    - Implement bisection method for rate calculation (already working in functions.py)
    - Implement present value calculation helper
    - Add convergence checking and iteration limits
    - Handle edge cases (zero rate, non-convergent scenarios)
    - _Requirements: 2.3, 2.4_

  - [ ]* 4.2 Write property test for rate solver convergence
    - **Property 3: Rate solver convergence**
    - **Validates: Requirements 2.3**


- [x] 5. Implement validators module



  - [x] 5.1 Create core/validators.py with validation functions


    - Implement ValidationResult class
    - Implement validate_loan_inputs()
    - Implement validate_payment_inputs()
    - Implement validate_rate_range()
    - Implement validate_payment_capacity()
    - _Requirements: 9.2_

  - [ ]* 5.2 Write property test for payment capacity validation
    - **Property 13: Payment capacity validation**
    - **Validates: Requirements 9.2**

- [x] 6. Implement data models



  - [x] 6.1 Create models/loan.py with Loan and related classes


    - Implement LoanParameters dataclass
    - Implement LoanMetrics dataclass
    - Implement Loan class with lazy calculation
    - Add calculate() method integrating core modules
    - _Requirements: 6.1_

  - [x] 6.2 Create models/scenario.py for scenario management


    - Implement Scenario dataclass
    - Implement ScenarioComparison class
    - Add comparison and best-scenario identification logic
    - _Requirements: 6.2, 6.3_

  - [ ]* 6.3 Write property test for scenario completeness
    - **Property 6: Scenario completeness**
    - **Validates: Requirements 6.1**

  - [ ]* 6.4 Write property test for scenario comparison completeness
    - **Property 7: Scenario comparison completeness**
    - **Validates: Requirements 6.2**

  - [ ]* 6.5 Write property test for best scenario identification
    - **Property 8: Best scenario identification**
    - **Validates: Requirements 6.3**

- [x] 7. Checkpoint - Core modules complete




  - Verify all core modules (calculations, amortization, rate_solver, validators) are working
  - Run any implemented property-based tests
  - Ensure all tests pass, ask the user if questions arise

## Phase 2: Services and Models

- [x] 8. Implement export service




  - [x] 8.1 Create services/export_service.py with export strategies


    - Migrate generar_pdf_tabla() from functions.py into PDFExporter
    - Implement ExportStrategy protocol
    - Implement CSVExporter with UTF-8 BOM encoding (already working in pages)
    - Implement ExcelExporter with multiple sheets (already working in pages)
    - Implement PDFExporter with formatting (migrate from functions.py)
    - Implement ExportService orchestrator
    - _Requirements: 5.1, 5.2, 5.3, 5.4, 5.5_

  - [ ]* 8.2 Write property test for filename format consistency
    - **Property 5: Filename format consistency**
    - **Validates: Requirements 5.5**

- [x] 9. Implement scenario service




  - [x] 9.1 Create services/scenario_service.py


    - Implement ScenarioRepository for CRUD operations
    - Implement save_scenario()
    - Implement delete_scenario()
    - Implement clear_all_scenarios()
    - Implement get_comparison_data()
    - _Requirements: 6.1, 6.4_

  - [ ]* 9.2 Write property test for scenario deletion correctness
    - **Property 9: Scenario deletion correctness**
    - **Validates: Requirements 6.4**

- [x] 10. Implement analysis service




  - [x] 10.1 Create services/analysis_service.py


    - Implement sensitivity_analysis() for parameter sweeps
    - Implement tornado_analysis() for impact comparison
    - Implement early_payoff_analysis()
    - Implement payment_frequency_comparison()
    - _Requirements: 10.3, 10.4_

  - [ ]* 10.2 Write property test for payment frequency consistency
    - **Property 16: Payment frequency consistency**
    - **Validates: Requirements 10.3**

  - [ ]* 10.3 Write property test for early payoff savings calculation
    - **Property 17: Early payoff savings calculation**
    - **Validates: Requirements 10.4**

- [x] 11. Implement utility modules





  - [x] 11.1 Create utils/formatters.py


    - Migrate style_amort() from functions.py (used for pandas Styler formatting)
    - Implement format_currency() with symbol and precision
    - Implement format_percentage()
    - Implement format_number()
    - Ensure consistent rounding
    - _Requirements: 2.5, 8.1, 8.2_

  - [ ]* 11.2 Write property test for consistent rounding
    - **Property 4: Consistent rounding**
    - **Validates: Requirements 2.5**

  - [ ]* 11.3 Write property test for currency symbol consistency
    - **Property 10: Currency symbol consistency**
    - **Validates: Requirements 8.1**

  - [ ]* 11.4 Write property test for decimal precision consistency
    - **Property 11: Decimal precision consistency**
    - **Validates: Requirements 8.2**

  - [x] 11.5 Create utils/session_state.py


    - Implement session state initialization
    - Implement get/set helpers with type safety
    - Implement state persistence utilities
    - _Requirements: 4.5_

  - [x] 11.6 Create utils/helpers.py


    - Implement common utility functions
    - Implement date/time formatting
    - Implement data transformation helpers
    - _Requirements: 5.5_

- [x] 12. Checkpoint - Services and utilities complete




  - Verify all services (export, scenario, analysis) and utilities are working
  - Test integration between models and services
  - Ensure all tests pass, ask the user if questions arise

- [x] 13. Implement UI components





  - [x] 13.1 Create ui/components/forms.py


    - Implement loan_input_form() reusable component
    - Implement format_preferences_form()
    - Implement scenario_save_form()
    - Add input validation and error display
    - _Requirements: 4.2, 4.3_

  - [x] 13.2 Create ui/components/charts.py


    - Implement display_balance_chart()
    - Implement display_payment_breakdown_chart()
    - Implement display_tornado_chart()
    - Implement display_sensitivity_chart()
    - Add axis labels, titles, and legends
    - _Requirements: 7.1, 7.2, 7.3_

  - [x] 13.3 Create ui/components/tables.py


    - Implement display_amortization_table()
    - Implement display_scenario_comparison()
    - Implement display_sensitivity_results()
    - Add formatting and styling
    - _Requirements: 4.4_

  - [x] 13.4 Create ui/components/metrics.py


    - Implement display_loan_metrics()
    - Implement display_comparison_metrics()
    - Use st.metric with proper formatting
    - _Requirements: 4.4_

## Phase 3: UI Refactoring

- [x] 14. Refactor existing pages to use new modules





  - [x] 14.1 Refactor tabla_amortizacion.py to ui/pages/


    - Move tabla_amortizacion.py to ui/pages/ directory
    - Replace functions.py calls with core modules (calculations, amortization)
    - Use new UI components from ui/components/
    - Use new export service
    - Maintain all existing functionality (forms, charts, downloads, formatting)
    - _Requirements: 1.1, 4.4_

  - [x] 14.2 Refactor tasa_creditos.py to ui/pages/


    - Move tasa_creditos.py to ui/pages/ directory
    - Replace calcular_tasa() with RateSolver from core
    - Use new UI components
    - Use new export service
    - Maintain all existing functionality (credit comparison, charts, downloads)
    - _Requirements: 1.1, 4.4_

  - [x] 14.3 Refactor simulador.py to ui/pages/


    - Move simulador.py to ui/pages/ directory
    - Use Loan model and scenario service
    - Use new UI components
    - Use analysis service for parameter sweeps
    - Maintain all existing functionality (base scenario, sweeps, scenario comparison)
    - _Requirements: 1.1, 4.4_

  - [x] 14.4 Refactor sensibilidad.py to ui/pages/


    - Move sensibilidad.py to ui/pages/ directory
    - Use analysis service for sensitivity and tornado analysis
    - Use new UI components
    - Use new export service
    - Maintain all existing functionality (local sensitivity, tornado charts)
    - _Requirements: 1.1, 4.4_

- [x] 15. Checkpoint - UI refactoring complete





  - Verify all 4 existing pages work with new modular architecture
  - Test navigation and state preservation
  - Verify all export formats still work correctly
  - Remove old functions.py file (all functionality migrated to core/, services/, utils/)
  - Ensure all tests pass, ask the user if questions arise

## Phase 4: New Features

- [ ] 16. Implement new feature: Payment capacity calculator
  - [ ] 16.1 Create ui/pages/capacidad_pago.py
    - Implement input form for payment capacity, rate, and term
    - Use calculate_max_loan_amount() from core
    - Display maximum loan amount and full amortization
    - Add warnings for unusual amounts
    - Add export functionality using export service
    - _Requirements: 9.1, 9.2, 9.3, 9.5_

- [ ] 17. Implement new feature: Early payment simulator
  - [ ] 17.1 Create ui/pages/pago_anticipado.py
    - Implement input form for base loan and extra payment scenarios
    - Use AmortizationSchedule.with_extra_payments()
    - Display comparison of original vs. early payoff schedules
    - Show savings calculation
    - Add payment frequency comparison
    - Add export functionality
    - _Requirements: 10.1, 10.2, 10.3, 10.4, 10.5_

- [ ] 18. Implement multi-currency support
  - [ ] 18.1 Add currency configuration to config/settings.py
    - Define supported currencies with symbols and formatting
    - Add exchange rate configuration
    - _Requirements: 12.1_

  - [ ] 18.2 Extend formatters for currency conversion
    - Implement convert_currency() in utils/formatters.py
    - Add currency labeling helpers
    - _Requirements: 12.2, 12.3_

  - [ ]* 18.3 Write property test for currency conversion round-trip
    - **Property 18: Currency conversion round-trip**
    - **Validates: Requirements 12.2**

  - [ ] 18.4 Add currency selection to UI
    - Add currency selector to format preferences
    - Add exchange rate input where needed
    - Update export services to include currency info
    - _Requirements: 12.1, 12.4, 12.5_

- [ ] 19. Update main.py navigation
  - [ ] 19.1 Update navigation to reference new page locations
    - Update page paths to ui/pages/ directory structure
    - Add "Capacidad de pago" to Básicos section
    - Add "Pago anticipado" to Avanzados section
    - Update help popover with new features
    - _Requirements: 4.5_

- [ ] 20. Enhance error handling and user feedback
  - [ ] 20.1 Add loading spinners and progress indicators
    - Use st.spinner for long calculations
    - Add progress bars for batch operations
    - _Requirements: 4.1_

  - [ ] 20.2 Improve error messages
    - Use validators for all inputs
    - Display clear error messages with st.error
    - Add suggestions for resolution
    - _Requirements: 4.2, 4.3_

- [ ] 21. Add help and documentation
  - [ ] 21.1 Create help content
    - Add contextual help tooltips to all inputs
    - Create help section with examples
    - Add formula explanations
    - _Requirements: 11.1, 11.2, 11.5_

  - [ ] 21.2 Add feature highlights
    - Add introductory messages for new features
    - Add "What's New" section to sidebar
    - _Requirements: 11.4_

- [ ] 22. Performance optimization
  - [ ] 22.1 Add caching to expensive operations
    - Use @st.cache_data for pure calculation functions
    - Cache amortization schedules in session state
    - _Requirements: 3.4_

  - [ ] 22.2 Optimize large table display
    - Add pagination for tables > 100 rows
    - Use st.dataframe with height limit
    - _Requirements: 3.5_

- [ ] 23. Final checkpoint - All features complete
  - Verify all 6 pages work correctly (4 refactored + 2 new)
  - Test all new features (payment capacity, early payment, multi-currency)
  - Verify performance optimizations are working
  - Run full test suite
  - Ensure all tests pass, ask the user if questions arise

## Phase 5: Documentation and Polish

- [ ] 24. Update documentation
  - [ ] 24.1 Update README.md
    - Document new architecture
    - Add feature list
    - Add installation and usage instructions
    - _Requirements: 11.2_

  - [ ] 24.2 Add inline documentation
    - Ensure all functions have docstrings
    - Add module-level documentation
    - Add type hints to all functions
    - _Requirements: 1.2, 1.4_

- [ ] 25. Final testing and validation
  - [ ]* 25.1 Run full test suite
    - Run all unit tests
    - Run all property-based tests
    - Verify all properties pass with 100+ iterations

  - [ ]* 25.2 Perform integration testing
    - Test all page workflows
    - Test navigation and state preservation
    - Test all export formats

  - [ ]* 25.3 Perform manual UI testing
    - Test responsive design
    - Test accessibility
    - Test error scenarios
    - Verify formatting consistency across pages
