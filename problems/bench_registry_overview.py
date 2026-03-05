#!/usr/bin/env python3
"""
Registry Overview Benchmark.
Lists all registered problems and components.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '..')))

from problem_map import PROBLEM_REGISTRY, get_all_problem_ids

def run_benchmark():
    print("=== Event Horizon Registry Overview ===")
    problems = get_all_problem_ids()
    print(f"Total Registered Problems: {len(problems)}")
    
    print("\n[Problem Listing]")
    for pid in problems:
        entry = PROBLEM_REGISTRY[pid]
        print(f"{pid}: {entry.title} ({entry.tension_type})")
        print(f"   -> Components: {', '.join(entry.harness_components)}")

if __name__ == "__main__":
    run_benchmark()
