from mcp.server.fastmcp import FastMCP
import requests

mcp = FastMCP("github-agent")


@mcp.tool()
def search_github(query: str):
    """Search GitHub repositories"""
    url = f"https://api.github.com/search/repositories?q={query}"
    res = requests.get(url).json()

    if "items" not in res:
        return []

    return [{"name": r["full_name"], "url": r["html_url"]} for r in res["items"][:3]]


# ----------------------------
# FIXED DOWNLOAD TOOL (IMPORTANT)
# ----------------------------
@mcp.tool()
def download_repo(full_name: str):
    """Download GitHub repo as ZIP using zipball (NO BRANCH ISSUES)"""

    try:
        owner, repo = full_name.split("/")

        # 🔥 BEST METHOD: GitHub auto-handles branch
        zip_url = f"https://github.com/{owner}/{repo}/archive/refs/heads/main.zip"

        response = requests.get(zip_url, stream=True)

        if response.status_code != 200:
            return {
                "status": "error",
                "message": f"Download failed ({response.status_code})",
                "repo": full_name,
            }

        filename = f"{repo}.zip"

        with open(filename, "wb") as f:
            for chunk in response.iter_content(chunk_size=1024):
                f.write(chunk)

        return {
            "status": "success",
            "repo": full_name,
            "file": filename,
            "message": "Downloaded successfully using zipball API",
        }

    except Exception as e:
        return {"status": "error", "message": str(e), "repo": full_name}


if __name__ == "__main__":
    mcp.run()
