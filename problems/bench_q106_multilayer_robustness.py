#!/usr/bin/env python3
"""
Benchmark Q106: Multilayer Robustness
"""
import sys, os
sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), '../../src')))

from governance.coordination import SystemGovernor, CascadeDetector

def run_benchmark():
    print("=== Benchmark Q106 ===")
    governor = SystemGovernor(
        cascade_detector=CascadeDetector(max_depth=3),
        halt_on_cascade=True
    )
    
    print("Registering root...")
    governor.register_agent("root")
    
    parent = "root"
    for i in range(4):
        aid = f"child_{i}"
        success = governor.register_agent(aid, parent_id=parent)
        print(f"Spawn {aid} under {parent}: {'OK' if success else 'BLOCKED'}")
        if success:
            parent = aid

if __name__ == "__main__":
    run_benchmark()
