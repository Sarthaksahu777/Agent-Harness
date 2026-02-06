"""
Proxy Enforcement Layer for Governance Kernel.

This module provides network-level enforcement by intercepting all tool calls
through an HTTP proxy. The proxy enforces governance decisions OUTSIDE the 
agent process, making it non-bypassable.

Fail-Closed Semantics:
- If governance kernel is unreachable -> BLOCK (403)
- If governance decision is HALT -> BLOCK (403)
- If any error occurs during enforcement -> BLOCK (403)
- Only explicit ALLOW from governance -> execute tool

Usage:
    # Start the proxy server
    uvicorn governance.proxy_enforcer:app --host 0.0.0.0 --port 8000
    
    # Or programmatically
    from governance.proxy_enforcer import create_app
    app = create_app(kernel=my_kernel)
"""

import os
import sys
import json
import traceback
from typing import Any, Callable, Dict, Optional
from dataclasses import dataclass, asdict
from datetime import datetime, timezone

# Add src to path for imports
sys.path.insert(0, os.path.dirname(os.path.dirname(os.path.abspath(__file__))))

from fastapi import FastAPI, Request, HTTPException, Response
from fastapi.responses import JSONResponse
from starlette.middleware.base import BaseHTTPMiddleware

from governance.kernel import GovernanceKernel
from governance.profiles import BALANCED
from governance.audit import AuditLogger
from governance.result import EngineResult


# =============================================================================
# Configuration
# =============================================================================

PROXY_HOST = os.environ.get("GOVERNANCE_PROXY_HOST", "0.0.0.0")
PROXY_PORT = int(os.environ.get("GOVERNANCE_PROXY_PORT", "8000"))


# =============================================================================
# Mock Tool Backend (for testing)
# =============================================================================

