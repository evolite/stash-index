"""Rebuild index.yml from each plugin's latest GitHub release (see plugins.yml).

Independent of Codeberg: names/descriptions come from the existing index.yml, and
version/date/path/sha256 come from the GitHub release. Entries without a GitHub
release (or not listed in plugins.yml) are kept as they are.
"""
import hashlib
import json
import os
import urllib.error
import urllib.request
from datetime import datetime

import yaml

OWNER = "evolite"
HEADERS = {"Accept": "application/vnd.github+json", "User-Agent": "stash-index"}
if os.environ.get("GITHUB_TOKEN"):
    HEADERS["Authorization"] = f"Bearer {os.environ['GITHUB_TOKEN']}"


def get(url):
    return urllib.request.urlopen(urllib.request.Request(url, headers=HEADERS), timeout=30)


def latest_release(repo):
    try:
        with get(f"https://api.github.com/repos/{OWNER}/{repo}/releases/latest") as r:
            return json.load(r)
    except urllib.error.HTTPError as e:
        if e.code == 404:  # no release yet
            return None
        raise


def sha256_of(url):
    h = hashlib.sha256()
    with get(url) as r:
        for chunk in iter(lambda: r.read(1 << 16), b""):
            h.update(chunk)
    return h.hexdigest()


def render(entry):
    return (
        f"- id: {entry['id']}\n"
        f"  name: {entry['name']}\n"
        "  metadata:\n"
        f"    description: {entry['metadata']['description']}\n"
        f"  version: {entry['version']}\n"
        f"  date: \"{entry['date']}\"\n"
        f"  path: {entry['path']}\n"
        f"  sha256: {entry['sha256']}\n"
    )


def main():
    entries = yaml.safe_load(open("index.yml")) or []
    by_id = {e["id"]: e for e in entries}
    for p in yaml.safe_load(open("plugins.yml")):
        entry = by_id.get(p["id"])
        if entry is None:
            print(f"skip {p['id']}: not in index.yml")
            continue
        release = latest_release(p["repo"])
        asset = next((a for a in (release or {}).get("assets", []) if a["name"] == p["asset"]), None)
        if asset is None:
            print(f"keep {p['id']}: no GitHub release asset yet")
            continue
        version = release["tag_name"].lstrip("v")
        if str(entry["version"]) == version and entry["path"] == asset["browser_download_url"]:
            print(f"ok   {p['id']} {version}")
            continue
        digest = (asset.get("digest") or "").removeprefix("sha256:") or sha256_of(asset["browser_download_url"])
        entry.update(
            version=version,
            date=datetime.fromisoformat(release["published_at"].replace("Z", "+00:00")).strftime("%Y-%m-%d %H:%M:%S"),
            path=asset["browser_download_url"],
            sha256=digest,
        )
        print(f"new  {p['id']} -> {version}")
    text = "".join(render(e) for e in entries)
    assert yaml.safe_load(text) == entries, "rendered index does not round-trip"
    open("index.yml", "w").write(text)


main()
