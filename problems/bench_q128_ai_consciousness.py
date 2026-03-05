#!/usr/bin/env python3
"""
Benchmark Q128: AI Consciousness
Demonstrates state integration and thresholds.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals, MetricsCollector

def run_benchmark():
    print("=== Benchmark Q128 ===")
    agent = GovernanceAgent()
    collector = MetricsCollector()
    
    print("Processing integrated information...")
    for i in range(5):
        s = Signals(reward=0.5, novelty=0.5, urgency=0.5)
        res = step(agent, s)
        collector.record(res, s)
        print(f"Step {i}: Integrated State={res.state}")
        
    print(f"Summary: {collector.summary()}")

if __name__ == "__main__":
    run_benchmark()
