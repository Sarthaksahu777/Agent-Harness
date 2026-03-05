"""
Audit System for Governance Kernel with Hash Chaining.

Records an immutable, append-only log of every governance decision and action attempt.
Essential for reconstructability and compliance.

Hash Chaining:
- Each entry includes previous_hash (hash of previous entry)
- Each entry includes entry_hash (SHA256 of canonical JSON)
- Chain can be verified for tampering detection

Usage:
    # Basic logging
    logger = AuditLogger()
    logger.log(step=1, action="llm_call", params={}, signals={}, result=result)
    
    # With hash chaining and persistence
    logger = HashChainedAuditLogger(filepath="audit_chain.jsonl")
    logger.log(step=1, action="llm_call", params={}, signals={}, result=result)
    
    # Verification
    python -m governance.audit verify audit_chain.jsonl
"""

import json
import hashlib
import sys
import dataclasses
from dataclasses import dataclass, field
from datetime import datetime, timezone
from typing import Any, Dict, List, Optional, Union
from pathlib import Path

# Handle import when run as module vs imported
try:
    from governance.result import EngineResult
except ImportError:
    import os
    sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
    from governance.result import EngineResult


@dataclass
class AuditEntry:
    """
    Immutable record of a single governance event.
    
    Hash Chaining Fields:
    - previous_hash: SHA256 of the previous entry (empty string for first entry)
    - entry_hash: SHA256 of this entry's canonical JSON (excluding entry_hash itself)
    """
    timestamp: str
    step: int
    action: str
    params: Dict[str, Any]
    signals: Dict[str, float]
    budget_snapshot: Dict[str, float]
    decision_halted: bool
    halt_reason: Optional[str]
    # Hash chaining fields
    previous_hash: str = ""
    entry_hash: str = ""


def canonical_json(obj: Dict[str, Any]) -> str:
    """
    Produce canonical JSON for hashing.
    
    Uses sorted keys and no extra whitespace to ensure determinism.
    """
    return json.dumps(obj, sort_keys=True, separators=(',', ':'))


def compute_entry_hash(entry_dict: Dict[str, Any]) -> str:
    """
    Compute SHA256 hash of an entry (excluding entry_hash field).
    """
    # Create a copy without entry_hash
    hashable = {k: v for k, v in entry_dict.items() if k != "entry_hash"}
    canonical = canonical_json(hashable)
    return hashlib.sha256(canonical.encode('utf-8')).hexdigest()


class AuditLogger:
    """
    In-memory audit logger (original implementation).
    """
    def __init__(self):
        self._entries: List[AuditEntry] = []

    def log(self, 
            step: int, 
            action: str, 
            params: Dict[str, Any], 
            signals: Dict[str, float], 
            result: EngineResult) -> None:
        """
        Record a governance event.
        
        Args:
            step: Current harness step
            action: Name of the action being attempted
            params: Parameters for the action
            signals: The input signals passed to kernel
            result: The output result from kernel
        """
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            step=step,
            action=action,
            params=params,
            signals=signals,
            budget_snapshot=dataclasses.asdict(result.budget),
            decision_halted=result.halted,
            halt_reason=result.reason
        )
        self._entries.append(entry)

    def dump(self) -> List[Dict[str, Any]]:
        """
        Return all entries as a list of dictionaries (JSON-serializable).
        """
        return [dataclasses.asdict(entry) for entry in self._entries]

    def dump_json(self, filepath: Optional[str] = None) -> str:
        """
        Serialize to JSON string, optionally writing to a file.
        """
        data = self.dump()
        json_str = json.dumps(data, indent=2)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(json_str)
                
        return json_str


