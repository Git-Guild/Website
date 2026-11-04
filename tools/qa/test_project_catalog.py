"""Unit checks for GitHub filtering, pagination, snapshots, and slot overflow."""
import io
import json
import os
import sys
import tempfile
import unittest
from urllib.error import URLError
from urllib.parse import parse_qs, urlparse

ROOT = os.path.dirname(os.path.dirname(os.path.dirname(os.path.abspath(__file__))))
sys.path.insert(0, os.path.join(ROOT, "tools", "sync"))
sys.path.insert(0, os.path.join(ROOT, "tools", "build"))
from sync_github_projects import fetch_repositories, select_public_projects, sync
from project_catalog import build_catalog


def repo(name, **extra):
    value = {
        "name": name,
        "full_name": "Git-Guild/" + name,
        "html_url": "https://github.com/Git-Guild/" + name,
        "description": "Description for " + name,
        "language": "Python",
        "topics": ["open-source"],
        "updated_at": "2026-10-01T12:00:00Z",
        "archived": False,
        "fork": False,
        "private": False,
        "visibility": "public",
    }
    value.update(extra)
    return value


class Response(io.BytesIO):
    def __enter__(self):
        return self

    def __exit__(self, *_args):
        self.close()


class SnapshotTests(unittest.TestCase):
    def test_filters_private_fork_and_archived_repositories(self):
        selected = select_public_projects([
            repo("visible"),
            repo("private", private=True),
            repo("fork", fork=True),
            repo("archived", archived=True),
        ])
        self.assertEqual([item["name"] for item in selected], ["visible"])

    def test_fetches_all_pages_until_a_short_page(self):
        pages = {
            1: [repo("one"), repo("two")],
            2: [repo("three")],
        }
        requested = []

        def opener(request, timeout):
            page = int(parse_qs(urlparse(request.full_url).query)["page"][0])
            requested.append((page, timeout))
            return Response(json.dumps(pages[page]).encode("utf-8"))

        result = fetch_repositories(opener=opener, page_size=2)
        self.assertEqual([item["name"] for item in result], ["one", "two", "three"])
        self.assertEqual([page for page, _ in requested], [1, 2])

    def test_failed_sync_preserves_existing_snapshot(self):
        with tempfile.TemporaryDirectory() as folder:
            path = os.path.join(folder, "snapshot.json")
            with open(path, "w", encoding="utf-8") as handle:
                handle.write("previous snapshot\n")

            def fail(_request, timeout):
                raise URLError("offline")

            with self.assertRaisesRegex(RuntimeError, "previous snapshot was not changed"):
                sync(path, opener=fail)
            with open(path, "r", encoding="utf-8") as handle:
                self.assertEqual(handle.read(), "previous snapshot\n")

    def test_catalog_maps_three_twelve_and_thirteen_projects(self):
        for count in (3, 12, 13):
            with self.subTest(count=count):
                repositories = [repo(f"project-{i:02d}", updated_at=f"2026-10-{i + 1:02d}T00:00:00Z") for i in range(count)]
                curation = {"projectOrder": [item["name"] for item in repositories], "projects": {}}
                catalog = build_catalog({"repositories": repositories}, curation)
                self.assertEqual(len(catalog["order"]), count)
                self.assertEqual(catalog["order"][:12], [f"n{i}" for i in range(min(count, 12))])
                self.assertEqual(catalog["order"][12:], ["r-project-12"] if count == 13 else [])

    def test_unlisted_repositories_append_by_latest_update(self):
        repositories = [repo("curated"), repo("older", updated_at="2026-09-01T00:00:00Z"), repo("newer", updated_at="2026-11-01T00:00:00Z")]
        catalog = build_catalog({"repositories": repositories}, {"projectOrder": ["curated"], "projects": {}})
        self.assertEqual([catalog["projects"][key]["repoName"] for key in catalog["order"]], ["curated", "newer", "older"])


if __name__ == "__main__":
    unittest.main()
