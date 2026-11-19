#!/usr/bin/env python3
"""Build the Avant Gay archive site from the Obsidian vault.

Usage: python3 scripts/build.py
Reads every .md note in the repo (= the vault), extracts wikilinks and
metadata, injects the graph data into website/template.html, and writes
the finished site to site/index.html, plus a machine-readable
export at site/archive.json and site/archive.csv.
"""
import csv
import json
import re
import shutil
import subprocess
import sys
from datetime import datetime, timezone
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
TEMPLATE = ROOT / "website" / "template.html"
OUT = ROOT / "site" / "index.html"

# GitHub repo (owner/name) — used for the Contribute buttons on the site.
REPO = "SonOfLasG/avant-gay-archive"

# Cloudflare Worker URL for anonymous votes (see votes-worker/worker.js).
# Leave empty to hide the vote buttons entirely.
VOTES_URL = "https://avant-gay-votes.sonoflasg.workers.dev"

# Folders/files that are repo plumbing, not archive notes.
EXCLUDE_DIRS = {".obsidian", ".github", ".git", "scripts", "website", "site", "node_modules", "_preview"}
EXCLUDE_FILES = {"README.md", "CONTRIBUTING.md", "LICENSE.md", "AGENTS.md", "REVIEW.md"}

WIKILINK = re.compile(r"\[\[([^\]|#]+)(?:#[^\]|]*)?(?:\|([^\]]+))?\]\]")
EMBED = re.compile(r"!\[\[[^\]]+\]\]")
IMG_EMBED = re.compile(r"!\[\[([^\]|]+?\.(?:png|jpe?g|gif|webp))(?:\|[^\]]*)?\]\]", re.I)
IMG_EXTS = {".png", ".jpg", ".jpeg", ".gif", ".webp"}
SOURCE = re.compile(r"^Source:\s*(\S+)", re.M | re.I)
AUTHOR = re.compile(r"^Author:\s*(.+)$", re.M | re.I)
DATE = re.compile(r"^Date:\s*(.+)$", re.M | re.I)
STATUS = re.compile(r"^Status:\s*(.+)$", re.M | re.I)
XHANDLE = re.compile(r"^X:\s*@?([A-Za-z0-9_]{1,15})\s*$", re.M)
ROLE = re.compile(r"^Role:\s*(.+)$", re.M | re.I)
# Metadata lines: attribution, not graph edges and not summary text.
META_LINE = re.compile(r"^(Source|Author|Date|Status|X|Role):.*$", re.M | re.I)
PFP_DIR = ROOT / "website" / "pfp"

SITE_URL = "https://avantgay.sonoflasg.com"
SOURCES_HEAD = re.compile(r"^(#+\s*)?(\*\*)?(Further\s+)?Sources\b", re.I)  # plural: do not match the Source: header
MD_LINK = re.compile(r"\[([^\]]+)\]\((https?://[^)\s]+)\)")
BARE_URL = re.compile(r"https?://[^\s)\]>\"']+")
HEADING = re.compile(r"^#+\s+")


def pfp_index():
    """handle (lowercase) -> manifest item with a local image."""
    mf = PFP_DIR / "manifest.json"
    if not mf.exists():
        return {}
    items = json.loads(mf.read_text(encoding="utf-8")).get("items", [])
    return {i["handle"].lower(): i for i in items if i.get("image") and (PFP_DIR.parent / i["image"]).exists()}

