import os
import time
import openai
import requests
from dotenv import load_dotenv

# -----------------------------
# 🌱 Load API keys and repo info
# -----------------------------
load_dotenv()

GITHUB_TOKEN = "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"
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
REPO = os.getenv("REPO")
openai.api_key = OPENAI_API_KEY

headers = {"Authorization": f"token {GITHUB_TOKEN}"}

# -----------------------------
# 🔍 Get latest GitHub Actions run
# -----------------------------
def get_latest_run():
    print("📦 Fetching latest workflow run...")
    url = f"https://api.github.com/repos/Srujana482029/Eco/actions/runs?per_page=1"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    run = res.json()["workflow_runs"][0]
    duration_ms = run.get("run_duration_ms", 600000)
    duration_min = duration_ms / 60000
    return {
        "duration": round(duration_min, 2),
        "workflow": run["name"],
        "commit": run["head_sha"],
        "url": run["html_url"]
    }