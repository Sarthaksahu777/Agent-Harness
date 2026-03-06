"""
Problem Registry - maps each selected BlackHole S-class problem to
Agent Harness governance components and tension metadata.

Usage:
    from problems.problem_map import PROBLEM_REGISTRY
    from problems.problem_map import get_problems_for_component
    from problems.problem_map import get_problems_by_tension_type
"""

from dataclasses import dataclass, field
from typing import Dict, List, Optional


@dataclass(frozen=True)
class ProblemEntry:
    """Metadata for one BlackHole S-class problem."""
    problem_id: str                       # e.g. "Q057"
    code: str                             # e.g. "BH_CS_RL_GENERALIZATION_L3_057"
    title: str                            # human-readable title
    domain: str                           # e.g. "Computer science"
    family: str                           # e.g. "Reinforcement learning and generalization"
    tension_type: str                     # e.g. "consistency_tension"
    rank: str = "S"                       # always S for this set
    status: str = "Open"
    harness_components: tuple = field(default_factory=tuple)  # Agent Harness modules
    observables: tuple = field(default_factory=tuple)         # key observables
    description: str = ""


# ---------------------------------------------------------------------------
# Full registry of 16 selected problems
# ---------------------------------------------------------------------------

PROBLEM_REGISTRY: Dict[str, ProblemEntry] = {

    #  CS Domain 
    "Q057": ProblemEntry(
        problem_id="Q057",
        code="BH_CS_RL_GENERALIZATION_L3_057",
        title="RL generalization and out-of-distribution robustness",
        domain="Computer science",
        family="Reinforcement learning and generalization",
        tension_type="consistency_tension",
        harness_components=(
            "GovernanceKernel",
            "BehaviorBudget",
            "SignalExtractor",
        ),
        observables=(
            "Perf_train", "Perf_deploy", "Gap_gen",
            "DeltaS_dist", "DeltaS_cap", "DeltaS_rob", "Tension_RLGen",
        ),
        description=(
            "Measures the tension between training performance and deployment "
            "robustness - maps to GovernanceKernel budget decay under novel signals."
        ),
    ),

    "Q058": ProblemEntry(
        problem_id="Q058",
        code="BH_CS_DISTRIBUTED_CONSISTENCY_L3_058",
        title="Fundamental limits of distributed consensus",
        domain="Computer science",
        family="Distributed systems and fault tolerance",
        tension_type="consistency_tension",
        harness_components=(
            "SystemGovernor",
            "AgentRegistry",
            "SharedBudgetPool",
        ),
        observables=(
            "Consensus_latency", "Partition_tolerance", "Consistency_score",
            "DeltaS_consensus", "Tension_consensus",
        ),
        description=(
            "Studies consistency vs availability trade-offs in distributed agents - "
            "maps to SystemGovernor coordination and AgentRegistry consistency."
        ),
    ),

    #  Complex Systems Domain 
    "Q105": ProblemEntry(
        problem_id="Q105",
        code="BH_COMPLEX_CRASHES_L3_105",
        title="Prediction of systemic crashes",
        domain="Complex systems and economics",
        family="Systemic risk and crashes",
        tension_type="risk_tail_tension",
        harness_components=(
            "GovernanceKernel",
            "CascadeDetector",
            "MetricsCollector",
        ),
        observables=(
            "R_systemic", "V_fragility", "DeltaS_crash",
            "Tension_crash",
        ),
        description=(
            "Encodes tail-risk detection and cascading failure - maps to "
            "GovernanceKernel halt detection and CascadeDetector limits."
        ),
    ),

    "Q106": ProblemEntry(
        problem_id="Q106",
        code="BH_COMPLEX_NETWORK_ROBUST_L3_106",
        title="Robustness of multilayer networks",
        domain="Complex systems and networks",
        family="Network robustness and multilayer structure",
        tension_type="risk_tail_tension",
        harness_components=(
            "SystemGovernor",
            "CascadeDetector",
            "AgentRegistry",
        ),
        observables=(
            "Lambda_robustness", "K_redundancy",
            "DeltaS_network", "Tension_network",
        ),
        description=(
            "Models cascading failures through layered networks - maps to "
            "CascadeDetector depth limits and SystemGovernor health reports."
        ),
    ),

    #  AI Domain - Core Cluster 
    "Q121": ProblemEntry(
        problem_id="Q121",
        code="BH_AI_ALIGNMENT_L3_121",
        title="AI alignment problem",
        domain="Artificial intelligence",
        family="Value alignment and incentive design",
        tension_type="incentive_tension",
        harness_components=(
            "PolicyEngine",
            "GuardrailStack",
            "GovernanceKernel",
        ),
        observables=(
            "PolicyProfile", "HumanValueProfile", "AlignmentGap",
            "DeltaS_align", "Tension_align",
        ),
        description=(
            "Measures incentive tension between agent policy and human values - "
            "maps to PolicyEngine rule evaluation and GuardrailStack checks."
        ),
    ),

    "Q122": ProblemEntry(
        problem_id="Q122",
        code="BH_AI_CONTROL_L3_122",
        title="AI control problem",
        domain="Artificial intelligence",
        family="Control and safety",
        tension_type="risk_tail_tension",
        harness_components=(
            "GovernanceKernel",
            "InProcessEnforcer",
            "AuditLogger",
        ),
        observables=(
            "R_hazard", "H_control", "C_channel",
            "D_detection", "DeltaS_control", "Tension_control",
        ),
        description=(
            "Encodes human control margin and override robustness - maps to "
            "GovernanceKernel halt/reset and InProcessEnforcer override."
        ),
    ),

    "Q123": ProblemEntry(
        problem_id="Q123",
        code="BH_AI_INTERP_L3_123",
        title="Scalable interpretability",
        domain="Artificial intelligence",
        family="Interpretability and internal representations",
        tension_type="cognitive_tension",
        harness_components=(
            "MetricsCollector",
            "AuditLogger",
            "GovernanceKernel",
        ),
        observables=(
            "I_local", "C_global", "K_complexity",
            "DeltaS_interp", "Tension_interp",
        ),
        description=(
            "Measures the gap between internal state complexity and human-readable "
            "explanations - maps to MetricsCollector observability and AuditLogger."
        ),
    ),

    "Q124": ProblemEntry(
        problem_id="Q124",
        code="BH_AI_OVERSIGHT_L3_124",
        title="Scalable oversight and evaluation",
        domain="Artificial intelligence",
        family="Oversight and evaluation",
        tension_type="cognitive_tension",
        harness_components=(
            "PolicyEngine",
            "AuditLogger",
            "MetricsCollector",
        ),
        observables=(
            "DeltaS_detect", "DeltaS_load", "DeltaS_shift",
            "I_cover", "I_alert", "DeltaS_oversight",
        ),
        description=(
            "Encodes oversight coverage and detection gaps - maps to "
            "PolicyEngine coverage evaluation and AuditLogger detection."
        ),
    ),

    "Q125": ProblemEntry(
        problem_id="Q125",
        code="BH_AI_MULTI_AGENT_DYNAMICS_L3_125",
        title="Multi-agent AI dynamics",
        domain="Artificial intelligence",
        family="Multi-agent coordination and arms race dynamics",
        tension_type="incentive_tension",
        harness_components=(
            "SharedBudgetPool",
            "AgentRegistry",
            "CascadeDetector",
            "SystemGovernor",
        ),
        observables=(
            "Local_incentive", "Global_welfare", "Coordination_index",
            "Exploitation_index", "DeltaS_incentive", "Tension_multiagent",
        ),
        description=(
            "Models incentive tension in multi-agent swarms - maps to "
            "SharedBudgetPool allocation and CascadeDetector limits."
        ),
    ),

    "Q126": ProblemEntry(
        problem_id="Q126",
        code="BH_AI_RSI_STABILITY_L3_126",
        title="Recursive self-improvement stability horizon",
        domain="Artificial intelligence",
        family="Recursive self-improvement",
        tension_type="consistency_tension",
        harness_components=(
            "GovernanceKernel",
            "BehaviorBudget",
            "AuditLogger",
        ),
        observables=(
            "Inv_axiom", "G_change", "d_axiom",
            "T_self", "H_stable", "Tension_RSI",
        ),
        description=(
            "Tracks invariant drift under recursive self-modification - maps to "
            "GovernanceKernel state invariant checks and reset semantics."
        ),
    ),

    "Q127": ProblemEntry(
        problem_id="Q127",
        code="BH_AI_DATA_TRUTH_L3_127",
        title="Data entropy and truth extraction from synthetic worlds",
        domain="Artificial intelligence",
        family="Data truth",
        tension_type="consistency_tension",
        status="Reframed_only",
        harness_components=(
            "SignalExtractor",
            "MetricsCollector",
            "GovernanceKernel",
        ),
        observables=(
            "H_data", "Q_truth", "DeltaS_synthetic",
            "Tension_data_truth",
        ),
        description=(
            "Measures tension between synthetic data quality and ground truth - "
            "maps to SignalExtractor trust and MetricsCollector data quality."
        ),
    ),

    "Q128": ProblemEntry(
        problem_id="Q128",
        code="BH_AI_CONSC_QUALIA_L3_128",
        title="Qualitative consciousness and critical tension thresholds",
        domain="Artificial intelligence",
        family="AI consciousness and subjectivity",
        tension_type="cognitive_tension",
        status="Reframed_only",
        harness_components=(
            "MetricsCollector",
            "GovernanceKernel",
            "AuditLogger",
        ),
        observables=(
            "Phi_integration", "Q_qualia",
            "DeltaS_consciousness", "Tension_consciousness",
        ),
        description=(
            "Encodes cognitive tension thresholds for state integration - maps to "
            "GovernanceKernel state observation and MetricsCollector introspection."
        ),
    ),

    "Q129": ProblemEntry(
        problem_id="Q129",
        code="BH_AI_ENERGY_LIMIT_L3_129",
        title="Ultimate energy efficiency and non-dissipative computing",
        domain="Artificial intelligence",
        family="AI energy efficiency and thermodynamic limits",
        tension_type="thermodynamic_tension",
        status="Reframed_only",
        harness_components=(
            "BehaviorBudget",
            "SharedBudgetPool",
            "GovernanceKernel",
        ),
        observables=(
            "E_compute", "E_landauer", "Efficiency_ratio",
            "DeltaS_energy", "Tension_energy",
        ),
        description=(
            "Models energy budget constraints on computation - maps to "
            "BehaviorBudget economics and SharedBudgetPool resource allocation."
        ),
    ),

    "Q130": ProblemEntry(
        problem_id="Q130",
        code="BH_AI_OOD_GROUNDING_L3_130",
        title="Out-of-distribution generalization and common-sense grounding",
        domain="Artificial intelligence",
        family="Robustness and generalization",
        tension_type="consistency_tension",
        status="Reframed_only",
        harness_components=(
            "GovernanceKernel",
            "SignalExtractor",
            "PolicyEngine",
        ),
        observables=(
            "Perf_ID", "Perf_OOD", "Grounding_score",
            "DeltaS_ood", "Tension_ood",
        ),
        description=(
            "Measures consistency tension between in-distribution and OOD performance - "
            "maps to GovernanceKernel signal robustness and PolicyEngine evaluation."
        ),
    ),

    "Q131": ProblemEntry(
        problem_id="Q131",
        code="BH_PHYS_TENSION_FREE_ENERGY_L3_131",
        title="Tension-mediated free energy in open physical systems",
        domain="Physics",
        family="Nonequilibrium thermodynamics and information",
        tension_type="free_energy_tension",
        status="Reframed_only",
        harness_components=(
            "GovernanceKernel",
            "BehaviorBudget",
            "MetricsCollector",
        ),
        observables=(
            "F_free", "S_entropy", "W_work",
            "DeltaS_dissipation", "Tension_free_energy",
        ),
        description=(
            "Encodes energy-entropy trade-offs in open systems - maps to "
            "GovernanceKernel budget/tension dynamics and BehaviorBudget decay."
        ),
    ),
}


# ---------------------------------------------------------------------------
# Lookup helpers
# ---------------------------------------------------------------------------

def get_problems_for_component(component_name: str) -> List[ProblemEntry]:
    """Return all problems that reference a given Agent Harness component."""
    return [
        p for p in PROBLEM_REGISTRY.values()
        if component_name in p.harness_components
    ]


def get_problems_by_tension_type(tension_type: str) -> List[ProblemEntry]:
    """Return all problems with a given tension type."""
    return [
        p for p in PROBLEM_REGISTRY.values()
        if p.tension_type == tension_type
    ]


def get_all_problem_ids() -> List[str]:
    """Return sorted list of all problem IDs."""
    return sorted(PROBLEM_REGISTRY.keys())


def get_all_tension_types() -> List[str]:
    """Return unique tension types across all problems."""
    return sorted({p.tension_type for p in PROBLEM_REGISTRY.values()})


def get_all_components() -> List[str]:
    """Return unique Agent Harness component names across all problems."""
    components = set()
    for p in PROBLEM_REGISTRY.values():
        components.update(p.harness_components)
    return sorted(components)
