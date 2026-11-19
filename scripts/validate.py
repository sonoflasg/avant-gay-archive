#!/usr/bin/env python3
"""Validate archive entries before review.

Usage:
  python3 scripts/validate.py                 # check entries changed vs origin/main
  python3 scripts/validate.py --base <ref>    # check entries changed vs another ref
  python3 scripts/validate.py --all           # scan the whole vault (privacy + build)
  python3 scripts/validate.py --files a.md b.md   # check specific files as if new

Errors (exit 1) block a pull request. Warnings are for the reviewer.
No dependencies beyond Python 3 and git. Read-only: never writes to the repo.
See AGENTS.md for the rules these checks enforce.
"""
import argparse
import difflib
import os
import re
import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent.parent
sys.path.insert(0, str(ROOT / "scripts"))
sys.dont_write_bytecode = True
import build  # noqa: E402

DATE_RE = re.compile(r"^\d{2}/\d{2}/\d{4}$")
META_RE = re.compile(r"^(Source|Author|Date|Status|X|Role):", re.I)
X_FIELD = re.compile(r"^@[A-Za-z0-9_]{1,15}$")
STATUS_OK = ("needs-sources", "contested")
URL_RE = re.compile(r"https?://[^\s)\]>\"']+")
SOURCES_HEAD = re.compile(r"^(#+\s*)?(\*\*)?(Further\s+)?Sources?\b", re.I)
REVISION_HEAD = re.compile(r"^#+\s*(Revisions?|Corrections?)\b", re.I)
PERSPECTIVE_HEAD = re.compile(r"^#+\s*(Perspectives?|Contested|Disputed|Competing accounts|Side by side)\b", re.I)
X_LINK = re.compile(r"https?://(?:www\.|mobile\.)?(?:x|twitter)\.com/[^\s)\]>\"']*", re.I)
X_OK = re.compile(r"^https://x\.com/[A-Za-z0-9_]{1,15}(?:/status/\d{5,25}(?:/(?:photo|video)/\d)?)?/?$")
ETH_RE = re.compile(r"\b0x[a-fA-F0-9]{40}\b")
SOL_RE = re.compile(r"(?<![A-Za-z0-9])[1-9A-HJ-NP-Za-km-z]{32,44}(?![A-Za-z0-9])")
INVITE_RE = re.compile(r"(discord\.gg/|discord(?:app)?\.com/invite/|t\.me/|telegram\.me/|chat\.whatsapp\.com/|signal\.group/)", re.I)
PRIVATE_RE = re.compile(r"\b(DMs?|DM'?d|direct message|private message|group ?chat|gc screenshot|leaked chat|telegram|discord server)\b", re.I)
SHILL_RE = re.compile(r"\b(floor price|buy now|mint now|not financial advice|NFA|to the moon|undervalued|ape in|sweep the floor)\b", re.I)
WORDS = set((ROOT / "scripts" / "bip39-english.txt").read_text().split())


class Report:
    def __init__(self):
        self.errors, self.warnings = [], []

    def err(self, f, msg):
        self.errors.append(f"{f}: {msg}")

    def warn(self, f, msg):
        self.warnings.append(f"{f}: {msg}")


def git(*args):
    return subprocess.run(["git", *args], cwd=ROOT, capture_output=True, text=True)


def is_entry(rel: str) -> bool:
    p = Path(rel)
    if p.suffix != ".md" or p.parts[0] in build.EXCLUDE_DIRS:
        return False
    return not (len(p.parts) == 1 and p.name in build.EXCLUDE_FILES)


def split_header(text):
    """Return (header dict, body lines). Header = metadata lines before the first '---' or prose."""
    meta, lines = {}, text.splitlines()
    for line in lines[:12]:
        m = META_RE.match(line)
        if m:
            meta[m.group(1).lower()] = line.split(":", 1)[1].strip()
    return meta, lines


def seed_runs(text):
    toks = re.findall(r"[a-z]+", text.lower())
    run = 0
    for t in toks:
        run = run + 1 if t in WORDS else 0
        if run >= 12:
            return True
    return False