class HashChainedAuditLogger:
    """
    Audit logger with SHA256 hash chaining for tamper detection.
    
    Features:
    - Each entry is hashed and linked to the previous
    - Entries are persisted to JSONL file (append-only)
    - Chain can be verified for integrity
    
    Hash Chain Structure:
        Entry[0]: previous_hash = "", entry_hash = SHA256(entry_0)
        Entry[1]: previous_hash = entry_0.entry_hash, entry_hash = SHA256(entry_1)
        Entry[N]: previous_hash = entry_N-1.entry_hash, entry_hash = SHA256(entry_N)
    """
    
    def __init__(self, filepath: Optional[str] = None):
        """
        Initialize hash-chained audit logger.
        
        Args:
            filepath: Path to JSONL file for persistence (optional)
        """
        self._entries: List[AuditEntry] = []
        self._filepath = filepath
        self._last_hash = ""
        self._entries_written = 0
        
        # Load existing entries if file exists
        if filepath and Path(filepath).exists():
            self._load_existing()
    
    def _load_existing(self) -> None:
        """Load existing entries from file."""
        with open(self._filepath, 'r') as f:
            for line in f:
                line = line.strip()
                if line:
                    entry_dict = json.loads(line)
                    entry = AuditEntry(**entry_dict)
                    self._entries.append(entry)
                    self._last_hash = entry.entry_hash
                    self._entries_written += 1
    
    def log(self,
            step: int,
            action: str,
            params: Dict[str, Any],
            signals: Dict[str, float],
            result: EngineResult) -> AuditEntry:
        """
        Record a governance event with hash chaining.
        
        Args:
            step: Current harness step
            action: Name of the action being attempted
            params: Parameters for the action
            signals: The input signals passed to kernel
            result: The output result from kernel
            
        Returns:
            The created AuditEntry with computed hashes
        """
        # Create entry without hashes first
        entry = AuditEntry(
            timestamp=datetime.now(timezone.utc).isoformat(),
            step=step,
            action=action,
            params=params,
            signals=signals,
            budget_snapshot=dataclasses.asdict(result.budget),
            decision_halted=result.halted,
            halt_reason=result.reason,
            previous_hash=self._last_hash,
            entry_hash="",  # Will compute below
        )
        
        # Convert to dict and compute hash
        entry_dict = dataclasses.asdict(entry)
        entry_hash = compute_entry_hash(entry_dict)
        
        # Create final entry with hash
        entry = AuditEntry(
            timestamp=entry.timestamp,
            step=entry.step,
            action=entry.action,
            params=entry.params,
            signals=entry.signals,
            budget_snapshot=entry.budget_snapshot,
            decision_halted=entry.decision_halted,
            halt_reason=entry.halt_reason,
            previous_hash=entry.previous_hash,
            entry_hash=entry_hash,
        )
        
        self._entries.append(entry)
        self._last_hash = entry_hash
        
        # Persist to file (append-only)
        if self._filepath:
            self._append_to_file(entry)
        
        self._entries_written += 1
        return entry
    
    def _append_to_file(self, entry: AuditEntry) -> None:
        """Append a single entry to the JSONL file."""
        with open(self._filepath, 'a') as f:
            f.write(json.dumps(dataclasses.asdict(entry)) + '\n')
    
    def dump(self) -> List[Dict[str, Any]]:
        """Return all entries as a list of dictionaries."""
        return [dataclasses.asdict(entry) for entry in self._entries]
    
    def dump_jsonl(self, filepath: Optional[str] = None) -> str:
        """
        Export to JSONL format.
        
        Args:
            filepath: If provided, write to file
            
        Returns:
            JSONL string
        """
        lines = [json.dumps(dataclasses.asdict(e)) for e in self._entries]
        content = '\n'.join(lines)
        
        if filepath:
            with open(filepath, 'w') as f:
                f.write(content + '\n')
        
        return content
    
    @property
    def entries_written(self) -> int:
        """Get count of entries written."""
        return self._entries_written
    
    @staticmethod
    def verify_chain(filepath: str) -> tuple[bool, Optional[str]]:
        """
        Verify the integrity of an audit chain file.
        
        Args:
            filepath: Path to the JSONL audit chain file
            
        Returns:
            Tuple of (is_valid, error_message)
            - (True, None) if chain is valid
            - (False, error_msg) if chain is invalid
        """
        if not Path(filepath).exists():
            return False, f"File not found: {filepath}"
        
        entries = []
        with open(filepath, 'r') as f:
            for line_num, line in enumerate(f, 1):
                line = line.strip()
                if not line:
                    continue
                try:
                    entry = json.loads(line)
                    entries.append((line_num, entry))
                except json.JSONDecodeError as e:
                    return False, f"Invalid JSON on line {line_num}: {e}"
        
        if not entries:
            return True, None  # Empty file is valid
        
        previous_hash = ""
        
        for line_num, entry in entries:
            # Check previous_hash linkage
            if entry.get("previous_hash", "") != previous_hash:
                return False, (
                    f"Line {line_num}: previous_hash mismatch. "
                    f"Expected '{previous_hash[:16]}...', "
                    f"got '{entry.get('previous_hash', '')[:16]}...'"
                )
            
            # Verify entry_hash
            stored_hash = entry.get("entry_hash", "")
            computed_hash = compute_entry_hash(entry)
            
            if stored_hash != computed_hash:
                return False, (
                    f"Line {line_num}: entry_hash mismatch. "
                    f"Stored '{stored_hash[:16]}...', "
                    f"computed '{computed_hash[:16]}...'"
                )
            
            previous_hash = stored_hash
        
        return True, None


# =============================================================================
# CLI Verification Tool
# =============================================================================

def main():
    """CLI entry point for audit chain verification."""
    if len(sys.argv) < 2:
        print("Usage: python -m governance.audit <command> [args]")
        print("")
        print("Commands:")
        print("  verify <filepath>  - Verify audit chain integrity")
        sys.exit(1)
    
    command = sys.argv[1]
    
    if command == "verify":
        if len(sys.argv) < 3:
            print("Usage: python -m governance.audit verify <filepath>")
            sys.exit(1)
        
        filepath = sys.argv[2]
        print(f"Verifying audit chain: {filepath}")
        
        is_valid, error = HashChainedAuditLogger.verify_chain(filepath)
        
        if is_valid:
            print("✓ Chain verified: OK")
            sys.exit(0)
        else:
            print(f"✗ Chain verification FAILED: {error}")
            sys.exit(1)
    
    else:
        print(f"Unknown command: {command}")
        sys.exit(1)


if __name__ == "__main__":
    main()