TYPE_BY_FOLDER = {
    "Artists": "artist",
    "Collections": "collection",
    "ArticlesNthreads": "article",
    "Imagery Reference Character": "reference",
    "VVV": "platform",
    "Platforms": "platform",
    "People": "person",
    "Events": "event",
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



def parse_sources(text: str):
    """URLs from every Sources section, with link text as title when present."""
    lines = text.splitlines()
    chunk, in_s = [], False
    for line in lines:
        if SOURCES_HEAD.match(line.strip()):
            in_s = True
            rest = SOURCES_HEAD.sub("", line, count=1).lstrip(":* ").strip()
            if rest:
                chunk.append(rest)
            continue
        if in_s:
            if HEADING.match(line) or line.strip() == "---":
                in_s = False
                continue
            chunk.append(line)
    blob = "\n".join(chunk)
    out, seen = [], set()
    for m in MD_LINK.finditer(blob):
        title, url = m.group(1).strip(), m.group(2).strip()
        if url not in seen:
            seen.add(url)
            out.append({"title": title, "url": url})
    for m in BARE_URL.finditer(blob):
        url = m.group(0).rstrip(".,;:")
        if url not in seen:
            seen.add(url)
            out.append({"title": None, "url": url})
    return out


def first_line(clean: str) -> str:
    """First non-empty body line, with light markdown stripped."""
    for line in clean.splitlines():
        s = line.strip().lstrip("-*# ").strip()
        if not s:
            continue
        s = MD_LINK.sub(r"\1", s)
        s = re.sub(r"\[\[([^\]|]+)(?:\|([^\]]+))?\]\]", lambda m: m.group(2) or m.group(1), s)
        s = re.sub(r"\*\*([^*]+)\*\*", r"\1", s)
        s = re.sub(r"\*([^*]+)\*", r"\1", s)
        return s[:300]
    return ""


def git_last_modified():
    """Relative vault path -> ISO date of the latest commit that touched it."""
    out = {}
    try:
        proc = subprocess.run(
            ["git", "log", "--format=%cI", "--name-only", "--diff-filter=ACMR"],
            cwd=ROOT, capture_output=True, text=True, check=False,
        )
    except OSError:
        return out
    if proc.returncode != 0:
        return out
    date = None
    for line in proc.stdout.splitlines():
        if not line:
            continue
        if len(line) >= 20 and line[0].isdigit() and "T" in line[:20]:
            date = line.strip()
            continue
        if date and line.endswith(".md") and line not in out:
            out[line] = date
    return out


def export_status(node):
    if node.get("type") == "phantom":
        return "phantom"
    st = (node.get("status") or "").lower()
    if st.startswith("needs-sources"):
        return "needs-sources"
    return "written"


def generated_at():
    try:
        from zoneinfo import ZoneInfo
        return datetime.now(ZoneInfo("Australia/Melbourne")).isoformat(timespec="seconds")
    except Exception:
        return datetime.now(timezone.utc).isoformat(timespec="seconds")


def scan_export(path: Path):
    """Run the validator's wallet/secret checks on an export file."""
    try:
        import validate  # late: validate already imports this module
    except Exception as e:
        print(f"warning: could not scan {path.name} ({e})")
        return
    rel = str(path.relative_to(ROOT))
    lines = [(i + 1, line) for i, line in enumerate(path.read_text(encoding="utf-8").splitlines())]
    rep = validate.Report()
    validate.scan_privacy(rep, rel, lines, strict=True)
    for w in rep.warnings:
        print("export warning:", w)
    if rep.errors:
        for err in rep.errors:
            print("export error:", err)
        sys.exit(f"refusing to write a live export that fails the privacy scan: {path.name}")


def write_export(data):
    """Write site/archive.json and site/archive.csv from the graph + vault files."""
    lastmod = git_last_modified()
    entries = []
    for n in data["nodes"]:
        header = (n.get("status") or "").lower()
        rec = {
            "title": n["id"],
            "path": n.get("path"),
            "type": n["type"] if n["type"] != "phantom" else "phantom",
            "folder": n.get("folder") or None,
            "status": export_status(n),
            "contested": header.startswith("contested"),
            "summary": first_line(n.get("summary") or ""),
            "xHandle": n.get("xHandle"),
            "roles": list(n.get("roles") or []),
            "community": bool(n.get("community")),
            "links": list(n.get("outlinks") or []),
            "backlinks": n.get("backlinks", 0),
            "sources": n.get("sources") or [],
            "date": n.get("date"),
            "lastModified": lastmod.get(n["path"]) if n.get("path") else None,
        }
        entries.append(rec)
    entries.sort(key=lambda e: (e["title"] or "").lower())
    payload = {
        "archive": "Avant Gay Archive",
        "url": SITE_URL + "/",
        "data": SITE_URL + "/archive.json",
        "csv": SITE_URL + "/archive.csv",
        "license": "CC BY-SA 4.0",
        "licenseUrl": "https://creativecommons.org/licenses/by-sa/4.0/",
        "attribution": "Cite the Avant Gay Archive and the entry's own sources.",
        "generated": generated_at(),
        "entryCount": len(entries),
        "entries": entries,
    }
    OUT.parent.mkdir(parents=True, exist_ok=True)
    json_path = OUT.parent / "archive.json"
    csv_path = OUT.parent / "archive.csv"
    json_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8")
    with csv_path.open("w", encoding="utf-8", newline="") as f:
        w = csv.writer(f)
        w.writerow(["title", "path", "type", "folder", "status", "contested",
                    "summary", "xHandle", "roles", "community", "links", "backlinks", "sources",
                    "date", "lastModified"])
        for e in entries:
            sources = "; ".join(
                (s["title"] + " | " + s["url"]) if s.get("title") else s["url"]
                for s in e["sources"]
            )
            w.writerow([
                e["title"], e["path"] or "", e["type"], e["folder"] or "",
                e["status"], "true" if e["contested"] else "false",
                e["summary"], e["xHandle"] or "", "; ".join(e["roles"]),
                "true" if e["community"] else "false",
                "; ".join(e["links"]),
                e["backlinks"], sources, e["date"] or "", e["lastModified"] or "",
            ])
    scan_export(json_path)
    scan_export(csv_path)
    print(f"wrote site/archive.json and site/archive.csv — {len(entries)} entries")


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

    pfps = pfp_index()
    if pfps:
        dest = OUT.parent / "pfp"
        dest.mkdir(parents=True, exist_ok=True)
        for item in pfps.values():
            shutil.copy2(PFP_DIR.parent / item["image"], dest / Path(item["image"]).name)

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
        status = STATUS.search(text)
        xh = XHANDLE.search(text)
        handle = xh.group(1) if xh else None
        pfp = pfps.get(handle.lower()) if handle else None
        role_m = ROLE.search(text)
        roles = []
        if role_m:
            roles = [r.strip().lower() for r in role_m.group(1).split(",") if r.strip()]
        clean = META_LINE.sub("", body)
        clean = re.sub(r"\n{3,}", "\n\n", clean).strip().strip("-").strip()
        notes[canon(name)] = {
            "images": resolve_images(text),
            "id": name,
            "type": TYPE_BY_FOLDER.get(folder, "concept"),
            "folder": folder,
            "path": rel.as_posix(),
            # Full note text: longer compiled entries need to be readable in the panel.
            "summary": clean[:20000],
            "source": src.group(1) if src else None,
            "author": author.group(1).strip() if author else None,
            "date": date.group(1).strip() if date else None,
            "status": status.group(1).strip() if status else None,
            "stub": len(clean) < 20,
            "xHandle": handle,
            "roles": roles,
            "community": "community" in roles,
            "pfp": pfp["image"] if pfp else None,
            "pfpCaptured": pfp["captured"].split(" ")[0] if pfp else None,
            "sources": parse_sources(text),
            "outlinks": [],
        }

    links = []
    for p in md_files:
        name = p.stem
        text = p.read_text(encoding="utf-8", errors="replace")
        # Metadata fields are attribution, not graph edges.
        link_text = META_LINE.sub("", text)
        for m in WIKILINK.finditer(link_text):
            target = m.group(1).strip()
            ct = canon(target)
            if ct == canon(name):
                continue
            if ct not in notes:
                notes[ct] = {
                    "id": target, "type": "phantom", "folder": "",
                    "path": None, "summary": "", "source": None, "author": None,
                    "date": None, "status": None, "stub": True, "outlinks": [], "images": [],
                    "xHandle": None, "roles": [], "community": False,
                    "pfp": None, "pfpCaptured": None, "sources": [],
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
        n["outlinks"] = list(dict.fromkeys(n["outlinks"]))
        n["backlinks"] = backlinks.get(c, 0)
        n["degree"] = n["backlinks"] + len(n["outlinks"])

    return {"nodes": list(notes.values()), "links": uniq}


def main():
    data = build_graph()
    OUT.parent.mkdir(parents=True, exist_ok=True)
    write_export(data)
    for n in data["nodes"]:
        n.pop("path", None)
        n.pop("sources", None)
        n.pop("outlinks", None)
    html = TEMPLATE.read_text(encoding="utf-8")
    html = html.replace("__GRAPH_DATA__", json.dumps(data, ensure_ascii=False))
    html = html.replace("__REPO__", REPO)
    html = html.replace("__VOTES_URL__", VOTES_URL)
    OUT.write_text(html, encoding="utf-8")
    # site icons (favicon.svg, favicon.ico, favicon-32.png, apple-touch-icon.png)
    for icon in (ROOT / "website" / "icons").glob("*"):
        if icon.is_file():
            shutil.copy2(icon, OUT.parent / icon.name)
    print(f"built site/index.html — {len(data['nodes'])} nodes, {len(data['links'])} links")


if __name__ == "__main__":
    main()
