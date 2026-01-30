#!/usr/bin/env python3
"""
Governance Visualizer: Real-time terminal dashboard for Agent Harness.

This visualizer uses the `rich` library to render a live dashboard
showing:
- Budget bars (effort, risk, exploration, persistence)
- Control state values
- Signal inputs
- Mode and halt status
- Step history graph (ASCII sparkline)

Usage:
    python experiments/visualizer.py
    
Or programmatically:
    from experiments.visualizer import GovernanceVisualizer
    
    viz = GovernanceVisualizer()
    viz.update(metrics)
    viz.render()

Requirements:
    pip install rich
"""
import sys
import os
import time

# Add src to path for imports
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../src')))

try:
    from rich.console import Console
    from rich.live import Live
    from rich.table import Table
    from rich.panel import Panel
    from rich.layout import Layout
    from rich.text import Text
    from rich.progress import Progress, BarColumn, TextColumn
    from rich import box
    RICH_AVAILABLE = True
except ImportError:
    RICH_AVAILABLE = False
    print("Warning: 'rich' library not installed. Install with: pip install rich")

from governance import GovernanceAgent, step, Signals, PROFILES, ProfileType
from governance.metrics import MetricsCollector, GovernanceMetrics
from typing import List, Optional


def create_bar(value: float, width: int = 20, filled: str = None, empty: str = None) -> str:
    """Create an ASCII progress bar."""
    # Use ASCII-safe characters on Windows to avoid encoding issues
    if filled is None:
        try:
            # Test if we can encode Unicode
            "█░".encode(sys.stdout.encoding or 'utf-8')
            filled, empty = "█", "░"
        except (UnicodeEncodeError, LookupError):
            filled, empty = "#", "-"
    if empty is None:
        empty = "-"
    filled_width = int(value * width)
    return filled * filled_width + empty * (width - filled_width)


def create_sparkline(values: List[float], width: int = 30) -> str:
    """Create an ASCII sparkline graph."""
    # Use ASCII-safe characters on Windows
    try:
        "─▁▂▃▄▅▆▇█".encode(sys.stdout.encoding or 'utf-8')
        empty_char = "─"
        chars = " ▁▂▃▄▅▆▇█"
    except (UnicodeEncodeError, LookupError):
        empty_char = "-"
        chars = " _.,-~=+#"
    
    if not values:
        return empty_char * width
    
    # Take last `width` values
    values = values[-width:]
    
    # Normalize to [0, 1]
    min_val = min(values) if values else 0
    max_val = max(values) if values else 1
    range_val = max_val - min_val if max_val != min_val else 1
    
    result = ""
    for v in values:
        normalized = (v - min_val) / range_val
        idx = int(normalized * (len(chars) - 1))
        result += chars[idx]
    
    # Pad to width
    result += empty_char * (width - len(result))
    return result


