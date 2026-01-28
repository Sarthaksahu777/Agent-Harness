# emocore/__init__.py
"""
EmoCore - Runtime Governance for Autonomous Agents

Public API:
    from governance import EmoCoreAgent, step, Signals
    from governance.profiles import PROFILES, ProfileType

Usage:
    agent = EmoCoreAgent()
    result = step(agent, Signals(reward=0.5, novelty=0.1, urgency=0.2))
"""

from governance.agent import EmoCoreAgent
from governance.interface import step, observe, Signals
from governance.observation import Observation
from governance.adapters import LLMLoopAdapter, ToolCallingAgentAdapter
from governance.guarantees import StepResult, GuaranteeEnforcer
from governance.failures import FailureType
from governance.modes import Mode
from governance.behavior import BehaviorBudget
from governance.state import ControlState
from governance.profiles import Profile, PROFILES, ProfileType

# Backward compatibility aliases
PressureState = ControlState

__all__ = [
    # Main API
    "EmoCoreAgent",
    "step",
    "observe",
    "Signals",
    "Observation",
    "StepResult",
    # Adapters
    "LLMLoopAdapter",
    "ToolCallingAgentAdapter",
    # Types
    "FailureType",
    "Mode",
    "BehaviorBudget",
    "ControlState",
    "PressureState",  # Alias
    # Profiles
    "Profile",
    "PROFILES",
    "ProfileType",
    # Guarantees
    "GuaranteeEnforcer",
]

__version__ = "0.7.0"
