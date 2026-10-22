"""Builds shared/kb/<state>.json and shared/kb/general.json, the knowledge the exam advisor (Max) answers questions from.

Source: the full Shopify product descriptions in store/products-full.json. Each description is cut into
its sections ("Exam Details", "Licensing Steps", "State Requirements", "Reference Books", ...) and its FAQ
questions. Every piece is tagged with the product's state and level, and identical pieces (the same section
repeated on every package for a state) are kept once.

Run by build.py; can also be run on its own:  python3 tools/make_kb.py
"""
import hashlib
import html
import json
import os
import re

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
MAX_CHARS = 1100          # one piece stays short so several fit in a single AI request
SKIP_SECTIONS = {"how 1 exam prep helps you reach your goal"}  # sales copy, not answers


def text_of(fragment):
    t = re.sub(r"<(br|/p|/li|/h\d)[^>]*>", "\n", fragment, flags=re.I)
    t = re.sub(r"<[^>]+>", " ", t)
    t = html.unescape(t)
    t = re.sub(r"[ \t\r\f\v]+", " ", t)
    t = re.sub(r"\s*\n\s*", "\n", t)
    return t.strip()


def split_long(text, limit=MAX_CHARS):
    """Cut a long section at sentence ends into pieces of about `limit` characters."""
    if len(text) <= limit:
        return [text]
    sentences = re.split(r"(?<=[.!?])\s+", text.replace("\n", " "))
    out, cur = [], ""
    for s in sentences:
        if cur and len(cur) + len(s) + 1 > limit:
            out.append(cur.strip())
            cur = ""
        cur += s + " "
    if cur.strip():
        out.append(cur.strip())
    return out


def sections(desc_html):
    """Yields (heading, text, is_faq) for each h2/h3 section; FAQ questions become their own pieces."""
    parts = re.split(r"<h[23][^>]*>(.*?)</h[23]>", desc_html, flags=re.S | re.I)
    intro = text_of(parts[0])
    if intro:
        yield ("Overview", intro, False)
    in_faq = False
    for i in range(1, len(parts), 2):
        head = text_of(parts[i])
        body = text_of(parts[i + 1]) if i + 1 < len(parts) else ""
        if re.match(r"(faq|frequently asked)", head, re.I):
            in_faq = True
            if body:
                yield (head, body, False)
            continue
        if head.lower() in SKIP_SECTIONS or not body:
            continue
        yield (head, body, in_faq and head.endswith("?"))


STATE_FACTS = ("Exam Details", "Licensing Steps", "State Requirements", "Open Book Test", "Closed Book Test",
               "Reference Books", "Exam Room Approved Books", "Test Information and Study Materials")


def qkey(q):
    return re.sub(r"\b(this|the|a|an|combo|package|product|kit|set)\b", " ", q.lower()).strip()


def build(catalog, full):
    """Returns {file_key: [pieces]}: one list per state ("florida") plus "general" for nationwide items
    and what each package contains."""
    by_id = {str(p["id"]): p for p in catalog}
    groups = {}
    for pid, info in full.items():
        p = by_id.get(str(pid))
        if p and info.get("html"):
            groups.setdefault((p.get("state") or None, p.get("level")), []).append((p, info["html"]))
    files = {}
    seen_text = set()
    tier_seen = set()

    def add(key, piece):
        norm = re.sub(r"\W+", " ", piece["t"].lower()).strip()
        h = hashlib.md5((key + "|" + (piece.get("l") or "") + "|" + norm).encode()).hexdigest()
        if h in seen_text or len(norm) < 40:
            return
        seen_text.add(h)
        files.setdefault(key, []).append(piece)

    for (state, level), prods in groups.items():
        key = state.lower().replace(" ", "-") if state else "general"
        lvl = level if level in ("Journeyman", "Master") else None
        prods.sort(key=lambda x: -int(x[0].get("rank") or 0))   # most complete package first
        facts_done, faq_done = set(), set()
        for p, desc in prods:
            for head, body, is_faq in sections(desc):
                if is_faq:
                    k = qkey(head)
                    if k in faq_done:
                        continue
                    faq_done.add(k)
                    add(key, {"s": state, "l": lvl, "h": "Q: " + head, "t": body[:MAX_CHARS]})
                elif head in STATE_FACTS:
                    if head in facts_done:
                        continue          # the same facts are repeated on every package for this state
                    facts_done.add(head)
                    for chunk in split_long(body):
                        add(key, {"s": state, "l": lvl, "h": head, "t": chunk})
                elif head == "What You Get" or (head == "Overview" and not state):
                    tk = (p["tier"], lvl, head, key if not state else "")
                    if tk in tier_seen:
                        continue
                    tier_seen.add(tk)
                    for chunk in split_long(body):
                        add("general", {"s": None, "l": lvl, "p": p["tierName"], "h": p["tierName"] + ": " + head, "t": chunk})
    return files


def main():
    cat_js = open(os.path.join(ROOT, "shared", "catalog.js"), encoding="utf-8").read()
    catalog = json.loads(re.search(r"window\.CATALOG\s*=\s*(\[.*?\]);", cat_js, re.S).group(1))
    full = json.load(open(os.path.join(ROOT, "store", "products-full.json"), encoding="utf-8"))
    files = build(catalog, full)
    outdir = os.path.join(ROOT, "shared", "kb")
    os.makedirs(outdir, exist_ok=True)
    for old in os.listdir(outdir):
        if old.endswith(".json") and old[:-5] not in files:
            os.remove(os.path.join(outdir, old))
    total = 0
    for key, pieces in files.items():
        path = os.path.join(outdir, key + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"v": 1, "pieces": pieces}, f, ensure_ascii=False, separators=(",", ":"))
        total += os.path.getsize(path)
    old = os.path.join(ROOT, "shared", "advisor-kb.json")
    if os.path.exists(old):
        os.remove(old)
    return sum(len(v) for v in files.values()), len(files), total


if __name__ == "__main__":
    n, nfiles, size = main()
    print("Advisor knowledge: %d pieces in %d files, %.1f MB" % (n, nfiles, size / 1e6))
