"""
Safe-Kernel Contracts for Governance Kernel.

This module defines explicit invariants and assertions to catch boundary violations
in the governance kernel. Contracts ensure the kernel maintains its safety guarantees.

Invariants Enforced:
1. Budget Never Increases - Budgets cannot increase spontaneously (only via recovery)
2. Halt Is Terminal - Once halted, kernel remains halted irreversibly
3. Kernel Never Invokes - Kernel evaluates but never executes actions

Usage:
    from governance.contracts import ContractEnforcer
    
    enforcer = ContractEnforcer(enabled=True)
    
    # Before step
    prev_budget = kernel.budget
    prev_halted = kernel._halted
    
    # After step
    result = kernel.step(...)
    enforcer.check_budget_monotonicity(prev_budget, result.budget)
    enforcer.check_halt_irreversibility(prev_halted, result.halted)

Enable via environment variable:
    export GOVERNANCE_CONTRACTS_ENABLED=1
"""

import os
from dataclasses import dataclass
from typing import Optional, Callable, Any
from functools import wraps


# =============================================================================
# Contract Configuration
# =============================================================================

def contracts_enabled() -> bool:
    """Check if contract enforcement is enabled."""
    return os.environ.get("GOVERNANCE_CONTRACTS_ENABLED", "0") == "1"


# =============================================================================
# Exceptions
# =============================================================================

class ContractViolation(Exception):
    """
    Raised when a kernel contract is violated.
    
    This is a critical error indicating the governance kernel has
    entered an invalid state. Should never occur in correct operation.
    """
    def __init__(self, contract_name: str, message: str, details: Optional[dict] = None):
        self.contract_name = contract_name
        self.message = message
        self.details = details or {}
        super().__init__(f"CONTRACT VIOLATION [{contract_name}]: {message}")


class BudgetIncreasedError(ContractViolation):
    """Raised when a budget value increases unexpectedly."""
    def __init__(self, budget_name: str, previous: float, current: float):
        super().__init__(
            contract_name="BUDGET_NEVER_INCREASES",
            message=f"{budget_name} budget increased from {previous:.4f} to {current:.4f}",
            details={"budget": budget_name, "previous": previous, "current": current}
        )


class HaltReversedError(ContractViolation):
    """Raised when a halted kernel returns to non-halted state."""
    def __init__(self):
        super().__init__(
            contract_name="HALT_IS_TERMINAL",
            message="Kernel reversed from HALTED to non-halted state",
            details={}
        )


class KernelInvokedActionError(ContractViolation):
    """Raised when the kernel attempts to execute an action directly."""
    def __init__(self, action_name: str):
        super().__init__(
            contract_name="KERNEL_NEVER_INVOKES",
            message=f"Kernel attempted to invoke action: {action_name}",
            details={"action": action_name}
        )


# =============================================================================
# Contract Decorator
# =============================================================================

def contract(name: str, enabled_check: Callable[[], bool] = contracts_enabled):
    """
    Decorator for contract-checked functions.
    
    Args:
        name: Name of the contract being enforced
        enabled_check: Function that returns True if contracts should be checked
    
    Usage:
        @contract("MUST_BE_POSITIVE")
        def check_positive(value: float) -> bool:
            return value >= 0
            
        # Returns True/False normally, raises ContractViolation if enabled and False
    """
    def decorator(func: Callable[..., bool]):
        @wraps(func)
        def wrapper(*args, **kwargs) -> bool:
            result = func(*args, **kwargs)
            if enabled_check() and not result:
                raise ContractViolation(
                    contract_name=name,
                    message=f"Contract {name} failed: {func.__doc__ or 'no description'}",
                    details={"args": args, "kwargs": kwargs}
                )
            return result
        return wrapper
    return decorator


# =============================================================================
# Contract Enforcer
# =============================================================================