def scan_privacy(rep, f, lines, strict):
    """Privacy/safety checks on the given lines. strict=True for added lines in a PR."""
    say = rep.err if strict else rep.warn  # existing vault text is reported, new text is blocked
    for i, line in lines:
        no_urls = URL_RE.sub(" ", line)
        if ETH_RE.search(no_urls):
            say(f, f"line {i}: looks like an Ethereum wallet/contract address; remove it (link a public page instead)")
        elif ETH_RE.search(line):
            rep.warn(f, f"line {i}: URL contains a 0x address; fine for a public collection contract, never for a personal wallet")
        for m in SOL_RE.finditer(no_urls):
            tok = m.group(0)
            if re.search(r"\d", tok) and re.search(r"[A-Z]", tok) and re.search(r"[a-z]", tok):
                say(f, f"line {i}: looks like a Solana address ({tok[:6]}…); remove it")
                break
        if INVITE_RE.search(line):
            say(f, f"line {i}: chat invite link (Discord/Telegram/WhatsApp/Signal); link public posts instead")
        if strict and PRIVATE_RE.search(line):
            rep.warn(f, f"line {i}: mentions DMs/private chats; private material needs the consent of everyone in it — reviewer to confirm")
        if strict and SHILL_RE.search(line):
            rep.warn(f, f"line {i}: market/shill language; the archive documents, it does not promote")
    text = "\n".join(l for _, l in lines)
    if seed_runs(text):
        say(f, "contains a run of 12+ seed-phrase words; never paste seed phrases or keys")


def check_x_links(rep, f, lines):
    for i, line in lines:
        for m in X_LINK.finditer(line):
            url = m.group(0).rstrip(".,;:")
            if not X_OK.match(url):
                rep.warn(f, f"line {i}: X link not in canonical form https://x.com/<handle>/status/<id> (no ?s=/tracking, no twitter.com): {url}")
            elif "/status/" in url:
                window = " ".join(l for j, l in lines if abs(j - i) <= 1)
                if not re.search(r"\b(AEDT|AEST)\b", window):
                    rep.warn(f, f"line {i}: X post cited without a Melbourne-time date (AEDT/AEST) nearby")


def check_entry_shape(rep, f, text, new):
    meta, lines = split_header(text)
    for field in ("source", "author", "date"):
        if field not in meta:
            (rep.err if new else rep.warn)(f, f"missing '{field.capitalize()}:' header line")
    if "date" in meta and not DATE_RE.match(meta["date"]):
        rep.warn(f, f"Date '{meta['date']}' is not DD/MM/YYYY (fine only if the source gives no exact date)")
    if "author" in meta and "[[" in meta["author"]:
        rep.warn(f, "Author is metadata, not a graph edge: write plain text (e.g. SonOfLasG), not a [[wikilink]]")
    if "x" in meta and not X_FIELD.match(meta["x"]):
        rep.err(f, f"X field '{meta['x']}' must be a single handle like '@handle' (the account's own public X handle)")
    if "status" in meta and not meta["status"].lower().startswith(STATUS_OK):
        rep.err(f, f"Status '{meta['status']}' must be one of: {', '.join(STATUS_OK)} (or omit the line)")
    if "role" in meta:
        roles = [r.strip().lower() for r in meta["role"].split(",") if r.strip()]
        unknown = [r for r in roles if r not in ("community",)]
        if not roles or unknown:
            rep.err(f, f"Role '{meta['role']}' must be 'community' (comma-separated known roles are allowed later)")
        if "[[" in meta["role"]:
            rep.warn(f, "Role is metadata, not a graph edge: write plain text (e.g. community), not a [[wikilink]]")
    if not any(l.strip() == "---" for l in lines[:14]):
        rep.warn(f, "no '---' line separating the header from the body")
    status = meta.get("status", "").lower()
    has_sources = False
    for idx, l in enumerate(lines):
        if SOURCES_HEAD.match(l.strip()) and any(URL_RE.search(x) for x in lines[idx:idx + 15]):
            has_sources = True
            break
    if not has_sources:
        if status.startswith("needs-sources"):
            rep.warn(f, "no Sources section with a URL (allowed while Status: needs-sources)")
        elif not new and URL_RE.match(meta.get("source", "")):
            rep.warn(f, "legacy entry without a Sources section (its Source: header has a URL); consider adding one")
        else:
            rep.err(f, "needs a 'Sources:' section with at least one public URL, or 'Status: needs-sources'")
    if "[[" not in "\n".join(l for l in lines if not META_RE.match(l)):
        rep.warn(f, "no [[wikilinks]] in the body; the entry will float disconnected in the graph")


def section_of(lines):
    """Map line index -> current heading text."""
    cur, out = "", []
    for l in lines:
        if l.lstrip().startswith("#"):
            cur = l.strip()
        out.append(cur)
    return out


