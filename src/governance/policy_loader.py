"""
Policy Loader for Governance Kernel.

Loads governance policies from YAML configuration files and applies them
to Profile objects for kernel initialization.

Usage:
    from governance.policy_loader import PolicyLoader
    
    # Load policies from file
    loader = PolicyLoader("config/policies.yaml")
    profile = loader.create_profile()
    
    # Use profile with kernel
    kernel = GovernanceKernel(profile)

Configuration Format:
    See config/policies.yaml for the complete schema.
"""

import os
from pathlib import Path
from dataclasses import dataclass
from typing import Any, Dict, Optional

try:
    import yaml
    YAML_AVAILABLE = True
except ImportError:
    YAML_AVAILABLE = False

try:
    from governance.profiles import Profile, BALANCED
except ImportError:
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from governance.profiles import Profile, BALANCED


# Default config path
DEFAULT_CONFIG_PATH = Path(__file__).parent.parent.parent / "config" / "policies.yaml"


class PolicyLoadError(Exception):
    """Raised when policy loading fails."""
    pass


@dataclass
class PolicyConfig:
    """
    Parsed policy configuration.
    
    Maps directly to Profile fields with sensible defaults.
    """
    # Limits
    max_steps: int = 100
    max_effort: float = 1.0
    max_risk: float = 0.8
    max_exploration: float = 0.9
    exhaustion_threshold: float = 0.05
    
    # Stagnation
    stagnation_window: int = 10
    stagnation_effort_floor: float = 0.1
    stagnation_effort_scale: float = 0.7
    stagnation_persistence_scale: float = 0.6
    progress_threshold: float = 0.05
    
    # Recovery
    recovery_rate: float = 0.25
    recovery_cap: float = 1.0
    recovery_delay: float = 0.5
    
    # Decay
    persistence_decay: float = 0.05
    exploration_decay: float = 0.05
    time_persistence_decay: float = 0.002
    time_exploration_decay: float = 0.002
    
    # Scaling
    effort_scale: float = 1.0
    risk_scale: float = 1.0
    exploration_scale: float = 1.0
    persistence_scale: float = 1.0


class PolicyLoader:
    """
    Loads governance policies from YAML configuration.
    
    Features:
    - Validates configuration schema
    - Provides sensible defaults for missing values
    - Creates Profile objects from configuration
    """
    
    def __init__(self, filepath: Optional[str] = None):
        """
        Initialize policy loader.
        
        Args:
            filepath: Path to YAML config file (uses default if None)
        """
        if not YAML_AVAILABLE:
            raise PolicyLoadError(
                "PyYAML is required for policy loading. "
                "Install with: pip install pyyaml"
            )
        
        self.filepath = Path(filepath) if filepath else DEFAULT_CONFIG_PATH
        self._config: Optional[Dict[str, Any]] = None
        self._policy: Optional[PolicyConfig] = None
    
    def load(self) -> PolicyConfig:
        """
        Load and parse the policy configuration.
        
        Returns:
            PolicyConfig with parsed values
            
        Raises:
            PolicyLoadError: If loading or parsing fails
        """
        if not self.filepath.exists():
            raise PolicyLoadError(f"Policy file not found: {self.filepath}")
        
        try:
            with open(self.filepath, 'r') as f:
                self._config = yaml.safe_load(f)
        except yaml.YAMLError as e:
            raise PolicyLoadError(f"Invalid YAML in {self.filepath}: {e}")
        
        # Parse into PolicyConfig with defaults
        limits = self._config.get('limits', {})
        stagnation = self._config.get('stagnation', {})
        recovery = self._config.get('recovery', {})
        decay = self._config.get('decay', {})
        scaling = self._config.get('scaling', {})
        
        self._policy = PolicyConfig(
            # Limits
            max_steps=limits.get('max_steps', 100),
            max_effort=limits.get('max_effort', 1.0),
            max_risk=limits.get('max_risk', 0.8),
            max_exploration=limits.get('max_exploration', 0.9),
            exhaustion_threshold=limits.get('exhaustion_threshold', 0.05),
            
            # Stagnation
            stagnation_window=stagnation.get('window', 10),
            stagnation_effort_floor=stagnation.get('effort_floor', 0.1),
            stagnation_effort_scale=stagnation.get('effort_scale', 0.7),
            stagnation_persistence_scale=stagnation.get('persistence_scale', 0.6),
            progress_threshold=stagnation.get('progress_threshold', 0.05),
            
            # Recovery
            recovery_rate=recovery.get('rate', 0.25),
            recovery_cap=recovery.get('cap', 1.0),
            recovery_delay=recovery.get('delay', 0.5),
            
            # Decay
            persistence_decay=decay.get('persistence', 0.05),
            exploration_decay=decay.get('exploration', 0.05),
            time_persistence_decay=decay.get('time_persistence', 0.002),
            time_exploration_decay=decay.get('time_exploration', 0.002),
            
            # Scaling
            effort_scale=scaling.get('effort', 1.0),
            risk_scale=scaling.get('risk', 1.0),
            exploration_scale=scaling.get('exploration', 1.0),
            persistence_scale=scaling.get('persistence', 1.0),
        )
        
        return self._policy
    
    def create_profile(self, name: str = "policy_configured") -> Profile:
        """
        Create a Profile from the loaded policy configuration.
        
        Args:
            name: Name for the created profile
            
        Returns:
            Profile configured from policy
        """
        if self._policy is None:
            self.load()
        
        policy = self._policy
        
        return Profile(
            name=name,
            # Scaling
            effort_scale=policy.effort_scale,
            risk_scale=policy.risk_scale,
            exploration_scale=policy.exploration_scale,
            persistence_scale=policy.persistence_scale,
            # Recovery
            recovery_rate=policy.recovery_rate,
            recovery_cap=policy.recovery_cap,
            recovery_delay=policy.recovery_delay,
            # Decay
            persistence_decay=policy.persistence_decay,
            exploration_decay=policy.exploration_decay,
            time_persistence_decay=policy.time_persistence_decay,
            time_exploration_decay=policy.time_exploration_decay,
            # Stagnation
            stagnation_window=policy.stagnation_window,
            stagnation_effort_floor=policy.stagnation_effort_floor,
            stagnation_effort_scale=policy.stagnation_effort_scale,
            stagnation_persistence_scale=policy.stagnation_persistence_scale,
            progress_threshold=policy.progress_threshold,
            # Limits
            exhaustion_threshold=policy.exhaustion_threshold,
            max_risk=policy.max_risk,
            max_exploration=policy.max_exploration,
            max_steps=policy.max_steps,
        )
    
    @property
    def raw_config(self) -> Optional[Dict[str, Any]]:
        """Get the raw YAML configuration dictionary."""
        return self._config


def load_policy_profile(filepath: Optional[str] = None) -> Profile:
    """
    Convenience function to load a profile from policy config.
    
    Args:
        filepath: Path to config file (uses default if None)
        
    Returns:
        Configured Profile
    """
    loader = PolicyLoader(filepath)
    return loader.create_profile()
