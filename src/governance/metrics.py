# src/governance/metrics.py
"""
Governance Metrics: Observability layer for the Governance Kernel.

This module provides:
- GovernanceMetrics: Immutable snapshot of kernel state
- MetricsCollector: Aggregates metrics over time
- PrometheusRegistry: V1 hardening Prometheus-style counters and gauges
- Export formats: Prometheus text, JSONL

Usage:
    from governance.metrics import MetricsCollector, PrometheusRegistry
    
    collector = MetricsCollector()
    registry = PrometheusRegistry()
    
    # After each step
    result = kernel.step(...)
    collector.record(result, signals)
    registry.record_step(result)
    
    # Export
    print(registry.to_prometheus_text())
"""
import json
from dataclasses import dataclass, asdict, field
from datetime import datetime, timezone
from typing import List, Callable, Optional, Dict, Any
from collections import defaultdict

try:
    from governance.result import EngineResult
    from governance.signals import Signals
except ImportError:
    import os
    import sys
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from governance.result import EngineResult
    from governance.signals import Signals


@dataclass(frozen=True)
class GovernanceMetrics:
    """
    Immutable snapshot of governance state at a single step.
    
    This is the canonical observability object. It captures everything
    needed to understand what the kernel decided and why.
    """
    # Temporal
    timestamp: str
    step: int
    
    # Budget (Output)
    effort: float
    risk: float
    exploration: float
    persistence: float
    
    # Control State (Internal)
    control_margin: float
    control_loss: float
    exploration_pressure: float
    urgency_level: float
    state_risk: float
    
    # Signals (Input)
    reward: float
    novelty: float
    urgency: float
    difficulty: float
    trust: float
    
    # Decision
    mode: str
    halted: bool
    failure_type: Optional[str] = None
    failure_reason: Optional[str] = None

    def to_dict(self) -> Dict[str, Any]:
        """Convert to dictionary for serialization."""
        return asdict(self)
    
    def to_json(self) -> str:
        """Convert to JSON string."""
        return json.dumps(self.to_dict())


# =============================================================================
# Prometheus-Style Metrics (V1 Hardening)
# =============================================================================

class Counter:
    """
    Prometheus-style counter that only increases.
    """
    def __init__(self, name: str, help_text: str, labels: Optional[List[str]] = None):
        self.name = name
        self.help_text = help_text
        self.labels = labels or []
        self._values: Dict[tuple, float] = defaultdict(float)
        self._total = 0.0
    
    def inc(self, value: float = 1.0, labels: Optional[Dict[str, str]] = None) -> None:
        """Increment the counter."""
        if labels:
            key = tuple(sorted(labels.items()))
            self._values[key] += value
        else:
            self._total += value
    
    def get(self, labels: Optional[Dict[str, str]] = None) -> float:
        """Get current value."""
        if labels:
            key = tuple(sorted(labels.items()))
            return self._values[key]
        return self._total
    
    def to_prometheus(self) -> str:
        """Export in Prometheus text format."""
        lines = [
            f"# HELP {self.name} {self.help_text}",
            f"# TYPE {self.name} counter",
        ]
        
        if self._values:
            for key, value in sorted(self._values.items()):
                label_str = ",".join(f'{k}="{v}"' for k, v in key)
                lines.append(f"{self.name}{{{label_str}}} {value}")
        else:
            lines.append(f"{self.name} {self._total}")
        
        return "\n".join(lines)


class Gauge:
    """
    Prometheus-style gauge that can go up or down.
    """
    def __init__(self, name: str, help_text: str):
        self.name = name
        self.help_text = help_text
        self._value = 0.0
    
    def set(self, value: float) -> None:
        """Set the gauge value."""
        self._value = value
    
    def inc(self, value: float = 1.0) -> None:
        """Increment the gauge."""
        self._value += value
    
    def dec(self, value: float = 1.0) -> None:
        """Decrement the gauge."""
        self._value -= value
    
    def get(self) -> float:
        """Get current value."""
        return self._value
    
    def to_prometheus(self) -> str:
        """Export in Prometheus text format."""
        return "\n".join([
            f"# HELP {self.name} {self.help_text}",
            f"# TYPE {self.name} gauge",
            f"{self.name} {self._value:.4f}",
        ])