class ContractEnforcer:
    """
    Runtime contract enforcer for governance kernel.
    
    Checks critical invariants and raises ContractViolation on breach.
    """
    
    def __init__(self, enabled: Optional[bool] = None):
        """
        Initialize contract enforcer.
        
        Args:
            enabled: Override for contract checking (uses env var if None)
        """
        self._enabled = enabled if enabled is not None else contracts_enabled()
    
    @property
    def enabled(self) -> bool:
        """Check if enforcement is enabled."""
        return self._enabled
    
    def check_budget_monotonicity(
        self,
        prev_budget: Any,
        curr_budget: Any,
        allow_recovery: bool = True,
        recovering: bool = False,
    ) -> None:
        """
        Contract: Budget Never Increases (except during recovery).
        
        Verifies that budget values do not increase spontaneously.
        Only effort and persistence may increase during RECOVERING mode.
        
        Args:
            prev_budget: Budget from previous step
            curr_budget: Budget from current step
            allow_recovery: If True, allow increases during recovery
            recovering: True if kernel is in RECOVERING mode
        
        Raises:
            BudgetIncreasedError: If budget increased outside of recovery
        """
        if not self._enabled:
            return
        
        # Risk should NEVER increase (even during recovery)
        if curr_budget.risk > prev_budget.risk + 1e-9:
            raise BudgetIncreasedError("risk", prev_budget.risk, curr_budget.risk)
        
        # Exploration should NEVER increase
        if curr_budget.exploration > prev_budget.exploration + 1e-9:
            raise BudgetIncreasedError("exploration", prev_budget.exploration, curr_budget.exploration)
        
        # Effort and persistence can only increase during recovery
        if not (allow_recovery and recovering):
            if curr_budget.effort > prev_budget.effort + 1e-9:
                raise BudgetIncreasedError("effort", prev_budget.effort, curr_budget.effort)
            
            if curr_budget.persistence > prev_budget.persistence + 1e-9:
                raise BudgetIncreasedError("persistence", prev_budget.persistence, curr_budget.persistence)
    
    def check_halt_irreversibility(
        self,
        was_halted: bool,
        is_halted: bool,
        reset_called: bool = False,
    ) -> None:
        """
        Contract: Halt Is Terminal.
        
        Once a kernel enters HALTED state, it must remain halted forever
        (unless explicitly reset, which is tracked separately).
        
        Args:
            was_halted: Halted state before step
            is_halted: Halted state after step
            reset_called: True if reset() was called between checks
        
        Raises:
            HaltReversedError: If halted state was reversed without reset
        """
        if not self._enabled:
            return
        
        if was_halted and not is_halted and not reset_called:
            raise HaltReversedError()
    
    def check_kernel_never_invokes(
        self,
        kernel: Any,
        action_name: Optional[str] = None,
    ) -> None:
        """
        Contract: Kernel Never Invokes.
        
        The kernel must never execute actions directly. It only evaluates
        signals and returns decisions. Execution is the enforcer's responsibility.
        
        This is a design invariant checked via code audit, but we provide
        a runtime check that can be called by enforcement layer.
        
        Args:
            kernel: The governance kernel instance
            action_name: Name of action if one was detected
        
        Raises:
            KernelInvokedActionError: If kernel invoked an action
        """
        if not self._enabled:
            return
        
        # The kernel should not have any action invocation methods
        # This check is primarily for documentation and audit purposes
        forbidden_attrs = ['execute', 'run_action', 'invoke', 'call_tool']
        
        for attr in forbidden_attrs:
            if hasattr(kernel, attr) and callable(getattr(kernel, attr)):
                raise KernelInvokedActionError(attr)


# =============================================================================
# Budget Wrapper with Contract Checking
# =============================================================================

class ContractCheckedKernel:
    """
    Wrapper around GovernanceKernel that enforces contracts on every step.
    
    Usage:
        from governance.kernel import GovernanceKernel
        from governance.contracts import ContractCheckedKernel
        
        kernel = GovernanceKernel(profile)
        checked = ContractCheckedKernel(kernel)
        
        result = checked.step(reward=0.5, novelty=0.1, urgency=0.2)
        # Contracts are automatically verified
    """
    
    def __init__(self, kernel: Any, enforcer: Optional[ContractEnforcer] = None):
        """
        Wrap a kernel with contract checking.
        
        Args:
            kernel: GovernanceKernel instance to wrap
            enforcer: ContractEnforcer instance (creates new if None)
        """
        self._kernel = kernel
        self._enforcer = enforcer or ContractEnforcer()
        self._reset_called = False
    
    def step(self, **kwargs) -> Any:
        """
        Execute a kernel step with contract verification.
        
        All arguments are passed through to kernel.step().
        
        Returns:
            EngineResult from the kernel
        
        Raises:
            ContractViolation: If any contract is violated
        """
        # Capture pre-step state
        prev_budget = self._kernel.budget
        was_halted = self._kernel._halted
        
        # Execute step
        result = self._kernel.step(**kwargs)
        
        # Check contracts
        from governance.modes import Mode
        recovering = result.mode == Mode.RECOVERING
        
        self._enforcer.check_budget_monotonicity(
            prev_budget,
            result.budget,
            recovering=recovering,
        )
        
        self._enforcer.check_halt_irreversibility(
            was_halted,
            result.halted,
            reset_called=self._reset_called,
        )
        
        self._reset_called = False
        return result
    
    def reset(self, reason: str) -> None:
        """Reset the kernel and mark that reset was called."""
        self._reset_called = True
        self._kernel.reset(reason)
    
    def __getattr__(self, name: str) -> Any:
        """Forward all other attribute access to wrapped kernel."""
        return getattr(self._kernel, name)


# =============================================================================
# Convenience Functions
# =============================================================================

def assert_budget_not_increased(
    prev_budget: Any,
    curr_budget: Any,
    context: str = "",
) -> None:
    """
    Assert that no budget value has increased.
    
    Convenience function for inline assertions.
    """
    if not contracts_enabled():
        return
    
    enforcer = ContractEnforcer(enabled=True)
    try:
        enforcer.check_budget_monotonicity(prev_budget, curr_budget, allow_recovery=False)
    except BudgetIncreasedError as e:
        if context:
            e.message = f"{context}: {e.message}"
        raise


def assert_halt_is_terminal(was_halted: bool, is_halted: bool) -> None:
    """
    Assert that halt state was not reversed.
    
    Convenience function for inline assertions.
    """
    if not contracts_enabled():
        return
    
    enforcer = ContractEnforcer(enabled=True)
    enforcer.check_halt_irreversibility(was_halted, is_halted)
