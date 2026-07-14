"""
Everything related to talking to the MCP GitHub server (server.py) lives here:
opening the client session, listing available tools, and running the
search -> download tool pipeline. The actual search/download behaviour is
defined in server.py and is untouched - this file only calls those tools.
"""

import json
from contextlib import asynccontextmanager

from mcp import ClientSession
from mcp.client.stdio import stdio_client, StdioServerParameters


@asynccontextmanager
async def open_session():
    """Start server.py as a subprocess and open an MCP client session to it."""
    server_params = StdioServerParameters(command="python", args=["server.py"])

    async with stdio_client(server_params) as (read, write):
        async with ClientSession(read, write) as session:
            await session.initialize()
            yield session


async def list_tools(session):
    return await session.list_tools()


async def run_download_pipeline(session, tool_name: str, arg: str):
    """Call the chosen tool, then auto-chain search -> download exactly like
    before. Returns a list of (label, text) pairs for the caller to print.
    """
    logs = []

    if tool_name == "download_repo":
        args = {"full_name": arg}
    else:
        args = {"query": arg}

    result = await session.call_tool(tool_name, args)

    if result.content:
        content = result.content[0]
        if hasattr(content, "text"):
            logs.append(("Result", content.text))
        else:
            logs.append(("Result", str(content)))

    # AUTO DOWNLOAD LOGIC (unchanged)
    if tool_name == "search_github":
        try:
            content_text = result.content[0].text
            data = json.loads(content_text)

            first_repo = None

            # Properly extract the repo path from either a list or dict payload
            if isinstance(data, list) and len(data) > 0:
                first_repo = data[0].get("full_name") or data[0].get("name")
            elif isinstance(data, dict):
                first_repo = data.get("full_name") or data.get("name")

            if first_repo:
                logs.append(("Auto downloading", first_repo))
                download_result = await session.call_tool("download_repo", {"full_name": first_repo})

                if download_result and download_result.content:
                    logs.append(("Download Result", download_result.content[0].text))
            else:
                logs.append(("Info", "No repositories found to auto-download."))

        except Exception as e:
            logs.append(("Auto-download failed", repr(e)))

    return logs
