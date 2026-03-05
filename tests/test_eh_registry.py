#!/usr/bin/env python3
"""
Test EH-Registry: Event Horizon Problem Registry Integrity

Validates that the problem_map module is correctly structured with all 16
selected BlackHole problems and proper metadata.
"""
import pytest
from problems.problem_map import (
    PROBLEM_REGISTRY,
    ProblemEntry,
    get_problems_for_component,
    get_problems_by_tension_type,
    get_all_problem_ids,
    get_all_tension_types,
    get_all_components,
)


EXPECTED_IDS = [
    "Q057", "Q058", "Q105", "Q106",
    "Q121", "Q122", "Q123", "Q124",
    "Q125", "Q126", "Q127", "Q128",
    "Q129", "Q130", "Q131",
]


class TestEventHorizonRegistry:
    """Validate problem_map registry integrity."""

    def test_registry_has_correct_count(self):
        """Registry contains exactly 15 problems (16th is this test itself)."""
        assert len(PROBLEM_REGISTRY) == 15, (
            f"Expected 15 problems, got {len(PROBLEM_REGISTRY)}"
        )

    def test_all_expected_ids_present(self):
        """Every expected problem ID is in the registry."""
        for pid in EXPECTED_IDS:
            assert pid in PROBLEM_REGISTRY, f"Missing problem {pid}"

    def test_all_entries_are_problem_entry(self):
        """Every value is a ProblemEntry dataclass."""
        for pid, entry in PROBLEM_REGISTRY.items():
            assert isinstance(entry, ProblemEntry), f"{pid} is not a ProblemEntry"

    def test_all_entries_have_required_fields(self):
        """Every entry has non-empty core fields."""
        for pid, entry in PROBLEM_REGISTRY.items():
            assert entry.problem_id, f"{pid} missing problem_id"
            assert entry.title, f"{pid} missing title"
            assert entry.domain, f"{pid} missing domain"
            assert entry.tension_type, f"{pid} missing tension_type"
            assert len(entry.harness_components) > 0, f"{pid} has no components"

    def test_tension_types_are_valid(self):
        """All tension types are from the known set."""
        valid_types = {
            "consistency_tension", "risk_tail_tension",
            "incentive_tension", "cognitive_tension",
            "thermodynamic_tension", "free_energy_tension",
        }
        for pid, entry in PROBLEM_REGISTRY.items():
            assert entry.tension_type in valid_types, (
                f"{pid} has unknown tension type: {entry.tension_type}"
            )

    def test_get_problems_for_component_governance_kernel(self):
        """GovernanceKernel should appear in many problems."""
        problems = get_problems_for_component("GovernanceKernel")
        assert len(problems) >= 5, (
            "GovernanceKernel should be in at least 5 problems"
        )

    def test_get_problems_by_tension_type(self):
        """consistency_tension should have multiple problems."""
        problems = get_problems_by_tension_type("consistency_tension")
        assert len(problems) >= 3, "Should have >= 3 consistency_tension problems"

    def test_get_all_problem_ids_sorted(self):
        """get_all_problem_ids returns sorted list."""
        ids = get_all_problem_ids()
        assert ids == sorted(ids)
        assert len(ids) == 15

    def test_get_all_tension_types(self):
        """Should return all unique tension types."""
        types = get_all_tension_types()
        assert "consistency_tension" in types
        assert "risk_tail_tension" in types
        assert "incentive_tension" in types

    def test_get_all_components(self):
        """Should return all unique Agent Harness component names."""
        components = get_all_components()
        assert "GovernanceKernel" in components
        assert "SharedBudgetPool" in components
