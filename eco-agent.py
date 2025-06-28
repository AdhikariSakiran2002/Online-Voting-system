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
    url = f"https://api.github.com/repos/actions/runner-images/actions/runs?per_page=1"
    res = requests.get(url, headers=headers)
    res.raise_for_status()
    runs = res.json().get(["workflow_runs",[]])

    if not runs:
        print("No workflow")
    return None

    run = runs[0]
    duration_ms = run.get("run_duration_ms", 600000)
    duration_min = duration_ms / 60000
    return {
        "duration": round(duration_min, 2),
        "workflow": run["name"],
        "commit": run["head_sha"],
        "url": run["html_url"]
    }

# -----------------------------
# 💨 Estimate CO₂ in grams
# -----------------------------
def estimate_co2(duration_min):
    kwh_per_min = 0.034 / 60
    co2_grams = duration_min * kwh_per_min * 0.4 * 1000
    return round(co2_grams, 2)

# -----------------------------
# 🧠 GPT: Think + Plan + Decide
# -----------------------------
def think_like_agent(run_info, co2):
    prompt = f"""
You are Eco-Agent, a smart assistant to reduce CI/CD carbon emissions.

Input:
- Job: {run_info['workflow']}
- Duration: {run_info['duration']} min
- Estimated CO₂: {co2} grams

Objective:
- Decide if emissions are too high.
- Suggest optimizations.
- Decide whether to create a GitHub issue.

Respond in JSON like:
{{
  "status": "high" or "low",
  "reasoning": "...",
  "recommendations": ["..."],
  "should_create_issue": true/false,
  "issue_title": "...",
  "issue_body": "..."
}}
"""
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[{"role": "user", "content": prompt}],
        temperature=0.2,
    )
    return eval(response.choices[0].message.content.strip())

# -----------------------------
# 📝 Create GitHub issue
# -----------------------------
def create_issue(title, body):
    print("📬 Creating GitHub issue...")
    url = f"https://api.github.com/repos/actions/runner-images/issues"
    res = requests.post(url, headers=headers, json={"title": title, "body": body})
    if res.status_code == 201:
        print("✅ Issue created:", res.json()["html_url"])
    else:
        print("❌ Issue creation failed:", res.status_code, res.text)

# -----------------------------
# 🔁 Main agent loop
# -----------------------------
def agent_loop():
    for attempt in range(3):
        print(f"\n🔄 Agent Loop Round {attempt + 1}")
        run_info = get_latest_run()
        co2 = estimate_co2(run_info["duration"])
        plan = think_like_agent(run_info, co2)

        print(f"\n📊 Status: {plan['status']}")
        print(f"🧠 Reasoning: {plan['reasoning']}")
        print("💡 Recommendations:")
        for rec in plan['recommendations']:
            print(f"  - {rec}")

        if plan["status"] == "unknown":
            print("🤔 Need more data, retrying...")
            time.sleep(2)
            continue

        if plan["should_create_issue"]:
            create_issue(plan["issue_title"], plan["issue_body"])
        else:
            print("✅ Emissions are okay. No action needed.")
        break

# -----------------------------
# 🚀 Run the agent
# -----------------------------
if __name__ == "__main__":
    print("🚀 Launching Eco-Agent...\n")
    agent_loop()