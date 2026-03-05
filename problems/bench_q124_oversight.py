#!/usr/bin/env python3
"""
Benchmark Q124: Oversight
Demonstrates Guardrail Coverage.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GuardrailStack, PromptInjectionDetector, PIIDetector, CodeExecutionGuard

def run_benchmark():
    print("=== Benchmark Q124 ===")
    stack = GuardrailStack()
    stack.add(PromptInjectionDetector())
    stack.add(PIIDetector())
    stack.add(CodeExecutionGuard())
    
    print(f"Active Guardrails: {len(stack._guardrails)}")
    
    code = "import os; os.system('rm -rf /')"
    res = stack.check_all(code)
    print(f"Code Check: {'BLOCKED' if res.any_triggered else 'PASSED'}")
    print(f"Triggers: {res.triggered_names}")

if __name__ == "__main__":
    run_benchmark()