def check_removals(rep, f, old, new):
    """A change to existing prose must not silently remove cited claims."""
    o, n = old.splitlines(), new.splitlines()
    sm = difflib.SequenceMatcher(a=o, b=n, autojunk=False)
    removed, added = [], []
    for tag, a1, a2, b1, b2 in sm.get_opcodes():
        if tag in ("replace", "delete"):
            removed += [(k, o[k]) for k in range(a1, a2)]
        if tag in ("replace", "insert"):
            added += [(k, n[k]) for k in range(b1, b2)]
    new_text = new
    lost = []
    for k, line in removed:
        s = line.strip()
        if not s or META_RE.match(s) or s in new_text:
            continue
        urls = URL_RE.findall(s)
        cited = bool(urls) or len(s) >= 80
        if not cited:
            continue
        # treat as an edit, not a removal, if a near-identical line was added and its URLs survive
        near = any(difflib.SequenceMatcher(a=s, b=a.strip()).ratio() > 0.85 for _, a in added)
        if near and all(u in new_text for u in urls):
            continue
        lost.append((k + 1, s, bool(urls)))
    if not lost:
        return
    secs = section_of(n)
    noted = any(REVISION_HEAD.match(secs[k]) or PERSPECTIVE_HEAD.match(secs[k]) for k, _ in added)
    noted = noted or any(re.search(r"\b(Revised|Corrected|Rewritten)\s+\d{2}/\d{2}/\d{4}", a) for _, a in added)
    for ln, s, has_url in lost:
        msg = f"removes {'a cited claim' if has_url else 'existing prose'} from old line {ln}: “{s[:90]}…”"
        if noted:
            rep.warn(f, msg + " (a Revisions/Perspectives note was added — reviewer to check it explains this)")
        elif has_url:
            rep.err(f, msg + ". Corrections need a '### Revisions' note citing the source that shows the error; disputes add a '### Perspectives' section and keep the original claim")
        else:
            rep.warn(f, msg + ". If this corrects an error, add a '### Revisions' note")



def revisions_cite_old_path(text, old_path):
    """True if a Revisions section mentions the previous entry path."""
    in_rev = False
    for line in text.splitlines():
        if REVISION_HEAD.match(line):
            in_rev = True
            continue
        if in_rev:
            if line.startswith("#") or SOURCES_HEAD.match(line):
                break
            if old_path in line:
                return True
    return False


def documented_retitle(old_path, diff):
    """New or renamed entry whose Revisions note records a move from old_path."""
    for row in diff:
        parts = row.split("\t")
        st, path = parts[0], parts[-1]
        if not (st.startswith("A") or st.startswith("R")):
            continue
        if not is_entry(path):
            continue
        fp = ROOT / path
        if fp.exists() and revisions_cite_old_path(
            fp.read_text(encoding="utf-8", errors="replace"), old_path
        ):
            return path
    return None


def phantoms(rep, base):
    head = {n["id"].lower() for n in build.build_graph()["nodes"] if n["type"] == "phantom"}
    if not base:
        return head
    wt = Path("/tmp") / f"agv-base-{os.getpid()}"
    if git("worktree", "add", "-q", "--detach", str(wt), base).returncode != 0:
        return head
    try:
        out = subprocess.run([sys.executable, "-B", "-c",
            "import sys,json;sys.path.insert(0,'scripts');import build;"
            "build.OUT=build.ROOT/'.validate-tmp'/'index.html';"
            "print(json.dumps([n['id'].lower() for n in build.build_graph()['nodes'] if n['type']=='phantom']))"],
            cwd=wt, capture_output=True, text=True)
        import json
        before = set(json.loads(out.stdout or "[]"))
    finally:
        git("worktree", "remove", "--force", str(wt))
    for p in sorted(head - before):
        rep.warn("graph", f"new phantom node [[{p}]] (linked but has no entry) — check spelling against existing filenames, or write the entry")
    return head


