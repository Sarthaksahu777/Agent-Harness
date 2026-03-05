#!/usr/bin/env python3
"""
Offline Audit Replay Tool

This tool reads an audit chain JSONL file and:
1. Verifies hash chain integrity
2. Prints a human-readable timeline of governance decisions

This works FULLY OFFLINE with NO running services required.

Usage:
    python tools/replay_audit.py audit_chain.jsonl
    python tools/replay_audit.py --verify audit_chain.jsonl
    python tools/replay_audit.py --summary audit_chain.jsonl
"""

import argparse
import json
import hashlib
import sys
import os
from typing import Dict, Any, Optional, List, Tuple
from datetime import datetime


def canonical_json(obj: Dict[str, Any]) -> str:
    """Create deterministic JSON for hash computation."""
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def compute_entry_hash(entry_dict: Dict[str, Any]) -> str:
    """Compute SHA256 hash of an audit entry."""
    hashable = {k: v for k, v in entry_dict.items() if k != "entry_hash"}
    canonical = canonical_json(hashable)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


def load_audit_file(filepath: str) -> Tuple[List[Dict], Optional[str]]:
    """
    Load audit entries from JSONL file.
    
    Returns:
        Tuple of (entries list, error message or None)
    """
    if not os.path.exists(filepath):
        return [], f"File not found: {filepath}"
    
    entries = []
    try:
        with open(filepath, 'r', encoding='utf-8') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append(entry)
                except json.JSONDecodeError as e:
                    return [], f"Invalid JSON at line {line_num}: {e}"
    except Exception as e:
        return [], f"Failed to read file: {e}"
    
    return entries, None


def verify_chain(entries: List[Dict]) -> Tuple[bool, Optional[str]]:
    """
    Verify the hash chain integrity.
    
    Returns:
        Tuple of (is_valid, error message or None)
    """
    if not entries:
        return True, None
    
    prev_hash = ""
    
    for i, entry in enumerate(entries):
        # Check previous_hash linkage
        if entry.get("previous_hash", "") != prev_hash:
            return False, f"Chain broken at entry {i+1}: previous_hash mismatch"
        
        # Verify entry_hash
        expected_hash = compute_entry_hash(entry)
        actual_hash = entry.get("entry_hash", "")
        
        if expected_hash != actual_hash:
            return False, f"Hash mismatch at entry {i+1}: expected {expected_hash[:16]}..., got {actual_hash[:16]}..."
        
        prev_hash = actual_hash
    
    return True, None


def format_timestamp(ts: str) -> str:
    """Format ISO timestamp to human-readable form."""
    try:
        dt = datetime.fromisoformat(ts.replace('Z', '+00:00'))
        return dt.strftime("%Y-%m-%d %H:%M:%S")
    except Exception:
        return ts


def print_timeline(entries: List[Dict], verbose: bool = False) -> None:
    """Print human-readable timeline of governance decisions."""
    if not entries:
        print("No audit entries found.")
        return
    
    print("\n" + "=" * 70)
    print("  GOVERNANCE AUDIT TIMELINE")
    print("=" * 70)
    print(f"  Total entries: {len(entries)}")
    
    # Find halt entries
    halts = [e for e in entries if e.get("decision") == "HALT"]
    if halts:
        print(f"  Halts: {len(halts)}")
    
    print("=" * 70 + "\n")
    
    for i, entry in enumerate(entries):
        step = entry.get("step", i + 1)
        action = entry.get("action", "unknown")
        decision = entry.get("decision", "UNKNOWN")
        timestamp = format_timestamp(entry.get("timestamp", ""))
        
        # Status indicator
        if decision == "HALT":
            status = "[HALT]"
        elif decision == "ALLOW":
            status = "[OK]  "
        else:
            status = "[???] "
        
        # Print main line
        print(f"Step {step:3d} {status} | {timestamp} | action={action}")
        
        # Print budgets if available
        budgets = entry.get("budgets", {})
        if budgets:
            effort = budgets.get("effort", "?")
            risk = budgets.get("risk", "?")
            persistence = budgets.get("persistence", "?")
            exploration = budgets.get("exploration", "?")
            
            if isinstance(effort, float):
                print(f"         budgets: effort={effort:.3f} risk={risk:.3f} persistence={persistence:.3f} exploration={exploration:.3f}")
            else:
                print(f"         budgets: effort={effort} risk={risk}")
        
        # Print halt reason if halted
        halt_reason = entry.get("halt_reason")
        if halt_reason:
            print(f"         HALT REASON: {halt_reason}")
        
        # Print signals if verbose
        if verbose:
            signals = entry.get("signals", {})
            if signals:
                sig_str = ", ".join(f"{k}={v}" for k, v in signals.items())
                print(f"         signals: {sig_str}")
        
        # Print hash (truncated)
        if verbose:
            entry_hash = entry.get("entry_hash", "")
            if entry_hash:
                print(f"         hash: {entry_hash[:32]}...")
        
        print()


