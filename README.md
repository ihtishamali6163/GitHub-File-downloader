# GitHub Downloading Agent

A small AI agent that chats normally like any chatbot, and downloads GitHub
repositories on demand when you ask it to. It's built on the **Model Context
Protocol (MCP)**: a lightweight server exposes `search_github` and
`download_repo` as callable tools, and a client talks to that server plus a
Groq-hosted LLM to decide what to do with your input.

## How it works

- Type anything normal (`hi`, `how are you`, `what can you do`) and you get a
  plain chatbot reply. No search, no download, no GitHub API calls.
- Type `/download <topic>` (e.g. `/download mcp`) and the agent:
  1. Asks the LLM which MCP tool to use for your request.
  2. Searches GitHub for matching repositories (`search_github`).
  3. Automatically downloads the top match as a `.zip` (`download_repo`).

## Project structure

```
.
├── main.py          # Entry point - takes input, routes chat vs /download
├── llm.py           # Groq client, system prompts, chat & tool-selection logic
├── mcp_client.py     # MCP session setup + search/download tool pipeline
├── server.py         # MCP server exposing search_github and download_repo
├── requirements.txt
├── .env.example
└── .gitignore
```

## Setup

**1. Clone and enter the project**

```bash
git clone <your-repo-url>
cd Github_Downloading_agent
```

**2. Create a virtual environment**

```bash
python -m venv venv
venv\Scripts\activate      # Windows
source venv/bin/activate   # macOS/Linux
```

**3. Install dependencies**

```bash
pip install -r requirements.txt
```

**4. Add your Groq API key**

Copy `.env.example` to `.env` and fill in your key:

```
GROQ_API_KEY="your-groq-api-key-here"
```

Get a free key at [console.groq.com](https://console.groq.com).

## Usage

```bash
python main.py
```

```
GitHub MCP Agent Ready
Ask me anything, or type '/download <topic>' to fetch a repo from GitHub.

Ask: hi, how are you?
Bot: I'm doing well, thanks for asking! How can I help you today?

Ask: /download mcp
LLM Decision: search_github | mcp

Auto downloading: modelcontextprotocol/servers

Download Result: Downloaded successfully using zipball API
```

Downloaded repositories are saved as `<repo-name>.zip` in the project's root
directory.

Type `exit` or `quit` to stop the agent.

## Tools exposed by the MCP server

| Tool | Description |
|---|---|
| `search_github(query)` | Searches GitHub repositories and returns the top 3 matches. |
| `download_repo(full_name)` | Downloads a repo's `main` branch as a zip via GitHub's zipball URL. |

## Notes

- Downloads currently assume the repository's default branch is `main`.
- The LLM is only used for (a) casual chat replies and (b) deciding which
  tool to call for a `/download` request - it never invents repository names.
- **Never commit your `.env` file.** It's already excluded via `.gitignore`;
  use `.env.example` as the template for others setting up the project.

## License

Add a license of your choice (e.g. MIT) before publishing.
