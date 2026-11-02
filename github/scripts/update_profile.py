#!/usr/bin/env python3
"""Refresh the profile README project showcase and recent public activity."""

import html
import os
import re
import requests
from pathlib import Path

USERNAME = os.getenv("GITHUB_USERNAME", "aruncx")
TOKEN = os.getenv("GITHUB_TOKEN")
README = Path("README.md")
API = "https://api.github.com"

HEADERS = {
    "Accept": "application/vnd.github+json",
    "X-GitHub-Api-Version": "2022-11-28",
}
if TOKEN:
    HEADERS["Authorization"] = f"Bearer {TOKEN}"


def github_get(url, params=None):
    response = requests.get(url, headers=HEADERS, params=params, timeout=30)
    response.raise_for_status()
    return response.json()


def safe(value):
    """Escape text for safe display in a README table/list."""
    return html.escape(str(value or "")).replace("|", r"\|").replace("\n", " ")


def update_or_append_section(readme_text, section_name, heading, body):
    """Update a marked section, or append it if the markers do not exist yet."""
    start_marker = f"<!-- {section_name}:START -->"
    end_marker = f"<!-- {section_name}:END -->"

    has_start = start_marker in readme_text
    has_end = end_marker in readme_text

    if has_start and has_end:
        pattern = re.compile(
            re.escape(start_marker) + r".*?" + re.escape(end_marker),
            flags=re.DOTALL,
        )
        replacement = f"{start_marker}\n{body}\n{end_marker}"
        return pattern.sub(lambda _: replacement, readme_text, count=1)

    if has_start != has_end:
        raise RuntimeError(
            f"README.md has only one marker for {section_name}. "
            f"Add both {start_marker} and {end_marker}, or remove the incomplete marker."
        )

    section = f"\n\n## {heading}\n\n{start_marker}\n{body}\n{end_marker}\n"
    return readme_text.rstrip() + section


def build_projects():
    repos = github_get(
        f"{API}/users/{USERNAME}/repos",
        {"per_page": 100, "sort": "updated", "type": "owner"},
    )
    repos = [
        repo for repo in repos
        if not repo.get("fork")
        and not repo.get("archived")
        and not repo.get("private")
    ]
    repos.sort(
        key=lambda repo: (
            repo.get("stargazers_count", 0),
            repo.get("updated_at", ""),
        ),
        reverse=True,
    )

    rows = []
    for repo in repos[:8]:
        name = safe(repo.get("name"))
        url = repo.get("html_url", f"https://github.com/{USERNAME}")
        description = safe(
            repo.get("description") or "Open-source project and development work."
        )
        language = safe(repo.get("language") or "Various")
        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)

        rows.append(
            f'<tr><td width="68%"><b><a href="{url}">{name}</a></b>'
            f'<br/>{description}</td>'
            f'<td align="center">{language}<br/>⭐ {stars} · 🍴 {forks}</td></tr>'
        )

    if not rows:
        return "_No public repositories were returned by the GitHub API._"

    return "<table>\n" + "\n".join(rows) + "\n</table>"


def build_activity():
    events = github_get(
        f"{API}/users/{USERNAME}/events/public",
        {"per_page": 100},
    )

    lines = []
    for event in events:
        event_type = event.get("type", "")
        repo = event.get("repo", {}).get("name", "")
        created = event.get("created_at", "")[:10]
        payload = event.get("payload", {})

        if event_type == "PushEvent":
            count = len(payload.get("commits", []))
            detail = f"Pushed {count} commit(s)"
        elif event_type == "PullRequestEvent":
            action = payload.get("action", "updated")
            detail = f"{action.title()} a pull request"
        elif event_type == "IssuesEvent":
            action = payload.get("action", "updated")
            detail = f"{action.title()} an issue"
        elif event_type == "CreateEvent":
            ref_type = payload.get("ref_type", "a resource")
            detail = f"Created {ref_type}"
        elif event_type == "ReleaseEvent":
            detail = "Published a release"
        elif event_type == "WatchEvent":
            detail = "Starred a repository"
        else:
            continue

        if repo:
            lines.append(
                f"- **{created}** · {detail} in "
                f"[`{safe(repo)}`](https://github.com/{repo})"
            )
        else:
            lines.append(f"- **{created}** · {detail}")

        if len(lines) >= 7:
            break

    if not lines:
        return (
            "_No recent public events are available yet. "
            "Private activity is not exposed by this public endpoint._"
        )

    return "\n".join(lines)


def main():
    if not README.exists():
        raise FileNotFoundError("README.md was not found in the repository root.")

    readme_text = README.read_text(encoding="utf-8")
    projects_md = build_projects()
    activity_md = build_activity()

    readme_text = update_or_append_section(
        readme_text,
        "PROJECTS",
        "🚀 Automatically Updated Projects",
        projects_md,
    )
    readme_text = update_or_append_section(
        readme_text,
        "ACTIVITY",
        "⚡ Recent GitHub Activity",
        activity_md,
    )

    README.write_text(readme_text.rstrip() + "\n", encoding="utf-8")
    print("README project showcase and recent public activity refreshed successfully.")


if __name__ == "__main__":
    main()
