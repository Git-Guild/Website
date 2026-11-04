#!/usr/bin/env python3
"""Refresh the public Git Guild repository snapshot used by the static build."""
import argparse
import json
import os
import tempfile
from datetime import datetime, timezone
from urllib.error import HTTPError, URLError
from urllib.parse import urlencode
from urllib.request import Request, urlopen


ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
DEFAULT_OUTPUT = os.path.join(ROOT, "data", "github-projects.json")
API_ROOT = "https://api.github.com"
ORG = "Git-Guild"
PAGE_SIZE = 100
FIELDS = (
    "name", "full_name", "html_url", "description", "language", "topics",
    "updated_at", "archived", "fork", "private", "visibility",
)


def fetch_page(org, page, opener=urlopen, page_size=PAGE_SIZE):
    query = urlencode({"type": "public", "sort": "updated", "direction": "desc", "per_page": page_size, "page": page})
    request = Request(
        f"{API_ROOT}/orgs/{org}/repos?{query}",
        headers={
            "Accept": "application/vnd.github+json",
            "X-GitHub-Api-Version": "2022-11-28",
            "User-Agent": "GitGuildWebsiteSnapshot/1.0",
        },
    )
    with opener(request, timeout=25) as response:
        payload = json.load(response)
    if not isinstance(payload, list):
        raise ValueError(f"GitHub returned an invalid repository page: {page}")
    return payload


def fetch_repositories(org=ORG, opener=urlopen, page_size=PAGE_SIZE):
    all_repos = []
    page = 1
    while True:
        batch = fetch_page(org, page, opener=opener, page_size=page_size)
        all_repos.extend(batch)
        if len(batch) < page_size:
            break
        page += 1
    return all_repos


def select_public_projects(repositories):
    selected = []
    for repo in repositories:
        if repo.get("private") or repo.get("visibility") not in (None, "public"):
            continue
        if repo.get("fork") or repo.get("archived"):
            continue
        if not repo.get("name") or not repo.get("html_url"):
            raise ValueError("GitHub returned a repository without its name or URL")
        selected.append({field: repo.get(field) for field in FIELDS if field in repo})
    return selected


def write_snapshot(output_path, repos, org=ORG):
    if not repos:
        raise ValueError("No eligible public repositories returned; keeping the previous snapshot")
    payload = {
        "schema_version": 1,
        "organization": org,
        "fetched_at": datetime.now(timezone.utc).replace(microsecond=0).isoformat().replace("+00:00", "Z"),
        "repositories": repos,
    }
    directory = os.path.dirname(output_path)
    os.makedirs(directory, exist_ok=True)
    fd, temp_path = tempfile.mkstemp(prefix=".github-projects-", suffix=".tmp", dir=directory)
    try:
        with os.fdopen(fd, "w", encoding="utf-8", newline="\n") as handle:
            json.dump(payload, handle, ensure_ascii=False, indent=2)
            handle.write("\n")
        os.replace(temp_path, output_path)
    except Exception:
        try:
            os.unlink(temp_path)
        except FileNotFoundError:
            pass
        raise
    return payload


def sync(output_path=DEFAULT_OUTPUT, org=ORG, opener=urlopen, page_size=PAGE_SIZE):
    try:
        repos = select_public_projects(fetch_repositories(org, opener, page_size))
        return write_snapshot(output_path, repos, org)
    except (HTTPError, URLError, TimeoutError, OSError, ValueError) as error:
        raise RuntimeError(f"GitHub project sync failed: {error}. The previous snapshot was not changed.") from error


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--org", default=ORG, help="GitHub organization (default: Git-Guild)")
    parser.add_argument("--output", default=DEFAULT_OUTPUT, help="snapshot path")
    args = parser.parse_args()
    payload = sync(args.output, args.org)
    print(f"Saved {len(payload['repositories'])} public repositories to {args.output}")


if __name__ == "__main__":
    try:
        main()
    except RuntimeError as error:
        raise SystemExit(str(error))