class PrometheusRegistry:
    """
    Registry of Prometheus-style metrics for governance observability.
    
    V1 Hardening Metrics:
    - agent_steps_total: Total agent steps executed
    - halts_by_reason: Halts counted by reason label
    - audit_entries_written: Total audit entries written
    - effort_drain_rate: Current effort drain rate
    - governance_budget_*: Current budget values (effort, risk, exploration, persistence)
    """
    
    def __init__(self):
        # Counters
        self.steps_total = Counter(
            "agent_steps_total",
            "Total agent steps executed"
        )
        self.halts_by_reason = Counter(
            "halts_by_reason",
            "Halts counted by reason",
            labels=["reason"]
        )
        self.audit_entries_written = Counter(
            "audit_entries_written",
            "Total audit entries written"
        )
        
        # Gauges
        self.effort_drain_rate = Gauge(
            "effort_drain_rate",
            "Current effort drain rate per step"
        )
        self.budget_effort = Gauge(
            "governance_budget_effort",
            "Current effort budget [0,1]"
        )
        self.budget_risk = Gauge(
            "governance_budget_risk",
            "Current risk budget [0,1]"
        )
        self.budget_exploration = Gauge(
            "governance_budget_exploration",
            "Current exploration budget [0,1]"
        )
        self.budget_persistence = Gauge(
            "governance_budget_persistence",
            "Current persistence budget [0,1]"
        )
        self.halted = Gauge(
            "governance_halted",
            "Whether the kernel is halted (0/1)"
        )
        
        # Internal tracking
        self._previous_effort = 1.0
        self._all_metrics = [
            self.steps_total,
            self.halts_by_reason,
            self.audit_entries_written,
            self.effort_drain_rate,
            self.budget_effort,
            self.budget_risk,
            self.budget_exploration,
            self.budget_persistence,
            self.halted,
        ]
    
    def record_step(self, result: EngineResult) -> None:
        """
        Record metrics from a kernel step result.
        
        Args:
            result: The EngineResult from kernel.step()
        """
        # Increment step counter
        self.steps_total.inc()
        
        # Record halt if applicable
        if result.halted and result.reason:
            self.halts_by_reason.inc(labels={"reason": result.reason})
        
        # Update budget gauges
        self.budget_effort.set(result.budget.effort)
        self.budget_risk.set(result.budget.risk)
        self.budget_exploration.set(result.budget.exploration)
        self.budget_persistence.set(result.budget.persistence)
        
        # Calculate effort drain rate
        drain = self._previous_effort - result.budget.effort
        self.effort_drain_rate.set(max(0.0, drain))
        self._previous_effort = result.budget.effort
        
        # Update halted state
        self.halted.set(1.0 if result.halted else 0.0)
    
    def record_audit_entry(self) -> None:
        """Record that an audit entry was written."""
        self.audit_entries_written.inc()
    
    def to_prometheus_text(self) -> str:
        """
        Export all metrics in Prometheus text format.
        
        Returns:
            Complete Prometheus metrics text
        """
        sections = [m.to_prometheus() for m in self._all_metrics]
        return "\n\n".join(sections)


