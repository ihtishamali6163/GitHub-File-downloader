"""
Entry point: takes user input in a loop and runs the app.

- Plain messages ("hi", "how are you") get a normal chat reply.
- "/download <topic>" runs the existing search -> download pipeline via MCP.
"""

import asyncio

from llm import chat_reply, choose_tool
from mcp_client import open_session, list_tools, run_download_pipeline

DOWNLOAD_PREFIX = "/download"


async def main():
    async with open_session() as session:
        tools = await list_tools(session)

        print("\nGitHub MCP Agent Ready")
        print(f"Ask me anything, or type '{DOWNLOAD_PREFIX} <topic>' to fetch a repo from GitHub.")

        while True:
            user_input = input("\nAsk: ")

            if user_input.lower() in ["exit", "quit"]:
                break

            # ----------------------------
            # ROUTE: plain chat vs download command
            # Only messages starting with "/download" go into the tool
            # pipeline - everything else is answered as a normal chat reply
            # and never touches the GitHub tools.
            # ----------------------------
            if not user_input.strip().lower().startswith(DOWNLOAD_PREFIX):
                reply = chat_reply(user_input)
                print("\nBot:", reply)
                continue

            # strip the "/download" prefix, keep the rest as the actual request
            user_input = user_input.strip()[len(DOWNLOAD_PREFIX):].strip()

            if not user_input:
                print(f"\nPlease tell me what to download, e.g. '{DOWNLOAD_PREFIX} mcp'")
                continue

            decision = choose_tool(user_input, tools)
            print("LLM Decision:", decision)

            try:
                tool_name, arg = decision.split("|")
                tool_name = tool_name.strip()
                arg = arg.strip().replace("query:", "")
            except Exception:
                print("❌ Invalid LLM output:", decision)
                continue

            logs = await run_download_pipeline(session, tool_name, arg)
            for label, text in logs:
                print(f"\n{label}:", text)


if __name__ == "__main__":
    asyncio.run(main())
