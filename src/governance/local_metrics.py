"""
Local Metrics Sink: Offline-first metrics persistence.

This module provides a non-blocking, fault-tolerant metrics sink that:
- Appends metrics snapshots to a local JSONL file
- Never raises exceptions (silently drops on failure)
- Never blocks execution
- Works fully offline with no network dependencies

IMPORTANT: Governance correctness does NOT depend on this module.
This is an optional observer that must never affect execution.

Usage:
    from governance.local_metrics import LocalMetricsSink
    
    sink = LocalMetricsSink("metrics.jsonl")
    sink.record(step=1, effort=0.85, risk=0.1, halted=False)
"""

import json
import os
from datetime import datetime, timezone
from typing import Optional, Any, Dict


class LocalMetricsSink:
    """
    Offline-first metrics sink that persists to JSONL.
    
    Design principles:
    - NEVER raises exceptions
    - NEVER blocks execution
    - Silently drops metrics on any failure
    - Zero network dependencies
    
    The governance kernel must function identically whether this
    sink is working, failing, or disabled entirely.
    """
    
    def __init__(self, filepath: str = "metrics.jsonl"):
        """
        Initialize the local metrics sink.
        
        Args:
            filepath: Path to JSONL file for metrics storage
        """
        self._filepath = filepath
        self._enabled = True
    
    def record(
        self,
        step: int,
        effort_remaining: float,
        risk_level: float,
        halted: bool = False,
        halt_reason: Optional[str] = None,
        extra: Optional[Dict[str, Any]] = None,
    ) -> bool:
        """
        Record a metrics snapshot to the local file.
        
        This method NEVER raises exceptions. On any failure,
        it silently drops the metric and returns False.
        
        Args:
            step: Current step number
            effort_remaining: Remaining effort budget [0, 1]
            risk_level: Current risk level [0, 1]
            halted: Whether the kernel is halted
            halt_reason: Reason for halt (if halted)
            extra: Optional additional fields
            
        Returns:
            True if write succeeded, False otherwise
        """
        if not self._enabled:
            return False
        
        try:
            # Build metrics entry
            entry = {
                "timestamp": datetime.now(timezone.utc).isoformat(),
                "step": step,
                "effort_remaining": effort_remaining,
                "risk_level": risk_level,
                "halted": halted,
            }
            
            if halted and halt_reason:
                entry["halt_reason"] = halt_reason
            
            if extra:
                entry.update(extra)
            
            # Serialize to JSON
            line = json.dumps(entry, separators=(',', ':'))
            
            # Append to file (non-blocking, best-effort)
            with open(self._filepath, 'a', encoding='utf-8') as f:
                f.write(line + '\n')
            
            return True
            
        except Exception:
            # CRITICAL: Never propagate exceptions
            # Metrics are optional observers, not dependencies
            return False
    
    def record_from_result(self, result: Any, step: int = 0) -> bool:
        """
        Record metrics from an EngineResult.
        
        Args:
            result: EngineResult from kernel.step()
            step: Current step number
            
        Returns:
            True if write succeeded, False otherwise
        """
        try:
            return self.record(
                step=step,
                effort_remaining=result.budget.effort,
                risk_level=result.budget.risk,
                halted=result.halted,
                halt_reason=result.reason if result.halted else None,
                extra={
                    "exploration": result.budget.exploration,
                    "persistence": result.budget.persistence,
                    "mode": result.mode.name if hasattr(result.mode, 'name') else str(result.mode),
                }
            )
        except Exception:
            # CRITICAL: Never propagate exceptions
            return False
    
    def disable(self) -> None:
        """Disable metrics recording."""
        self._enabled = False
    
    def enable(self) -> None:
        """Enable metrics recording."""
        self._enabled = True
    
    @property
    def filepath(self) -> str:
        """Get the metrics file path."""
        return self._filepath
    
    def clear(self) -> bool:
        """
        Clear the metrics file.
        
        Returns:
            True if successful, False otherwise
        """
        try:
            if os.path.exists(self._filepath):
                os.remove(self._filepath)
            return True
        except Exception:
            return False


def create_sink(filepath: str = "metrics.jsonl") -> LocalMetricsSink:
    """
    Factory function to create a LocalMetricsSink.
    
    Args:
        filepath: Path for metrics file
        
    Returns:
        LocalMetricsSink instance
    """
    return LocalMetricsSink(filepath)