def check_pr_body(rep, body):
    if not body.strip():
        rep.warn("PR", "empty description; use the pull request template")
        return
    if not re.search(r"- \[x\]", body, re.I):
        rep.warn("PR", "no change type ticked in the template")
    m = re.search(r"LLM / agent used[^:\n]*:[ \t]*(.*)", body, re.I)
    if not m or not m.group(1).strip() or m.group(1).strip().startswith("<!--"):
        rep.warn("PR", "AI disclosure not filled in (write 'none' if you did not use one)")
    m = re.search(r"Credit as[^:\n]*:[ \t]*(.*)", body, re.I)
    if not m or not m.group(1).strip() or m.group(1).strip().startswith("<!--"):
        rep.warn("PR", "contributor credit not filled in")


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--base", default=os.environ.get("VALIDATE_BASE", "origin/main"))
    ap.add_argument("--all", action="store_true")
    ap.add_argument("--files", nargs="*")
    a = ap.parse_args()
    rep = Report()
    base = None

    if a.files:
        targets = [(f, None) for f in a.files]
    elif a.all:
        targets = []
        scanned = 0
        for p in build.collect_files():
            scanned += 1
            rel = str(p.relative_to(ROOT))
            text = p.read_text(encoding="utf-8", errors="replace")
            scan_privacy(rep, rel, list(enumerate(text.splitlines(), 1)), strict=False)
    else:
        base = a.base
        mb = git("merge-base", base, "HEAD")
        if mb.returncode != 0:
            sys.exit(f"cannot find base '{base}' (fetch it, or pass --base)")
        base = mb.stdout.strip()
        diff = git("diff", "--name-status", "-M", base, "--").stdout.splitlines()
        diff += [f"A\t{x}" for x in git("ls-files", "-o", "--exclude-standard").stdout.splitlines()]
        targets = []
        retitled = set()
        for row in diff:
            parts = row.split("\t")
            st, path = parts[0], parts[-1]
            if st.startswith("D"):
                if is_entry(parts[1]):
                    stem = Path(parts[1]).stem.lower()
                    if any(Path(r.split("\t")[-1]).stem.lower() == stem and not r.startswith("D") for r in diff):
                        rep.warn(parts[1], "entry moved to another folder (same name, so links still resolve)")
                    else:
                        dest = documented_retitle(parts[1], diff)
                        if dest:
                            old = git("show", f"{base}:{parts[1]}").stdout
                            targets.append((dest, old))
                            retitled.add(dest)
                            rep.warn(parts[1], f"entry retitled to {dest} (Revisions note records the old path)")
                        else:
                            rep.err(parts[1], "deletes an entry; entries are not deleted (mark Status: needs-sources or add a Revisions note instead)")
                continue
            if is_entry(path):
                if path in retitled:
                    continue
                old = None
                if st.startswith(("M", "R")):
                    oldpath = parts[1]
                    old = git("show", f"{base}:{oldpath}").stdout
                targets.append((path, old))

    for path, old in targets:
        fp = ROOT / path
        if not fp.exists():
            rep.err(path, "file not found")
            continue
        text = fp.read_text(encoding="utf-8", errors="replace")
        new_lines = text.splitlines()
        if old is None:
            changed = list(enumerate(new_lines, 1))
        else:
            sm = difflib.SequenceMatcher(a=old.splitlines(), b=new_lines, autojunk=False)
            changed = [(k + 1, new_lines[k]) for t, _, _, b1, b2 in sm.get_opcodes() if t in ("replace", "insert") for k in range(b1, b2)]
        scan_privacy(rep, path, changed, strict=True)
        check_x_links(rep, path, changed)
        if old is not None and changed and all(META_RE.match(l) for _, l in changed):
            # metadata-only edit (e.g. adding an X: handle): check the field, not the whole legacy entry
            meta, _ = split_header(text)
            if "x" in meta and not X_FIELD.match(meta["x"]):
                rep.err(path, f"X field '{meta['x']}' must be a single handle like '@handle'")
            check_removals(rep, path, old, text)
            continue
        check_entry_shape(rep, path, text, new=old is None)
        if old is not None:
            check_removals(rep, path, old, text)

    try:
        build.OUT = ROOT / "site" / "index.html"
        data = build.build_graph()
        nn = len(data["nodes"])
    except Exception as e:  # noqa: BLE001
        rep.err("build", f"scripts/build.py failed: {e}")
        nn = 0
    if not a.all and not a.files:
        phantoms(rep, base)
    if os.environ.get("PR_BODY") is not None:
        check_pr_body(rep, os.environ["PR_BODY"])

    for w in rep.warnings:
        print(f"WARN  {w}")
    for e in rep.errors:
        print(f"ERROR {e}")
    if a.all:
        print(f"\nscanned {scanned} entries (existing text: warnings only)")
    print(f"{len(targets)} changed entr{'y' if len(targets) == 1 else 'ies'} checked · graph builds ({nn} nodes) · "
          f"{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)")
    summary = os.environ.get("GITHUB_STEP_SUMMARY")
    if summary:
        with open(summary, "a") as fh:
            fh.write("## Archive validator\n\n")
            for e in rep.errors:
                fh.write(f"- ❌ {e}\n")
            for w in rep.warnings:
                fh.write(f"- ⚠️ {w}\n")
            fh.write(f"\n{len(rep.errors)} error(s), {len(rep.warnings)} warning(s)\n")
    sys.exit(1 if rep.errors else 0)


if __name__ == "__main__":
    main()
