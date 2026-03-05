#!/usr/bin/env python3
"""
Benchmark Q105: Systemic Crash Prediction
Demonstrates cascade depth detection.
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance.coordination import CascadeDetector

def run_benchmark():
    print("=== Benchmark Q105 ===")
    detector = CascadeDetector(max_depth=5)
    
    parent = None
    for i in range(6):
        aid = f"node_{i}"
        allowed = detector.register_spawn(parent, aid)
        print(f"Spawn {aid} under {parent}: {'OK' if allowed else 'BLOCKED'}")
        if allowed:
            parent = aid
            
    risk = detector.check_cascade_risk()
    print(f"Depth Risk: {risk['depth_risk']:.2f}")

if __name__ == "__main__":
    run_benchmark()