class MockToolBackend:
    """
    Mock tool backend that simulates tool execution.
    In production, this would forward to actual tool implementations.
    """
    
    def __init__(self):
        self._tools: Dict[str, Callable] = {
            "echo": lambda params: {"result": params.get("message", "")},
            "add": lambda params: {"result": params.get("a", 0) + params.get("b", 0)},
            "test_action": lambda params: {"result": "executed", "params": params},
        }
    
    def register(self, name: str, handler: Callable) -> None:
        """Register a tool handler."""
        self._tools[name] = handler
    
    def execute(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool by name."""
        if tool_name not in self._tools:
            raise ValueError(f"Unknown tool: {tool_name}")
        return self._tools[tool_name](params)
    
    def has_tool(self, tool_name: str) -> bool:
        """Check if a tool exists."""
        return tool_name in self._tools


# =============================================================================
# Fail-Closed Middleware
# =============================================================================

class FailClosedMiddleware(BaseHTTPMiddleware):
    """
    Middleware that ensures fail-closed behavior.
    
    Any unhandled exception in the request processing will result in
    a 403 Forbidden response, never a silent pass-through.
    """
    
    async def dispatch(self, request: Request, call_next):
        try:
            response = await call_next(request)
            return response
        except Exception as e:
            # Log the error for debugging
            traceback.print_exc()
            # FAIL-CLOSED: Always return 403 on any error
            return JSONResponse(
                status_code=403,
                content={
                    "blocked": True,
                    "halt_reason": "ENFORCEMENT_ERROR",
                    "error": str(e),
                    "message": "Action blocked due to enforcement error (fail-closed)"
                }
            )


# =============================================================================
# Proxy Enforcer Application
# =============================================================================

@dataclass
class ToolCallRequest:
    """Incoming tool call request."""
    tool_name: str
    params: Dict[str, Any]
    # Optional signal overrides for testing
    reward: float = 0.0
    novelty: float = 0.0
    urgency: float = 0.0
    difficulty: float = 0.0
    trust: float = 1.0


@dataclass
class EnforcementDecision:
    """Result of governance enforcement check."""
    allowed: bool
    halt_reason: Optional[str] = None
    budget_snapshot: Optional[Dict[str, float]] = None
    step: int = 0


class ProxyEnforcer:
    """
    HTTP Proxy Enforcer that intercepts tool calls and enforces governance.
    
    Architecture:
        Agent -> ProxyEnforcer -> GovernanceKernel -> Decision
                      |                                  |
                      +-- If ALLOW ----------------------+-> ToolBackend -> Result
                      +-- If HALT -------------------------> 403 Forbidden
    """
    
    def __init__(
        self,
        kernel: Optional[GovernanceKernel] = None,
        backend: Optional[MockToolBackend] = None,
        audit_logger: Optional[AuditLogger] = None,
    ):
        self.kernel = kernel or GovernanceKernel(BALANCED)
        self.backend = backend or MockToolBackend()
        self.audit = audit_logger or AuditLogger()
        self._step_count = 0
    
    def enforce(self, request: ToolCallRequest) -> EnforcementDecision:
        """
        Enforce governance decision for a tool call.
        
        Returns:
            EnforcementDecision with allowed=True/False
        """
        try:
            self._step_count += 1
            
            # Get governance decision
            result: EngineResult = self.kernel.step(
                reward=request.reward,
                novelty=request.novelty,
                urgency=request.urgency,
                difficulty=request.difficulty,
                trust=request.trust,
            )
            
            # Log to audit BEFORE returning decision
            signals = {
                "reward": request.reward,
                "novelty": request.novelty,
                "urgency": request.urgency,
                "difficulty": request.difficulty,
                "trust": request.trust,
            }
            self.audit.log(
                step=self._step_count,
                action=request.tool_name,
                params=request.params,
                signals=signals,
                result=result,
            )
            
            # Build decision
            budget_snapshot = {
                "effort": result.budget.effort,
                "risk": result.budget.risk,
                "exploration": result.budget.exploration,
                "persistence": result.budget.persistence,
            }
            
            return EnforcementDecision(
                allowed=not result.halted,
                halt_reason=result.reason if result.halted else None,
                budget_snapshot=budget_snapshot,
                step=self._step_count,
            )
            
        except Exception as e:
            # FAIL-CLOSED: Any error during enforcement -> BLOCK
            return EnforcementDecision(
                allowed=False,
                halt_reason=f"ENFORCEMENT_ERROR: {str(e)}",
                step=self._step_count,
            )
    
    def execute_tool(self, tool_name: str, params: Dict[str, Any]) -> Dict[str, Any]:
        """Execute a tool via the backend."""
        return self.backend.execute(tool_name, params)


def create_app(
    kernel: Optional[GovernanceKernel] = None,
    backend: Optional[MockToolBackend] = None,
    audit_logger: Optional[AuditLogger] = None,
) -> FastAPI:
    """
    Create a FastAPI application with governance enforcement.
    
    Args:
        kernel: GovernanceKernel instance (uses BALANCED profile if None)
        backend: Tool backend (uses MockToolBackend if None)
        audit_logger: Audit logger for recording decisions
    
    Returns:
        Configured FastAPI application
    """
    app = FastAPI(
        title="Governance Proxy Enforcer",
        description="Network-level governance enforcement for agent tool calls",
        version="1.1.0",
    )
    
    # Add fail-closed middleware
    app.add_middleware(FailClosedMiddleware)
    
    # Create enforcer instance
    enforcer = ProxyEnforcer(
        kernel=kernel,
        backend=backend,
        audit_logger=audit_logger,
    )
    
    # Store enforcer in app state for access in routes
    app.state.enforcer = enforcer
    
    @app.post("/tool/{tool_name}")
    async def call_tool(tool_name: str, request: Request):
        """
        Execute a tool call with governance enforcement.
        
        Path Parameters:
            tool_name: Name of the tool to execute
        
        Request Body:
            {
                "params": {...},           # Tool parameters
                "signals": {               # Optional signal overrides
                    "reward": 0.0,
                    "novelty": 0.0,
                    "urgency": 0.0,
                    "difficulty": 0.0,
                    "trust": 1.0
                }
            }
        
        Returns:
            200: Tool executed successfully
            403: Blocked by governance (halted or error)
            404: Tool not found
        """
        try:
            body = await request.json()
        except Exception:
            body = {}
        
        params = body.get("params", {})
        signals = body.get("signals", {})
        
        # Build tool call request
        tool_request = ToolCallRequest(
            tool_name=tool_name,
            params=params,
            reward=signals.get("reward", 0.0),
            novelty=signals.get("novelty", 0.0),
            urgency=signals.get("urgency", 0.0),
            difficulty=signals.get("difficulty", 0.0),
            trust=signals.get("trust", 1.0),
        )
        
        # Enforce governance decision
        decision = enforcer.enforce(tool_request)
        
        if not decision.allowed:
            # BLOCKED: Return 403 with halt reason
            return JSONResponse(
                status_code=403,
                content={
                    "blocked": True,
                    "halt_reason": decision.halt_reason,
                    "step": decision.step,
                    "budget": decision.budget_snapshot,
                }
            )
        
        # ALLOWED: Execute the tool
        if not enforcer.backend.has_tool(tool_name):
            return JSONResponse(
                status_code=404,
                content={"error": f"Tool not found: {tool_name}"}
            )
        
        try:
            result = enforcer.execute_tool(tool_name, params)
            return JSONResponse(
                status_code=200,
                content={
                    "allowed": True,
                    "step": decision.step,
                    "budget": decision.budget_snapshot,
                    "result": result,
                }
            )
        except Exception as e:
            # FAIL-CLOSED: Error during execution -> 403
            return JSONResponse(
                status_code=403,
                content={
                    "blocked": True,
                    "halt_reason": f"EXECUTION_ERROR: {str(e)}",
                    "step": decision.step,
                }
            )
    
    @app.get("/health")
    async def health_check():
        """Health check endpoint."""
        return {"status": "healthy", "version": "1.1.0"}
    
    @app.get("/audit")
    async def get_audit():
        """Get current audit log."""
        return enforcer.audit.dump()
    
    @app.get("/metrics")
    async def get_metrics():
        """
        Prometheus metrics endpoint.
        
        Returns metrics in Prometheus text format for scraping.
        """
        from governance.metrics import PrometheusRegistry
        
        # Get the registry from app state or create one
        if not hasattr(app.state, 'registry'):
            app.state.registry = PrometheusRegistry()
        
        return Response(
            content=app.state.registry.to_prometheus_text(),
            media_type="text/plain; charset=utf-8"
        )
    
    return app


# Default application instance
app = create_app()


# =============================================================================
# CLI Entry Point
# =============================================================================

if __name__ == "__main__":
    import uvicorn
    
    print(f"Starting Governance Proxy Enforcer on {PROXY_HOST}:{PROXY_PORT}")
    print("Endpoints:")
    print(f"  POST /tool/<tool_name>  - Execute tool with governance")
    print(f"  GET  /health            - Health check")
    print(f"  GET  /audit             - View audit log")
    
    uvicorn.run(app, host=PROXY_HOST, port=PROXY_PORT)
