#!/usr/bin/env python3
"""
MCP Server for Odoo Testing Scripts
Exposes bash scripts as MCP tools that Claude can discover and use automatically
"""

import asyncio
import json
import subprocess
import sys
from pathlib import Path
from typing import Any

# This is a simple MCP server implementation
# It exposes our bash scripts as tools that Claude can call

SCRIPTS_DIR = Path(__file__).parent.parent / "bash"

AVAILABLE_TOOLS = [
    {
        "name": "odoo_restart",
        "description": "Restart Odoo service on testing or production server",
        "inputSchema": {
            "type": "object",
            "properties": {
                "server": {
                    "type": "string",
                    "enum": ["testing", "production"],
                    "description": "Which server to restart (testing or production)",
                    "default": "production"
                }
            },
            "required": []
        },
        "script": "odoo-restart.sh"
    },
    {
        "name": "odoo_logs",
        "description": "View Odoo logs from testing or production server",
        "inputSchema": {
            "type": "object",
            "properties": {
                "server": {
                    "type": "string",
                    "enum": ["testing", "production"],
                    "description": "Which server logs to view",
                    "default": "production"
                },
                "mode": {
                    "type": "string",
                    "enum": ["lines", "follow"],
                    "description": "View last N lines or follow in real-time",
                    "default": "lines"
                },
                "lines": {
                    "type": "integer",
                    "description": "Number of lines to show (only for 'lines' mode)",
                    "default": 100
                }
            },
            "required": []
        },
        "script": "odoo-logs.sh"
    },
    {
        "name": "odoo_health_check",
        "description": "Complete health check of Odoo server including services, resources, and database status",
        "inputSchema": {
            "type": "object",
            "properties": {
                "server": {
                    "type": "string",
                    "enum": ["testing", "production"],
                    "description": "Which server to check",
                    "default": "production"
                }
            },
            "required": []
        },
        "script": "odoo-health-check.sh"
    }
]


async def handle_list_tools():
    """Return list of available tools"""
    return {
        "jsonrpc": "2.0",
        "result": {
            "tools": AVAILABLE_TOOLS
        }
    }


async def handle_call_tool(tool_name: str, arguments: dict[str, Any]):
    """Execute a tool by running the corresponding bash script"""

    # Find the tool
    tool = next((t for t in AVAILABLE_TOOLS if t["name"] == tool_name), None)
    if not tool:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32602,
                "message": f"Tool '{tool_name}' not found"
            }
        }

    # Build command arguments
    script_path = SCRIPTS_DIR / tool["script"]
    cmd = [str(script_path)]

    if tool_name == "odoo_restart":
        cmd.append(arguments.get("server", "production"))
    elif tool_name == "odoo_logs":
        cmd.append(arguments.get("server", "production"))
        cmd.append(arguments.get("mode", "lines"))
        if arguments.get("mode", "lines") == "lines":
            cmd.append(str(arguments.get("lines", 100)))
    elif tool_name == "odoo_health_check":
        cmd.append(arguments.get("server", "production"))

    # Execute the script
    try:
        result = subprocess.run(
            cmd,
            capture_output=True,
            text=True,
            timeout=30
        )

        output = result.stdout if result.returncode == 0 else result.stderr

        return {
            "jsonrpc": "2.0",
            "result": {
                "content": [
                    {
                        "type": "text",
                        "text": output
                    }
                ]
            }
        }
    except subprocess.TimeoutExpired:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": "Script execution timed out"
            }
        }
    except Exception as e:
        return {
            "jsonrpc": "2.0",
            "error": {
                "code": -32603,
                "message": f"Error executing script: {str(e)}"
            }
        }


async def main():
    """Main MCP server loop"""

    # Read requests from stdin and write responses to stdout
    while True:
        try:
            line = await asyncio.get_event_loop().run_in_executor(None, sys.stdin.readline)
            if not line:
                break

            request = json.loads(line)
            method = request.get("method")

            if method == "tools/list":
                response = await handle_list_tools()
            elif method == "tools/call":
                params = request.get("params", {})
                tool_name = params.get("name")
                arguments = params.get("arguments", {})
                response = await handle_call_tool(tool_name, arguments)
            else:
                response = {
                    "jsonrpc": "2.0",
                    "error": {
                        "code": -32601,
                        "message": f"Method '{method}' not found"
                    }
                }

            # Add request ID if present
            if "id" in request:
                response["id"] = request["id"]

            print(json.dumps(response), flush=True)

        except json.JSONDecodeError:
            continue
        except Exception as e:
            print(json.dumps({
                "jsonrpc": "2.0",
                "error": {
                    "code": -32603,
                    "message": str(e)
                }
            }), flush=True)


if __name__ == "__main__":
    asyncio.run(main())