class GovernanceVisualizer:
    """
    Real-time terminal dashboard for governance state visualization.
    """
    
    def __init__(self):
        self.console = Console() if RICH_AVAILABLE else None
        self.history: List[GovernanceMetrics] = []
        self.max_history = 100
    
    def update(self, metrics: GovernanceMetrics) -> None:
        """Add a new metrics snapshot to history."""
        self.history.append(metrics)
        if len(self.history) > self.max_history:
            self.history = self.history[-self.max_history:]
    
    def render_simple(self) -> str:
        """Render a simple ASCII dashboard (no rich dependency)."""
        if not self.history:
            return "No data yet..."
        
        m = self.history[-1]
        effort_history = [h.effort for h in self.history]
        risk_history = [h.risk for h in self.history]
        
        lines = [
            "┌" + "─" * 70 + "┐",
            "│" + " Agent Harness Governance Dashboard ".center(70) + "│",
            "├" + "─" * 70 + "┤",
            f"│ Step: {m.step:<6}  Mode: {m.mode:<12}  Halted: {str(m.halted):<6}".ljust(71) + "│",
            "├" + "─" * 70 + "┤",
            "│ BUDGET".ljust(71) + "│",
            f"│   Effort      {create_bar(m.effort)}  {m.effort:.2f}".ljust(71) + "│",
            f"│   Risk        {create_bar(m.risk)}  {m.risk:.2f}".ljust(71) + "│",
            f"│   Exploration {create_bar(m.exploration)}  {m.exploration:.2f}".ljust(71) + "│",
            f"│   Persistence {create_bar(m.persistence)}  {m.persistence:.2f}".ljust(71) + "│",
            "├" + "─" * 70 + "┤",
            "│ CONTROL STATE".ljust(71) + "│",
            f"│   Margin: {m.control_margin:+.2f}  Loss: {m.control_loss:.2f}  Pressure: {m.exploration_pressure:.2f}  Urgency: {m.urgency_level:.2f}".ljust(71) + "│",
            "├" + "─" * 70 + "┤",
            "│ SIGNALS (Last Input)".ljust(71) + "│",
            f"│   Reward: {m.reward:.2f}  Novelty: {m.novelty:.2f}  Urgency: {m.urgency:.2f}  Difficulty: {m.difficulty:.2f}  Trust: {m.trust:.2f}".ljust(71) + "│",
            "├" + "─" * 70 + "┤",
            "│ EFFORT TREND".ljust(71) + "│",
            f"│   {create_sparkline(effort_history, 60)}".ljust(71) + "│",
            "│ RISK TREND".ljust(71) + "│",
            f"│   {create_sparkline(risk_history, 60)}".ljust(71) + "│",
            "└" + "─" * 70 + "┘",
        ]
        
        if m.halted and m.failure_type:
            lines.insert(-1, f"│ ⚠ HALTED: {m.failure_type} - {m.failure_reason or 'No reason'}".ljust(71) + "│")
        
        return "\n".join(lines)
    
    def render_rich(self) -> Panel:
        """Render a rich-formatted dashboard panel."""
        if not RICH_AVAILABLE or not self.history:
            return Panel("No data yet...")
        
        m = self.history[-1]
        effort_history = [h.effort for h in self.history]
        risk_history = [h.risk for h in self.history]
        
        # Build content
        content = []
        
        # Header
        mode_color = "green" if m.mode == "NOMINAL" else "yellow" if m.mode == "RECOVERING" else "red"
        header = Text()
        header.append(f"Step: {m.step}  ", style="bold")
        header.append(f"Mode: ", style="dim")
        header.append(f"{m.mode}  ", style=f"bold {mode_color}")
        header.append(f"Halted: ", style="dim")
        header.append(f"{m.halted}", style="bold red" if m.halted else "bold green")
        content.append(header)
        content.append("")
        
        # Budget bars
        content.append(Text("BUDGET", style="bold underline"))
        budget_items = [
            ("Effort", m.effort, "blue"),
            ("Risk", m.risk, "red"),
            ("Exploration", m.exploration, "green"),
            ("Persistence", m.persistence, "yellow"),
        ]
        for name, value, color in budget_items:
            bar = create_bar(value)
            line = Text()
            line.append(f"  {name:12} ", style="dim")
            line.append(bar, style=color)
            line.append(f"  {value:.2f}", style="bold")
            content.append(line)
        content.append("")
        
        # Control State
        content.append(Text("CONTROL STATE", style="bold underline"))
        state_line = Text()
        state_line.append(f"  Margin: {m.control_margin:+.2f}  ", style="cyan")
        state_line.append(f"Loss: {m.control_loss:.2f}  ", style="red")
        state_line.append(f"Pressure: {m.exploration_pressure:.2f}  ", style="green")
        state_line.append(f"Urgency: {m.urgency_level:.2f}", style="yellow")
        content.append(state_line)
        content.append("")
        
        # Signals
        content.append(Text("SIGNALS", style="bold underline"))
        sig_line = Text()
        sig_line.append(f"  Reward: {m.reward:.2f}  ", style="green" if m.reward > 0 else "red")
        sig_line.append(f"Novelty: {m.novelty:.2f}  ", style="blue")
        sig_line.append(f"Urgency: {m.urgency:.2f}  ", style="yellow")
        sig_line.append(f"Difficulty: {m.difficulty:.2f}  ", style="red")
        sig_line.append(f"Trust: {m.trust:.2f}", style="cyan")
        content.append(sig_line)
        content.append("")
        
        # Sparklines
        content.append(Text("TRENDS (last 30 steps)", style="bold underline"))
        content.append(Text(f"  Effort: {create_sparkline(effort_history)}", style="blue"))
        content.append(Text(f"  Risk:   {create_sparkline(risk_history)}", style="red"))
        
        # Halt warning
        if m.halted:
            content.append("")
            content.append(Text(f"⚠ HALTED: {m.failure_type} - {m.failure_reason or 'Unknown'}", style="bold red"))
        
        return Panel(
            "\n".join(str(c) if isinstance(c, str) else c.plain if hasattr(c, 'plain') else str(c) for c in content),
            title="[bold]Agent Harness Governance Dashboard[/bold]",
            border_style="blue",
            box=box.DOUBLE,
        )
    
    def print(self) -> None:
        """Print the current dashboard state."""
        if RICH_AVAILABLE and self.console:
            self.console.clear()
            self.console.print(self.render_rich())
        else:
            print("\033[2J\033[H")  # Clear terminal
            print(self.render_simple())


