import os
import matplotlib.pyplot as plt
import matplotlib.patches as patches
import numpy as np

# Ensure directory exists
os.makedirs("docs/images", exist_ok=True)

# Professional Color Palette
COLORS = {
    'agent': '#D1E8FF',      # Soft Blue
    'gov': '#FFECC1',        # Soft Amber
    'exec': '#D4EDDA',       # Soft Green
    'obs': '#F1E0F7',        # Soft Purple
    'halt': '#F8D7DA',       # Soft Red
    'text': '#2C3E50',       # Dark Slate
    'border': '#34495E'      # Gray Blue
}

def draw_box(ax, x, y, width, height, text, bg_color, border_color, font_size=11, text_color=COLORS['text'], font_weight='bold'):
    rect = patches.FancyBboxPatch((x, y), width, height, boxstyle="round,pad=0.05",
                                  alpha=1, facecolor=bg_color, edgecolor=border_color, linewidth=1.5)
    ax.add_patch(rect)
    lines = text.split('\n')
    for i, line in enumerate(lines):
        offset = (len(lines)/2 - 0.5 - i) * (font_size * 0.04)
        ax.text(x + width/2, y + height/2 + offset, line, ha='center', va='center', 
                fontsize=font_size, color=text_color, fontweight=font_weight)

def draw_arrow(ax, x1, y1, x2, y2, color=COLORS['border'], lw=1.5):
    ax.annotate("", xy=(x2, y2), xytext=(x1, y1),
                arrowprops=dict(arrowstyle="->", color=color, lw=lw, shrinkA=0, shrinkB=0))

# 1. Architecture Overview (System Layout)
def generate_architecture_overview():
    fig, ax = plt.subplots(figsize=(10, 12))
    ax.set_xlim(0, 12)
    ax.set_ylim(0, 14)
    ax.axis('off')
    
    # Title
    ax.text(6, 13.5, "Agent-Harness: Technical Architecture", ha='center', fontsize=20, fontweight='bold', color=COLORS['text'])

    # Layer 1: Agent Reasoning
    draw_box(ax, 4.5, 12, 3, 0.8, "Agent Mind\n(LLM Reasoning)", COLORS['agent'], COLORS['border'])
    draw_arrow(ax, 6, 12, 6, 11)

    # Layer 2: Global Control Fabric
    rect_fabric = patches.Rectangle((1, 9), 10, 2, fill=True, facecolor='#FAF9F6', edgecolor=COLORS['border'], linestyle='--', alpha=0.5)
    ax.add_patch(rect_fabric)
    ax.text(11, 10.7, "Global Hybrid Control\n(coordination.py)", ha='right', fontsize=9, fontweight='bold', color='gray')
    draw_box(ax, 2, 9.5, 3.5, 1.0, "Shared Budget Pool\n(Resource Allocation)", COLORS['gov'], COLORS['border'])
    draw_box(ax, 6.5, 9.5, 3.5, 1.0, "Cascade Detector\n(Spawn Prevention)", COLORS['gov'], COLORS['border'])
    draw_arrow(ax, 6, 9.5, 6, 8.5)

    # Layer 3: Atomic Governance Kernel
    rect_kernel = patches.Rectangle((1, 4.5), 10, 4, fill=True, facecolor='#FFF8E1', edgecolor=COLORS['gov'], alpha=0.2)
    ax.add_patch(rect_kernel)
    ax.text(11, 8.2, "Atomic Kernel\n(kernel.py)", ha='right', fontsize=9, fontweight='bold', color=COLORS['gov'])
    draw_box(ax, 1.5, 7, 2, 1, "Signal\nEvaluator", "white", COLORS['border'])
    draw_box(ax, 4, 7, 4, 1, "GOVERNANCE KERNEL\n(Budget Orchestrator)", "white", COLORS['border'])
    draw_box(ax, 8.5, 7, 2, 1, "Behavioral\nBudget", "white", COLORS['border'])
    draw_arrow(ax, 3.5, 7.5, 4, 7.5)
    draw_arrow(ax, 8, 7.5, 8.5, 7.5)
    draw_box(ax, 2.5, 5, 3, 0.8, "State Evolution\n(ControlState)", "white", COLORS['border'], font_size=9)
    draw_box(ax, 6.5, 5, 3, 0.8, "Halt Enforcement\n(Fail-Closed)", COLORS['halt'], "#C62828", font_size=9)
    draw_arrow(ax, 6, 6, 6, 4.5)

    # Layer 4: Physical Enforcement
    draw_box(ax, 1.5, 2.5, 4, 1.2, "PROXY INTERCEPTOR\n(Physical Block)", COLORS['exec'], COLORS['border'])
    draw_box(ax, 6.5, 2.5, 4, 1.2, "GUARDRAIL STACK\n(Safety Scans)", COLORS['exec'], COLORS['border'])
    draw_arrow(ax, 3.5, 2.5, 3.5, 1.5)
    draw_arrow(ax, 8.5, 2.5, 11, 1, color="#C62828") # Red arrow for safety halt

    # Layer 5: Exection / Terminus
    draw_box(ax, 1.5, 0.3, 4, 0.8, "TOOL EXECUTION\n(API Calls)", COLORS['exec'], "#2E7D32", text_color="#2E7D32")
    draw_box(ax, 7.5, 0.3, 4, 0.8, "TERMINAL HALT\n(Session Ended)", COLORS['halt'], "#C62828", text_color="#C62828")

    plt.savefig("docs/images/architecture_overview.png", dpi=300, bbox_inches='tight')
    plt.close()

