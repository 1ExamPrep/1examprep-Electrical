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


NUM_WORDS = {"one": 1, "two": 2, "three": 3, "four": 4, "five": 5, "six": 6, "seven": 7, "eight": 8}
EXP_SENT = re.compile(r"([^.]*?\b(\d{1,2},\d{3}|\d{3,5}|\d{1,2}|one|two|three|four|five|six|seven|eight)\s*(?:\+\s*)?(hours|years)\b[^.]*\.)", re.I)


def to_hours(num, unit):
    n = NUM_WORDS.get(num.lower()) or int(num.replace(",", ""))
    return n * 2000 if unit.lower().startswith("year") else n


def requirements(files):
    """One line per state and level saying how much work experience is needed, plus a nationwide summary,
    so 'is 3 years enough?' gets a real answer even before the customer names a state."""
    out, by_level = [], {"Journeyman": [], "Master": []}
    local = {"Journeyman": [], "Master": []}
    for key, pieces in files.items():
        if key in ("general", "requirements"):
            continue
        for level in ("Journeyman", "Master"):
            best = None
            for p in pieces:
                if p.get("l") != level:
                    continue
                rank = 0 if p["h"].startswith("Q:") and re.search(r"experience|hours|years|qualif", p["h"], re.I) else (1 if p["h"] in ("Licensing Steps", "State Requirements", "Exam Details") else 2)
                for m in EXP_SENT.finditer(p["t"]):
                    sent = m.group(1).strip()
                    if not re.search(r"experience|training|on-the-job|work|apprentic|license for", sent, re.I):
                        continue
                    if re.search(r"minutes|time limit|renew|continuing|exam lasts|to complete the exam|substitut", sent, re.I):
                        continue
                    hrs = to_hours(m.group(2), m.group(3))
                    if hrs < 1000:          # "2 years" of holding a license etc. still counts below via the sentence
                        hrs = None
                    cand = (rank, sent, hrs, p["s"])
                    if best is None or cand[0] < best[0]:
                        best = cand
            if best:
                rank, sent, hrs, state = best
                out.append({"s": state, "l": level, "h": "Experience required", "t": sent, "hrs": hrs})
                if hrs:
                    by_level[level].append((state, hrs))
            else:
                st = next((p["s"] for p in pieces if p.get("s")), None)
                if st and any(p.get("l") == level for p in pieces):
                    local[level].append(st)
    j = [h for _, h in by_level["Journeyman"] if h >= 4000]
    if j:
        common = max(set(j), key=j.count)
        more = sorted({(st, h) for st, h in by_level["Journeyman"] if h > common}, key=lambda r: -r[1])[:3]
        text = ("It depends on the state, but most states ask for %s hours of supervised electrical work (about %s years full time) "
                "before you can get a journeyman license." % (format(common, ","), common // 2000))
        if more:
            text += " A few ask for more, like " + " and ".join("%s (%s hours)" % (st, format(h, ",")) for st, h in more) + "."
        text += " Some states let school or an apprenticeship count toward the hours. Tell me your state for the exact rule."
        out.insert(0, {"s": None, "l": "Journeyman", "h": "Experience required by state", "t": text})
    m = [(st, h) for st, h in by_level["Master"] if h >= 10000]
    if by_level["Master"]:
        text = ("A master license takes more than journeyman. Many states want about 2 more years of work after you hold a journeyman license, "
                "and some count total hours instead")
        if m:
            text += ", like " + " and ".join("%s (%s hours)" % (st, format(h, ",")) for st, h in sorted(m, key=lambda r: -r[1])[:3])
        text += ". Tell me your state for the exact rule."
        out.insert(1 if j else 0, {"s": None, "l": "Master", "h": "Experience required by state", "t": text})
    return out


def main():
    cat_js = open(os.path.join(ROOT, "shared", "catalog.js"), encoding="utf-8").read()
    catalog = json.loads(re.search(r"window\.CATALOG\s*=\s*(\[.*?\]);", cat_js, re.S).group(1))
    full = json.load(open(os.path.join(ROOT, "store", "products-full.json"), encoding="utf-8"))
    files = build(catalog, full)
    files["requirements"] = requirements(files)
    # Slim product list for the advisor's server: just what it needs to pick packages (the full catalog.js
    # carries long descriptions and is too heavy to read on every question).
    files["products"] = [{"id": str(p["id"]), "state": p.get("state"), "level": p.get("level"),
                          "year": p.get("year"), "tier": p.get("tier"), "tierName": p.get("tierName"), "rank": p.get("rank") or 0,
                          "price": p.get("price"), "variants": [{"available": v.get("available", True)} for v in p.get("variants", [])[:1]]}
                         for p in catalog]
    # Ready-made word lists so the advisor's server does not have to split the text on every question.
    stop = set(("a an the and or of to in on for is are am be do does did i im my me we you your it its this that "
                "what which who how when where why can could would should will with from at by as about if so get need want "
                "electrician electrical exam test license licence state").split())
    def words(t):
        return " ".join(sorted({w for w in re.sub(r"[^a-z0-9 ]", " ", t.lower()).split() if len(w) > 1 and w not in stop}))
    for key, pieces in files.items():
        if key == "products":
            continue
        for p in pieces:
            p["k"] = words(p["h"] + " " + p["t"])
            p["kh"] = words(p["h"])
    outdir = os.path.join(ROOT, "shared", "kb")
    os.makedirs(outdir, exist_ok=True)
    for old in os.listdir(outdir):
        if old.endswith(".json") and old[:-5] not in files:
            os.remove(os.path.join(outdir, old))
    total = 0
    for key, pieces in files.items():
        path = os.path.join(outdir, key + ".json")
        with open(path, "w", encoding="utf-8") as f:
            json.dump({"v": 1, ("items" if key == "products" else "pieces"): pieces}, f, ensure_ascii=False, separators=(",", ":"))
        total += os.path.getsize(path)
    old = os.path.join(ROOT, "shared", "advisor-kb.json")
    if os.path.exists(old):
        os.remove(old)
    return sum(len(v) for v in files.values()), len(files), total


if __name__ == "__main__":
    n, nfiles, size = main()
    print("Advisor knowledge: %d pieces in %d files, %.1f MB" % (n, nfiles, size / 1e6))