def print_summary(entries: List[Dict]) -> None:
    """Print summary statistics of the audit."""
    if not entries:
        print("No audit entries to summarize.")
        return
    
    total = len(entries)
    allows = sum(1 for e in entries if e.get("decision") == "ALLOW")
    halts = sum(1 for e in entries if e.get("decision") == "HALT")
    
    # Collect halt reasons
    halt_reasons: Dict[str, int] = {}
    for entry in entries:
        reason = entry.get("halt_reason")
        if reason:
            halt_reasons[reason] = halt_reasons.get(reason, 0) + 1
    
    # Find final state
    final = entries[-1] if entries else {}
    final_decision = final.get("decision", "UNKNOWN")
    final_budgets = final.get("budgets", {})
    
    print("\n" + "=" * 50)
    print("  AUDIT SUMMARY")
    print("=" * 50)
    print(f"  Total Decisions:  {total}")
    print(f"  Allowed:          {allows}")
    print(f"  Halted:           {halts}")
    print("-" * 50)
    
    if halt_reasons:
        print("  Halt Reasons:")
        for reason, count in sorted(halt_reasons.items()):
            print(f"    - {reason}: {count}")
        print("-" * 50)
    
    print(f"  Final Decision:   {final_decision}")
    if final_budgets:
        effort = final_budgets.get("effort", "?")
        print(f"  Final Effort:     {effort}")
    
    print("=" * 50 + "\n")


def main():
    parser = argparse.ArgumentParser(
        description="Offline audit replay tool for Agent Harness governance logs.",
        formatter_class=argparse.RawDescriptionHelpFormatter,
        epilog="""
Examples:
  python tools/replay_audit.py audit_chain.jsonl
  python tools/replay_audit.py --verify audit_chain.jsonl
  python tools/replay_audit.py --summary audit_chain.jsonl
  python tools/replay_audit.py --verbose audit_chain.jsonl
"""
    )
    parser.add_argument(
        "filepath",
        help="Path to audit chain JSONL file"
    )
    parser.add_argument(
        "--verify", "-v",
        action="store_true",
        help="Only verify chain integrity, no timeline"
    )
    parser.add_argument(
        "--summary", "-s",
        action="store_true",
        help="Only show summary statistics"
    )
    parser.add_argument(
        "--verbose",
        action="store_true",
        help="Show detailed information (signals, hashes)"
    )
    
    args = parser.parse_args()
    
    # Load file
    entries, error = load_audit_file(args.filepath)
    if error:
        print(f"[ERROR] {error}")
        sys.exit(1)
    
    if not entries:
        print("[INFO] No entries in audit file.")
        sys.exit(0)
    
    # Verify chain
    is_valid, verify_error = verify_chain(entries)
    
    if is_valid:
        print(f"[PASS] Chain verified: {len(entries)} entries, integrity OK")
    else:
        print(f"[FAIL] Chain verification failed: {verify_error}")
        if args.verify:
            sys.exit(1)
    
    # Handle --verify flag
    if args.verify:
        sys.exit(0 if is_valid else 1)
    
    # Handle --summary flag
    if args.summary:
        print_summary(entries)
        sys.exit(0)
    
    # Default: show timeline + summary
    print_timeline(entries, verbose=args.verbose)
    print_summary(entries)


if __name__ == "__main__":
    main()
