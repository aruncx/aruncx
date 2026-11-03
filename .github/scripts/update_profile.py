#!/usr/bin/env python3
"""Update the profile README with public repositories and recent public activity."""

import html
import os
import re
from pathlib import Path

import requests

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


def github_get(endpoint, params=None):
    response = requests.get(
        endpoint,
        headers=HEADERS,
        params=params,
        timeout=30
    )
    response.raise_for_status()
    return response.json()


def safe(value):
    return html.escape(str(value or "")).replace("|", r"\|").replace("\n", " ")


def replace_section(content, section_name, body):
    start = f"<!-- {section_name}:START -->"
    end = f"<!-- {section_name}:END -->"

    if start not in content or end not in content:
        raise RuntimeError(
            f"Missing README markers for {section_name}. "
            f"Both {start} and {end} must exist."
        )

    pattern = re.compile(
        re.escape(start) + r".*?" + re.escape(end),
        re.DOTALL
    )

    replacement = f"{start}\n{body}\n{end}"
    updated, count = pattern.subn(
        lambda _: replacement,
        content,
        count=1
    )

    if count != 1:
        raise RuntimeError(
            f"Could not update README section: {section_name}"
        )

    return updated


def get_commit_count(payload):
    """
    Get the number of commits from GitHub PushEvent data.

    GitHub may omit the individual commits array.
    Therefore, use the event size fields first.
    """

    size = payload.get("size")

    if isinstance(size, int) and size > 0:
        return size

    distinct_size = payload.get("distinct_size")

    if isinstance(distinct_size, int) and distinct_size > 0:
        return distinct_size

    commits = payload.get("commits", [])

    if commits:
        return len(commits)

    # Avoid displaying misleading zero commit counts.
    return None


def make_project_table():

    repos = github_get(
        f"{API}/users/{USERNAME}/repos",
        {
            "per_page": 100,
            "sort": "updated",
            "type": "owner"
        }
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
            repo.get("updated_at", "")
        ),
        reverse=True
    )

    rows = []

    for repo in repos[:8]:

        name = safe(repo.get("name"))

        url = repo.get(
            "html_url",
            f"https://github.com/{USERNAME}"
        )

        description = safe(
            repo.get("description")
            or "Open-source project and development work."
        )

        language = safe(
            repo.get("language") or "Various"
        )

        stars = repo.get("stargazers_count", 0)
        forks = repo.get("forks_count", 0)

        rows.append(
            f'<tr><td width="68%"><b><a href="{url}">'
            f'{name}</a></b><br/>{description}</td>'
            f'<td align="center">{language}<br/>'
            f'⭐ {stars} · 🍴 {forks}</td></tr>'
        )

    if not rows:
        return "_No public repositories were returned by the GitHub API._"

    return "<table>\n" + "\n".join(rows) + "\n</table>"


def make_activity_list():

    events = github_get(
        f"{API}/users/{USERNAME}/events/public",
        {"per_page": 100}
    )

    lines = []

    for event in events:

        event_type = event.get("type", "")
        repo = event.get("repo", {}).get("name", "")
        date = event.get("created_at", "")[:10]
        payload = event.get("payload", {})

        if event_type == "PushEvent":

            commit_count = get_commit_count(payload)

            if commit_count is not None:
                detail = f"Pushed {commit_count} commit(s)"
            else:
                detail = "Pushed updates"

        elif event_type == "PullRequestEvent":

            detail = (
                f"{payload.get('action', 'updated').title()} "
                "a pull request"
            )

        elif event_type == "IssuesEvent":

            detail = (
                f"{payload.get('action', 'updated').title()} "
                "an issue"
            )

        elif event_type == "CreateEvent":

            detail = (
                f"Created {payload.get('ref_type', 'a resource')}"
            )

        elif event_type == "ReleaseEvent":

            detail = "Published a release"

        elif event_type == "WatchEvent":

            detail = "Starred a repository"

        else:
            continue

        if repo:

            lines.append(
                f"- **{date}** · {detail} in "
                f"[`{safe(repo)}`](https://github.com/{repo})"
            )

        else:

            lines.append(
                f"- **{date}** · {detail}"
            )

        if len(lines) >= 7:
            break

    if not lines:

        return (
            "_No recent public events are available yet. "
            "Private activity is not exposed by this public endpoint._"
        )

    return "\n".join(lines)


def main():

    if not README.is_file():
        raise FileNotFoundError(
            "README.md was not found in the repository root."
        )

    content = README.read_text(encoding="utf-8")

    content = replace_section(
        content,
        "PROJECTS",
        make_project_table()
    )

    content = replace_section(
        content,
        "ACTIVITY",
        make_activity_list()
    )

    README.write_text(
        content.rstrip() + "\n",
        encoding="utf-8"
    )

    print(
        "README project showcase and recent public activity "
        "updated successfully."
    )


if __name__ == "__main__":
    main()
