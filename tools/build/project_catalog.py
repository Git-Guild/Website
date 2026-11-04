"""Normalize a checked-in GitHub snapshot into the website's project model."""
import re


def slugify(value):
    slug = re.sub(r"[^a-z0-9]+", "-", str(value).lower()).strip("-")
    return slug or "project"


def build_catalog(snapshot, curation, slot_count=12, recent_limit=6):
    repos = snapshot.get("repositories")
    if not isinstance(repos, list):
        raise ValueError("GitHub snapshot must contain a repositories list")

    by_name = {}
    for repo in repos:
        name = repo.get("name")
        if not name or name in by_name:
            raise ValueError(f"Invalid or duplicate repository name: {name!r}")
        if repo.get("private") or repo.get("fork") or repo.get("archived"):
            raise ValueError(f"Snapshot contains an excluded repository: {name}")
        url = repo.get("html_url", "")
        if not url.startswith("https://github.com/Git-Guild/") or url.count("/") != 4:
            raise ValueError(f"Repository has an unexpected GitHub URL: {name}")
        if not repo.get("updated_at"):
            raise ValueError(f"Repository is missing its GitHub update time: {name}")
        by_name[name] = repo

    configured = curation.get("projectOrder", [])
    if len(configured) != len(set(configured)):
        raise ValueError("projectOrder contains duplicate repository names")

    ordered_names = [name for name in configured if name in by_name]
    remainder = [name for name in by_name if name not in set(ordered_names)]
    remainder.sort(key=lambda name: (by_name[name].get("updated_at") or "", name), reverse=True)
    ordered_names.extend(remainder)

    overrides = curation.get("projects", {})
    projects = {}
    order = []
    used_slugs = set()
    for index, repo_name in enumerate(ordered_names):
        repo = by_name[repo_name]
        override = overrides.get(repo_name, {})
        if index < slot_count:
            project_id = f"n{index}"
        else:
            base = "r-" + slugify(repo_name)
            project_id = base
            suffix = 2
            while project_id in used_slugs:
                project_id = f"{base}-{suffix}"
                suffix += 1
        used_slugs.add(project_id)

        topics = [topic for topic in repo.get("topics", []) if isinstance(topic, str) and topic]
        stack = []
        language = repo.get("language")
        for value in ([language] if language else []) + topics:
            if value not in stack:
                stack.append(value)

        project = {
            "id": project_id,
            "repoName": repo_name,
            "name": override.get("name") or repo_name,
            "tagline": override.get("tagline") or repo.get("description") or "GitHub repository",
            "blurb": override.get("blurb") or repo.get("description") or "No description has been added for this repository yet.",
            "language": language,
            "topics": topics,
            "stack": stack,
            "url": repo["html_url"],
            "repo": repo["html_url"],
            "updatedAt": repo.get("updated_at"),
            "featured": bool(override.get("featured", False)),
            "pathLabel": override.get("pathLabel"),
        }
        projects[project_id] = project
        order.append(project_id)

    updates = sorted(
        order,
        key=lambda project_id: (projects[project_id].get("updatedAt") or "", project_id),
    )[-recent_limit:]
    return {
        "collective": curation.get("collective", {}),
        "projects": projects,
        "order": order,
        "mergeTrain": updates,
        "snapshotFetchedAt": snapshot.get("fetched_at"),
    }