def run_demo():
    """Run a demo simulation with random signals."""
    import random
    
    print("=" * 60)
    print(" Agent Harness Governance Visualizer Demo")
    print("=" * 60)
    print()
    
    # Initialize
    agent = GovernanceAgent(PROFILES[ProfileType.BALANCED])
    collector = MetricsCollector()
    visualizer = GovernanceVisualizer()
    
    # Hook visualizer to collector
    collector.add_hook(visualizer.update)
    
    print("Starting demo... (Press Ctrl+C to stop)")
    print()
    time.sleep(1)
    
    try:
        for i in range(100):
            # Generate random signals (with some patterns)
            reward = random.uniform(0.0, 0.4) + (0.3 if i % 10 < 5 else 0.0)
            novelty = random.uniform(0.0, 0.3)
            urgency = min(1.0, 0.1 + (i * 0.01))  # Gradually increasing
            difficulty = random.uniform(0.0, 0.3) + (0.4 if i > 70 else 0.0)  # Spike late
            
            signals = Signals(
                reward=reward,
                novelty=novelty,
                urgency=urgency,
                difficulty=difficulty,
                trust=1.0,
            )
            
            result = step(agent, signals)
            collector.record(result, signals)
            
            # Render
            visualizer.print()
            
            if result.halted:
                print()
                print("=" * 60)
                print(f" Agent HALTED at step {i+1}")
                print(f" Reason: {result.reason}")
                print("=" * 60)
                break
            
            time.sleep(0.15)
    
    except KeyboardInterrupt:
        print("\n\nDemo stopped by user.")
    
    # Print summary
    print()
    print("=" * 60)
    print(" Session Summary")
    print("=" * 60)
    summary = collector.summary()
    print(f"  Total Steps: {summary.get('total_steps', 0)}")
    print(f"  Final Mode: {summary.get('final_mode', 'N/A')}")
    print(f"  Halted: {summary.get('halted', False)}")
    if 'effort' in summary:
        print(f"  Effort: min={summary['effort']['min']:.2f}, max={summary['effort']['max']:.2f}, avg={summary['effort']['avg']:.2f}")
    if 'risk' in summary:
        print(f"  Risk: min={summary['risk']['min']:.2f}, max={summary['risk']['max']:.2f}, avg={summary['risk']['avg']:.2f}")
    print()
    
    # Export
    prometheus_output = collector.to_prometheus()
    print("Prometheus Metrics (latest):")
    print("-" * 40)
    for line in prometheus_output.split("\n")[:10]:
        print(f"  {line}")
    print("  ...")
    print()


if __name__ == "__main__":
    if not RICH_AVAILABLE:
        print("For best experience, install rich: pip install rich")
        print()
    run_demo()