class MetricsCollector:
    """
    Collects and aggregates governance metrics over time.
    
    Features:
    - Records metrics from EngineResult + Signals
    - Supports hooks for real-time streaming
    - Exports to Prometheus and JSONL formats
    """
    
    def __init__(self):
        self._history: List[GovernanceMetrics] = []
        self._hooks: List[Callable[[GovernanceMetrics], None]] = []
        self._step_count = 0
    
    def add_hook(self, hook: Callable[[GovernanceMetrics], None]) -> None:
        """
        Register a callback to be invoked on each metric record.
        
        Args:
            hook: Function that receives GovernanceMetrics
        """
        self._hooks.append(hook)
    
    def remove_hook(self, hook: Callable[[GovernanceMetrics], None]) -> None:
        """Remove a previously registered hook."""
        if hook in self._hooks:
            self._hooks.remove(hook)
    
    def record(
        self,
        result: EngineResult,
        signals: Optional[Signals] = None,
        reward: float = 0.0,
        novelty: float = 0.0,
        urgency: float = 0.0,
        difficulty: float = 0.0,
        trust: float = 1.0,
    ) -> GovernanceMetrics:
        """
        Record metrics from a kernel step result.
        
        Args:
            result: The EngineResult from kernel.step()
            signals: Optional Signals object (if using observe())
            reward/novelty/urgency/difficulty/trust: Direct signal values
            
        Returns:
            The recorded GovernanceMetrics snapshot
        """
        self._step_count += 1
        
        # Extract signal values
        if signals is not None:
            reward = signals.reward
            novelty = signals.novelty
            urgency = signals.urgency
            difficulty = getattr(signals, 'difficulty', 0.0)
            trust = getattr(signals, 'trust', 1.0)
        
        # Build metrics snapshot
        metrics = GovernanceMetrics(
            timestamp=datetime.now(timezone.utc).isoformat(),
            step=self._step_count,
            # Budget
            effort=result.budget.effort,
            risk=result.budget.risk,
            exploration=result.budget.exploration,
            persistence=result.budget.persistence,
            # Control State (handle both dict and object)
            control_margin=result.state['control_margin'] if isinstance(result.state, dict) else result.state.control_margin,
            control_loss=result.state['control_loss'] if isinstance(result.state, dict) else result.state.control_loss,
            exploration_pressure=result.state['exploration_pressure'] if isinstance(result.state, dict) else result.state.exploration_pressure,
            urgency_level=result.state['urgency_level'] if isinstance(result.state, dict) else result.state.urgency_level,
            state_risk=result.state['risk'] if isinstance(result.state, dict) else result.state.risk,
            # Signals
            reward=reward,
            novelty=novelty,
            urgency=urgency,
            difficulty=difficulty,
            trust=trust,
            # Decision
            mode=result.mode.name if hasattr(result.mode, 'name') else str(result.mode),
            halted=result.halted,
            failure_type=result.failure.name if result.failure and hasattr(result.failure, 'name') else None,
            failure_reason=result.reason,
        )
        
        self._history.append(metrics)
        
        # Invoke hooks
        for hook in self._hooks:
            try:
                hook(metrics)
            except Exception:
                pass  # Don't let hook errors break collection
        
        return metrics
    
    @property
    def history(self) -> List[GovernanceMetrics]:
        """Get all recorded metrics."""
        return list(self._history)
    
    @property
    def latest(self) -> Optional[GovernanceMetrics]:
        """Get the most recent metrics snapshot."""
        return self._history[-1] if self._history else None
    
    def clear(self) -> None:
        """Clear all recorded metrics."""
        self._history.clear()
        self._step_count = 0
    
    def to_prometheus(self) -> str:
        """
        Export latest metrics in Prometheus text format.
        
        Returns:
            Prometheus-compatible metrics string
        """
        if not self._history:
            return ""
        
        m = self._history[-1]
        lines = [
            "# HELP governance_budget_effort Current effort budget [0,1]",
            "# TYPE governance_budget_effort gauge",
            f"governance_budget_effort {m.effort:.4f}",
            "",
            "# HELP governance_budget_risk Current risk budget [0,1]",
            "# TYPE governance_budget_risk gauge",
            f"governance_budget_risk {m.risk:.4f}",
            "",
            "# HELP governance_budget_exploration Current exploration budget [0,1]",
            "# TYPE governance_budget_exploration gauge",
            f"governance_budget_exploration {m.exploration:.4f}",
            "",
            "# HELP governance_budget_persistence Current persistence budget [0,1]",
            "# TYPE governance_budget_persistence gauge",
            f"governance_budget_persistence {m.persistence:.4f}",
            "",
            "# HELP governance_control_margin Internal control margin",
            "# TYPE governance_control_margin gauge",
            f"governance_control_margin {m.control_margin:.4f}",
            "",
            "# HELP governance_control_loss Accumulated control loss (frustration)",
            "# TYPE governance_control_loss gauge",
            f"governance_control_loss {m.control_loss:.4f}",
            "",
            "# HELP governance_step_count Total steps executed",
            "# TYPE governance_step_count counter",
            f"governance_step_count {m.step}",
            "",
            "# HELP governance_halted Whether the kernel is halted (0/1)",
            "# TYPE governance_halted gauge",
            f"governance_halted {1 if m.halted else 0}",
        ]
        return "\n".join(lines)
    
    def to_jsonl(self, filepath: Optional[str] = None) -> str:
        """
        Export all metrics as JSON Lines.
        
        Args:
            filepath: If provided, write to file. Otherwise return string.
            
        Returns:
            JSONL string if no filepath given
        """
        lines = [m.to_json() for m in self._history]
        content = "\n".join(lines)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(content)
        
        return content
    
    def summary(self) -> Dict[str, Any]:
        """
        Get a summary of collected metrics.
        
        Returns:
            Dict with min/max/avg for key metrics
        """
        if not self._history:
            return {}
        
        efforts = [m.effort for m in self._history]
        risks = [m.risk for m in self._history]
        losses = [m.control_loss for m in self._history]
        
        return {
            "total_steps": len(self._history),
            "halted": self._history[-1].halted,
            "final_mode": self._history[-1].mode,
            "effort": {
                "min": min(efforts),
                "max": max(efforts),
                "avg": sum(efforts) / len(efforts),
                "final": efforts[-1],
            },
            "risk": {
                "min": min(risks),
                "max": max(risks),
                "avg": sum(risks) / len(risks),
                "final": risks[-1],
            },
            "control_loss": {
                "min": min(losses),
                "max": max(losses),
                "final": losses[-1],
            },
        }