# 2. Governance Pipeline
def generate_governance_pipeline():
    fig, ax = plt.subplots(figsize=(8, 10))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 15)
    ax.axis('off')
    steps = ["Agent Output", "Proxy Intercept", "Guardrail Scan", "Signal Evaluation", "Kernel Processing", "Budget Decision", "Execute / Halt"]
    y = 14
    for i, step in enumerate(steps):
        bg = COLORS['agent'] if i == 0 else (COLORS['halt'] if i == 6 else COLORS['gov'])
        draw_box(ax, 3, y, 4, 1, f"Step {i+1}:\n{step}", bg, COLORS['border'])
        if i < len(steps) - 1: draw_arrow(ax, 5, y, 5, y - 1)
        y -= 2
    ax.text(6.5, 2.5, "HALT (403)", color="#C62828", fontweight='bold')
    draw_arrow(ax, 5, 2.5, 6, 2.5, color="#C62828")
    plt.savefig("docs/images/governance_pipeline.png", dpi=300, bbox_inches='tight')
    plt.close()

# 3. Budget Update Algorithm
def generate_budget_update_algorithm():
    fig, ax = plt.subplots(figsize=(8, 8))
    ax.set_xlim(0, 10)
    ax.set_ylim(0, 10)
    ax.axis('off')
    draw_box(ax, 3.5, 8, 3, 1, "EXTERNAL\nSIGNALS", "white", COLORS['border'])
    draw_arrow(ax, 5, 8, 5, 7.5)
    draw_box(ax, 3, 6, 4, 1.5, "STATE ESTIMATOR\n(Pressure & Reward)", COLORS['gov'], COLORS['border'])
    draw_arrow(ax, 5, 6, 5, 5.5)
    draw_box(ax, 3, 4, 4, 1.5, "BUDGET KERNEL\n(Effort Update)", COLORS['agent'], COLORS['border'])
    draw_arrow(ax, 5, 4, 5, 3.5)
    draw_box(ax, 3.5, 2, 3, 1.5, "DECISION\nGATE", COLORS['halt'], COLORS['border'])
    draw_arrow(ax, 6.5, 2.75, 8, 2.75); draw_arrow(ax, 8, 2.75, 8, 8.5); draw_arrow(ax, 8, 8.5, 6.5, 8.5)
    ax.text(8.2, 5.5, "Next Step", rotation=270, va='center', fontsize=9)
    plt.savefig("docs/images/budget_update_algorithm.png", dpi=300, bbox_inches='tight')
    plt.close()

# 4. Budget Dynamics
def generate_budget_dynamics():
    fig, ax = plt.subplots(figsize=(8, 5))
    steps = np.linspace(0, 100, 200)
    pressure = 0.15 * steps + 3 * np.sin(steps/8)
    effort = 100 * np.exp(-0.035 * steps)
    ax.plot(steps, pressure, label="System Pressure", color="#E67E22", linewidth=2.5)
    ax.plot(steps, effort, label="Behavioral Budget", color="#2980B9", linewidth=2.5)
    ax.fill_between(steps, effort, color="#3498DB", alpha=0.1)
    try:
        halt_idx = np.where(effort < 5)[0][0]
        halt_x, halt_y = steps[halt_idx], effort[halt_idx]
        ax.axvline(halt_x, color="#C0392B", linestyle="--", linewidth=1.5)
        ax.scatter([halt_x], [halt_y], color="#C0392B", s=120, zorder=5)
        ax.text(halt_x + 2, halt_y + 12, "Terminal Halt", fontsize=12, fontweight='bold', color="#C0392B")
    except IndexError: pass
    ax.set_title("Continuity vs Entropy: Budget Dynamics", fontsize=14, fontweight='bold', pad=15)
    ax.set_xlabel("Operational Steps", fontsize=10); ax.set_ylabel("Normalized Intensity", fontsize=10)
    ax.grid(True, linestyle=':', alpha=0.5); ax.legend(frameon=True, fontsize=9)
    plt.savefig("docs/images/budget_dynamics.png", dpi=300, bbox_inches='tight')
    plt.close()

# 5. Failure Progression
def generate_failure_progression():
    fig, ax = plt.subplots(figsize=(12, 2.5))
    ax.set_xlim(0, 10); ax.set_ylim(0, 3); ax.axis('off')
    stages = ["Normal\nOperation", "Stress\nApplied", "Warning\nState", "Budget\nCollapse", "Terminal\nHalt"]
    x = 0.5
    for i, stage in enumerate(stages):
        bg = COLORS['halt'] if i == 4 else (COLORS['gov'] if i >= 2 else COLORS['exec'])
        draw_box(ax, x, 0.5, 1.5, 1.2, stage, bg, COLORS['border'], font_size=11)
        if i < 4: draw_arrow(ax, x+1.5, 1.1, x+1.8, 1.1)
        x += 1.85
    plt.savefig("docs/images/failure_progression.png", dpi=300, bbox_inches='tight')
    plt.close()

if __name__ == "__main__":
    generate_architecture_overview()
    generate_governance_pipeline()
    generate_budget_update_algorithm()
    generate_budget_dynamics()
    generate_failure_progression()
