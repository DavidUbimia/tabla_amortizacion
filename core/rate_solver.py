"""
Interest rate solver using numerical methods.

This module provides the RateSolver class for calculating interest rates
from loan parameters using the bisection method. This is the inverse problem
of calculating monthly payments - given the principal, payment, and term,
solve for the interest rate.

The bisection method is chosen for its numerical stability and guaranteed
convergence (when a solution exists), making it more reliable than methods
like Newton-Raphson for this financial application.

All calculations use Python's Decimal type for numerical precision.
"""

from decimal import Decimal, ROUND_HALF_UP
from typing import Optional


class RateSolver:
    """
    Solves for interest rate using the bisection method.
    
    This class implements a numerically stable algorithm to find the monthly
    interest rate that equates the present value of an annuity to the loan
    principal. It uses bisection search with automatic interval expansion.
    
    The solver finds the rate r such that:
    PV(r) = payment * [1 - (1+r)^(-n)] / r = principal
    
    Attributes:
        precision: Convergence threshold for the solution
        max_iterations: Maximum number of bisection iterations
    """
    
    def __init__(
        self,
        precision: Decimal = Decimal('1e-10'),
        max_iterations: int = 200
    ):
        """
        Initialize a RateSolver with specified precision and iteration limits.
        
        Args:
            precision: Convergence threshold (default: 1e-10)
            max_iterations: Maximum bisection iterations (default: 200)
        """
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
        
        This method finds the monthly interest rate that makes the present
        value of the payment stream equal to the principal amount.
        
        The algorithm:
        1. Check for special cases (zero rate, insufficient payments)
        2. Establish initial search interval [lo, hi]
        3. Expand hi until PV(hi) < principal (bracketing)
        4. Perform bisection until convergence
        
        Args:
            principal: Loan amount (must be positive)
            monthly_payment: Monthly payment amount (must be positive)
            num_payments: Number of monthly payments (must be positive)
            
        Returns:
            Monthly interest rate as decimal (e.g., 0.01 for 1% monthly),
            or None if no valid rate exists
            
        Examples:
            >>> solver = RateSolver()
            >>> solver.solve_monthly_rate(
            ...     Decimal('100000'),
            ...     Decimal('1028.61'),
            ...     360
            ... )
            Decimal('0.01')  # 1% monthly rate
            
        Notes:
            - Returns None if total payments < principal (no positive rate exists)
            - Returns 0 if total payments = principal (zero interest)
            - Requires payment * num_payments > principal for positive rate
        """
        # Validate inputs
        if principal <= 0 or monthly_payment <= 0 or num_payments <= 0:
            return None
        
        # Calculate total payments without interest
        total_without_interest = monthly_payment * Decimal(num_payments)
        
        # Special case: zero interest rate
        # If total payments equal principal, rate is exactly zero
        if abs(total_without_interest - principal) < Decimal('1e-12'):
            return Decimal('0')
        
        # If total payments < principal, no positive rate can satisfy the equation
        if total_without_interest < principal:
            return None
        
        # Initialize bisection search interval
        # Start with [0, 0.01] (0% to 1% monthly)
        lo = Decimal('0')
        hi = Decimal('0.01')
        
        # Calculate present values at boundaries
        pv_lo = self._present_value(monthly_payment, lo, num_payments)
        pv_hi = self._present_value(monthly_payment, hi, num_payments)
        
        # Expand hi until PV(hi) <= principal (bracketing phase)
        # PV is monotonically decreasing in rate, so we need PV(hi) < principal
        # Limit: 10.0 = 1000% monthly rate (unreasonably high)
        while pv_hi > principal and hi < Decimal('10.0'):
            hi *= Decimal('2')
            pv_hi = self._present_value(monthly_payment, hi, num_payments)
        
        # If even with very high rate PV > principal, something is inconsistent
        if pv_hi > principal:
            return None
        
        # Bisection iteration
        for iteration in range(self.max_iterations):
            # Calculate midpoint
            mid = (lo + hi) / Decimal('2')
            pv_mid = self._present_value(monthly_payment, mid, num_payments)
            
            # Check convergence by present value difference
            pv_error = abs(pv_mid - principal)
            tolerance = max(self.precision * max(principal, Decimal('1')), Decimal('1e-12'))
            
            if pv_error <= tolerance:
                # Converged successfully
                return mid.quantize(Decimal('0.0000000001'), rounding=ROUND_HALF_UP)
            
            # Update search interval
            # PV is decreasing in rate, so:
            # - If PV(mid) > principal, we need higher rate (move lo up)
            # - If PV(mid) < principal, we need lower rate (move hi down)
            if pv_mid > principal:
                lo = mid
            else:
                hi = mid
            
            # Check if interval is too small (alternative convergence criterion)
            if abs(hi - lo) < self.precision:
                return ((lo + hi) / Decimal('2')).quantize(
                    Decimal('0.0000000001'),
                    rounding=ROUND_HALF_UP
                )
        
        # Maximum iterations reached - return best approximation
        result = (lo + hi) / Decimal('2')
        return result.quantize(Decimal('0.0000000001'), rounding=ROUND_HALF_UP)
    
    def _present_value(
        self,
        payment: Decimal,
        rate: Decimal,
        periods: int
    ) -> Decimal:
        """
        Calculate present value of an annuity.
        
        Computes the present value of a series of equal payments using:
        PV = payment * [1 - (1+rate)^(-periods)] / rate
        
        For rate ≈ 0, uses the limit formula: PV = payment * periods
        
        Args:
            payment: Payment amount per period
            rate: Interest rate per period (as decimal)
            periods: Number of payment periods
            
        Returns:
            Present value as Decimal
            
        Notes:
            - Handles zero rate case with limit formula
            - Uses high precision for intermediate calculations
        """
        if periods <= 0:
            return Decimal('0')
        
        # Handle zero or near-zero rate case
        # As rate → 0, PV → payment * periods
        if rate <= Decimal('1e-15'):
            return payment * Decimal(periods)
        
        # Standard present value formula
        # PV = payment * [1 - (1+rate)^(-periods)] / rate
        one_plus_rate = Decimal('1') + rate
        discount_factor = one_plus_rate ** (-periods)
        
        present_value = payment * (Decimal('1') - discount_factor) / rate
        
        return present_value
    
    def solve_annual_rate(
        self,
        principal: Decimal,
        monthly_payment: Decimal,
        num_payments: int
    ) -> Optional[Decimal]:
        """
        Solve for annual nominal interest rate.
        
        This is a convenience method that solves for the monthly rate
        and converts it to an annual nominal rate by multiplying by 12.
        
        Args:
            principal: Loan amount
            monthly_payment: Monthly payment amount
            num_payments: Number of monthly payments
            
        Returns:
            Annual nominal interest rate as decimal (e.g., 0.12 for 12%),
            or None if no valid rate exists
            
        Examples:
            >>> solver = RateSolver()
            >>> solver.solve_annual_rate(
            ...     Decimal('100000'),
            ...     Decimal('1028.61'),
            ...     360
            ... )
            Decimal('0.12')  # 12% annual rate
        """
        monthly_rate = self.solve_monthly_rate(principal, monthly_payment, num_payments)
        
        if monthly_rate is None:
            return None
        
        annual_rate = monthly_rate * Decimal('12')
        return annual_rate.quantize(Decimal('0.0000000001'), rounding=ROUND_HALF_UP)
    
    def solve_effective_annual_rate(
        self,
        principal: Decimal,
        monthly_payment: Decimal,
        num_payments: int
    ) -> Optional[Decimal]:
        """
        Solve for effective annual interest rate (TAE).
        
        This method solves for the monthly rate and converts it to the
        effective annual rate using: TAE = (1 + r_monthly)^12 - 1
        
        Args:
            principal: Loan amount
            monthly_payment: Monthly payment amount
            num_payments: Number of monthly payments
            
        Returns:
            Effective annual interest rate as decimal,
            or None if no valid rate exists
            
        Examples:
            >>> solver = RateSolver()
            >>> solver.solve_effective_annual_rate(
            ...     Decimal('100000'),
            ...     Decimal('1028.61'),
            ...     360
            ... )
            Decimal('0.1268')  # 12.68% effective annual rate
        """
        monthly_rate = self.solve_monthly_rate(principal, monthly_payment, num_payments)
        
        if monthly_rate is None:
            return None
        
        # Calculate effective annual rate: (1 + r_monthly)^12 - 1
        one_plus_monthly = Decimal('1') + monthly_rate
        effective_annual = one_plus_monthly ** 12 - Decimal('1')
        
        return effective_annual.quantize(Decimal('0.000001'), rounding=ROUND_HALF_UP)
