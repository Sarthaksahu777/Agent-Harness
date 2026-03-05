# Governance Engine/auto.py
import time
import functools
from typing import Callable, Any, Optional
from dataclasses import dataclass

from governance.agent import GovernanceAgent
from governance.interface import observe
from governance.observation import Observation
from governance.guarantees import StepResult

class GovernedDecorator:
    """
    Automates signal extraction by wrapping tool or agent calls.
    
    It observes:
    - Execution time (Elapsed)
    - Success/Failure (Exceptions)
    - Output size (Proxy for state change)
    """
    def __init__(self, agent: GovernanceAgent):
        self.agent = agent

    def __call__(self, func: Callable) -> Callable:
        @functools.wraps(func)
        def wrapper(*args, **kwargs) -> Any:
            start_time = time.monotonic()
            result = None
            error = None
            status = 'success'
            
            try:
                result = func(*args, **kwargs)
            except Exception as e:
                error = str(e)
                status = 'error'
            
            elapsed = time.monotonic() - start_time
            
            # Simple automatic observation
            # We use repr(result) length as a crude proxy for env_state_change
            # This can be overridden by the user.
            obs = Observation(
                action=func.__name__,
                result=status,
                elapsed_time=elapsed,
                env_state_delta=min(1.0, len(str(result)) / 1000.0) if result else 0.0,
                agent_state_delta=0.1, # Conservative default
                error=error
            )
            
            # Record observation
            gov_result = observe(self.agent, obs)
            
            # If governance halted, we might want to raise here or just return result
            # but usually, the loop should handle it.
            # We attach the gov_result to the function return for introspection.
            if hasattr(result, '__dict__'):
                result._gov = gov_result
                
            if error:
                raise Exception(f"Governance Check: {gov_result.mode.name} | Original Error: {error}")
                
            return result
        return wrapper

def governed(agent: GovernanceAgent):
    """Decorator to automatically govern a function."""
    return GovernedDecorator(agent)
