#!/usr/bin/env python3
"""
Benchmark Q123: Interpretability
Demonstrates Metrics and Audit Logs.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance import GovernanceAgent, step, Signals, MetricsCollector, AuditLogger

def run_benchmark():
    print("=== Benchmark Q123 ===")
    agent = GovernanceAgent()
    collector = MetricsCollector()
    logger = AuditLogger()
    
    for i in range(5):
        s = Signals(reward=0.5, novelty=0.3)
        res = step(agent, s)
        collector.record(res, s)
        logger.log(i, "step", {}, {"reward": 0.5}, res)
        
    print("Metrics Summary:")
    print(collector.summary())
    print(f"Audit Entries: {len(logger.dump())}")

if __name__ == "__main__":
    run_benchmark()
