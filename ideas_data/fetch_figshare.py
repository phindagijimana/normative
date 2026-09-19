"""Resolve IDEAS Figshare share tokens to file downloads.

Figshare's private-share flow is JS-driven and gated by AWS WAF, so we drive a
real Firefox via Playwright, wait for the article page to render, and intercept
the `getSharedItemFiles` GraphQL response to harvest file IDs. We then hit
`ndownloader.figshare.com/files/<id>?private_link=<token>` directly.
"""

from __future__ import annotations

import json
import sys
import urllib.request
from pathlib import Path

from playwright.sync_api import sync_playwright

TOKENS = {
    "freesurfer_stats": "010142dd51e37ba4e4e2",
    "clinical_metadata": "bab70268afeb1071202b",
    "ideas_z_scores": "8c086fc295a75f85e628",
}

OUT_DIR = Path(__file__).resolve().parent


def harvest(token: str) -> dict:
    """Return {title, files:[{id,name,size}]} for one share token."""
    with sync_playwright() as p:
        browser = p.firefox.launch(headless=True)
        page = browser.new_context().new_page()

        graphql_payloads: list[dict] = []

        def _on_response(resp):
            if "graphql" not in resp.url:
                return
            if "getSharedItemFiles" not in resp.url and \
                    "masterQuery" not in resp.url and \
                    "getRelatedMaterials" not in resp.url:
                return
            try:
                graphql_payloads.append({
                    "url": resp.url,
                    "body": resp.json(),
                })
            except Exception:
                pass

        page.on("response", _on_response)
        page.goto(f"https://figshare.com/s/{token}", wait_until="networkidle", timeout=60_000)
        page.wait_for_timeout(3_000)
        title = page.title()
        browser.close()

    files: list[dict] = []
    for entry in graphql_payloads:
        body = entry["body"]
        # Walk the JSON looking for objects that look like Figshare file records:
        # {id: <int>, name: <str>, size: <int>, ...}
        stack: list = [body]
        while stack:
            node = stack.pop()
            if isinstance(node, dict):
                if all(k in node for k in ("id", "name", "size")) and \
                        isinstance(node["id"], int) and \
                        isinstance(node["name"], str):
                    if not any(f["id"] == node["id"] for f in files):
                        files.append({"id": node["id"], "name": node["name"], "size": node["size"]})
                stack.extend(node.values())
            elif isinstance(node, list):
                stack.extend(node)

    if not files:
        raise RuntimeError(f"No files found in GraphQL payloads for token {token}. "
                           f"Payload URLs seen: {[p['url'] for p in graphql_payloads]}")
    return {"title": title, "files": files}


def download(file_id: int, token: str, dest: Path) -> None:
    url = f"https://ndownloader.figshare.com/files/{file_id}?private_link={token}"
    req = urllib.request.Request(url, headers={"User-Agent": "Mozilla/5.0"})
    with urllib.request.urlopen(req) as r, dest.open("wb") as out:
        while chunk := r.read(1 << 20):
            out.write(chunk)


def main() -> int:
    manifest: dict[str, dict] = {}
    for label, token in TOKENS.items():
        print(f"[{label}] resolving share token {token} ...", flush=True)
        info = harvest(token)
        print(f"  title: {info['title']}")
        for f in info["files"]:
            print(f"  file: id={f['id']} name={f['name']} size={f['size']:,}")
        for f in info["files"]:
            dest = OUT_DIR / f["name"]
            print(f"  -> downloading {dest.name} ...", flush=True)
            download(f["id"], token, dest)
            actual = dest.stat().st_size
            print(f"     saved {actual:,} bytes (expected {f['size']:,})")
        manifest[label] = info

    (OUT_DIR / "manifest.json").write_text(json.dumps(manifest, indent=2))
    print("done.")
    return 0


if __name__ == "__main__":
    sys.exit(main())
