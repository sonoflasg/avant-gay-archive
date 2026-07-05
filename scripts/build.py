#!/usr/bin/env python3
"""Build the Avant Gay archive site from the Obsidian vault.

Usage: python3 scripts/build.py
Reads every .md note in the repo (= the vault), extracts wikilinks and
metadata, injects the graph data into website/template.html, and writes
the finished site to site/index.html.
"""
import json
import re
import shutil
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "website" / "template.html"
OUT = ROOT / "site" / "index.html"

# GitHub repo (owner/name) — used for the Contribute buttons on the site.
REPO = "SonOfLasG/avant-gay-archive"

# Folders/files that are repo plumbing, not archive notes.
EXCLUDE_DIRS = {".obsidian", ".github", ".git", "scripts", "website", "site", "node_modules"}
EXCLUDE_FILES = {"README.md", "CONTRIBUTING.md", "LICENSE.md"}

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")
EMBED = re.compile(r"!\[\[[^\]]+\]\]")
IMG_EMBED = re.compile(r"!\[\[([^\]|]+?\.(?:png|jpe?g|gif|webp))(?:\|[^\]]*)?\]\]", re.I)
IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
SOURCE = re.compile(r"^Source:\s*(\S+)", re.M | re.I)
AUTHOR = re.compile(r"^Author:\s*(.+)$", re.M | re.I)
DATE = re.compile(r"^Date:\s*(.+)$", re.M | re.I)

TYPE_BY_FOLDER = {
    "Artists": "artist",
    "Collections": "collection",
    "ArticlesNthreads": "article",
    "Imagery Reference Character": "reference",
    "VVV": "platform",
}


def canon(name: str) -> str:
    return name.strip().lower()


def collect_files():
    files = []
    for p in ROOT.rglob("*.md"):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in EXCLUDE_DIRS:
            continue
        if len(rel.parts) == 1 and rel.name in EXCLUDE_FILES:
            continue
        files.append(p)
    return files


def image_index():
    """Map lowercase filename -> path, for every image in the vault."""
    idx = {}
    for p in ROOT.rglob("*"):
        rel = p.relative_to(ROOT)
        if rel.parts[0] in EXCLUDE_DIRS:
            continue
        if p.is_file() and p.suffix.lower() in IMG_EXTS:
            idx[p.name.lower()] = p
    return idx


def slugify(name: str) -> str:
    return re.sub(r"[^A-Za-z0-9.\-]+", "-", name).strip("-").lower()


def build_graph():
    notes = {}
    md_files = collect_files()
    images = image_index()
    assets = OUT.parent / "assets"
    copied = {}  # source path -> site-relative url

    def resolve_images(text):
        urls = []
        for m in IMG_EMBED.finditer(text):
            src = images.get(m.group(1).strip().lower())
            if not src:
                continue
            if src not in copied:
                assets.mkdir(parents=True, exist_ok=True)
                dest = assets / slugify(src.name)
                shutil.copy2(src, dest)
                copied[src] = "assets/" + dest.name
            urls.append(copied[src])
        return urls

    for p in md_files:
        name = p.stem
        rel = p.relative_to(ROOT)
        folder = rel.parts[0] if len(rel.parts) > 1 else ""
        text = p.read_text(encoding="utf-8", errors="replace")
        body = EMBED.sub("", text)
        if body.startswith("---"):
            end = body.find("---", 3)
            if end != -1:
                body = body[end + 3:]
        src = SOURCE.search(text)
        author = AUTHOR.search(text)
        date = DATE.search(text)
        clean = re.sub(r"^(Source|Author|Date):.*$", "", body, flags=re.M | re.I)
        clean = re.sub(r"\n{3,}", "\n\n", clean).strip().strip("-").strip()
        notes[canon(name)] = {
            "images": resolve_images(text),
            "id": name,
            "type": TYPE_BY_FOLDER.get(folder, "concept"),
            "folder": folder,
            "summary": clean[:900],
            "source": src.group(1) if src else None,
            "author": author.group(1).strip() if author else None,
            "date": date.group(1).strip() if date else None,
            "stub": len(clean) < 20,
            "outlinks": [],
        }

    links = []
    for p in md_files:
        name = p.stem
        text = p.read_text(encoding="utf-8", errors="replace")
        for m in WIKILINK.finditer(text):
            target = m.group(1).strip()
            ct = canon(target)
            if ct == canon(name):
                continue
            if ct not in notes:
                notes[ct] = {
                    "id": target, "type": "phantom", "folder": "",
                    "summary": "", "source": None, "author": None,
                    "date": None, "stub": True, "outlinks": [], "images": [],
                }
            links.append({"source": name, "target": notes[ct]["id"]})
            notes[canon(name)]["outlinks"].append(notes[ct]["id"])

    seen, uniq = set(), []
    for l in links:
        k = (l["source"], l["target"])
        if k not in seen:
            seen.add(k)
            uniq.append(l)

    backlinks = {}
    for l in uniq:
        backlinks[canon(l["target"])] = backlinks.get(canon(l["target"]), 0) + 1
    for c, n in notes.items():
        n["backlinks"] = backlinks.get(c, 0)
        n["degree"] = n["backlinks"] + len(set(n["outlinks"]))
        del n["outlinks"]

    return {"nodes": list(notes.values()), "links": uniq}


def main():
    data = build_graph()
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__GRAPH_DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__REPO__", REPO)
    OUT.parent.mkdir(parents=True, exist_ok=True)
    OUT.write_text(html, encoding="utf-8")
    print(f"built site/index.html — {len(data['nodes'])} nodes, {len(data['links'])} links")


if __name__ == "__main__":
    main()
