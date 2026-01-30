"""
Proxy Enforcer Startup Script

This script starts the governance proxy server.
Run with: python start_proxy.py

Options:
    --host: Host to bind to (default: 0.0.0.0)
    --port: Port to bind to (default: 8000)
"""

import os
import sys
import argparse

# Add src to path FIRST to avoid conflicts with installed packages
sys.path.insert(0, os.path.join(os.path.dirname(__file__), 'src'))

def main():
    parser = argparse.ArgumentParser(description='Start the Governance Proxy Enforcer')
    parser.add_argument('--host', default='0.0.0.0', help='Host to bind to')
    parser.add_argument('--port', type=int, default=8000, help='Port to bind to')
    args = parser.parse_args()
    
    # Import after path is set
    from governance.proxy_enforcer import create_app
    import uvicorn
    
    print(f"Starting Governance Proxy Enforcer...")
    print(f"  Health:  http://{args.host}:{args.port}/health")
    print(f"  Metrics: http://{args.host}:{args.port}/metrics")
    print(f"  Audit:   http://{args.host}:{args.port}/audit")
    print(f"  Tools:   POST http://{args.host}:{args.port}/tool/{{tool_name}}")
    print("-" * 50)
    
    app = create_app()
    uvicorn.run(app, host=args.host, port=args.port)


if __name__ == "__main__":
    main()
