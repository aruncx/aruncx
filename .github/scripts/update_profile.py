#!/usr/bin/env python3
"""Refresh the profile README project showcase and recent public activity."""
import os
import re
import html
import requests
from pathlib import Path

USERNAME = os.getenv("GITHUB_USERNAME", "aruncx")
TOKEN = os.getenv("GITHUB_TOKEN")
README = Path("README.md")
API = "https://api.github.com"
headers = {"Accept": "application/vnd.github+json", "X-GitHub-Api-Version": "2022-11-28"}
if TOKEN:
    headers["Authorization"] = f"Bearer {TOKEN}"

def get(url, params=None):
    response = requests.get(url, headers=headers, params=params, timeout=30)
    response.raise_for_status()
    return response.json()

def safe(value):
    return html.escape(str(value or "")).replace("|", r"\|").replace("\n", " ")

def update_section(text, name, body):
    pattern = rf"(<!-- {name}:START -->).*?(<!-- {name}:END -->)"
    replacement = rf"\1\n{body}\n\2"
    updated, count = re.subn(pattern, lambda m: f"{m.group(1)}\n{body}\n<!-- {name}:END -->", text, flags=re.S)
    if not count:
        raise RuntimeError(f"Could not find {name} markers in README.md")
    return updated

repos = get(f"{API}/users/{USERNAME}/repos", {"per_page": 100, "sort": "updated", "type": "owner"})
repos = [r for r in repos if not r.get("fork") and not r.get("archived") and not r.get("private")]
repos.sort(key=lambda r: (r.get("stargazers_count", 0), r.get("updated_at", "")), reverse=True)
cards = []
for repo in repos[:8]:
    name = safe(repo["name"])
    url = repo["html_url"]
    description = safe(repo.get("description") or "Open-source project and development work.")
    language = safe(repo.get("language") or "Various")
    stars = repo.get("stargazers_count", 0)
    forks = repo.get("forks_count", 0)
    cards.append(
        f'<tr><td width="68%"><b><a href="{url}">{name}</a></b><br/>{description}</td>'
        f'<td align="center">{language}<br/>⭐ {stars} · 🍴 {forks}</td></tr>'
    )
project_md = (
    '<table>\n' + "\n".join(cards) + '\n</table>'
    if cards else "_No public repositories were returned by the GitHub API._"
)

events = get(f"{API}/users/{USERNAME}/events/public", {"per_page": 100})
activity_lines = []
for event in events:
    typ = event.get("type", "")
    repo = event.get("repo", {}).get("name", "")
    created = event.get("created_at", "")[:10]
    payload = event.get("payload", {})
    if typ == "PushEvent":
        count = len(payload.get("commits", []))
        detail = f"Pushed {count} commit(s)"
    elif typ == "PullRequestEvent":
        action = payload.get("action", "updated")
        detail = f"{action.title()} a pull request"
    elif typ == "IssuesEvent":
        detail = f"{payload.get('action', 'updated').title()} an issue"
    elif typ == "CreateEvent":
        detail = f"Created {payload.get('ref_type', 'a resource')}"
    elif typ == "ReleaseEvent":
        detail = f"Published a release ({payload.get('action', 'published')})"
    elif typ == "WatchEvent":
        detail = "Starred a repository"
    else:
        continue
    activity_lines.append(f"- **{created}** · {detail} in [`{safe(repo)}`](https://github.com/{repo})")
    if len(activity_lines) == 7:
        break

activity_md = "\n".join(activity_lines) if activity_lines else "_No recent public events are available yet. Private activity is not exposed by this public endpoint._"

text = README.read_text(encoding="utf-8")
text = update_section(text, "PROJECTS", project_md)
text = update_section(text, "ACTIVITY", activity_md)
README.write_text(text, encoding="utf-8")
print("README project showcase and recent activity refreshed.")
