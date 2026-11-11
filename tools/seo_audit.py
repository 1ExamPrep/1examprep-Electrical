#!/usr/bin/env python3
"""Grade the built pages against "What every page and post needs to pass" (the page test, the AI readiness checks
and the pre-publish blockers). Run after python3 build.py:

    python3 tools/seo_audit.py .                    # summary of every check that is not passing everywhere
    python3 tools/seo_audit.py . --only texas/ --verbose   # every non-passing check, page by page

Priority 3 = must-have, 2 = recommended, 1 = nice-to-have, as in the checklist.
"""
import sys, os, re, json, collections
from bs4 import BeautifulSoup

ROOT = sys.argv[1]
_cfg = json.load(open(os.path.join(ROOT, "site-config.json"), encoding="utf-8")) if os.path.exists(os.path.join(ROOT, "site-config.json")) else {}
SITE = (_cfg.get("siteUrl") or "https://example.com").rstrip("/")
if "--site" in sys.argv: SITE = sys.argv[sys.argv.index("--site") + 1].rstrip("/")
ONLY = sys.argv[sys.argv.index("--only") + 1] if "--only" in sys.argv else None
VERBOSE = "--verbose" in sys.argv
PHONES_OK = {re.sub(r"\D", "", _cfg.get("phoneTel") or _cfg.get("phone") or "")[-10:]}
EMAILS_OK = {(_cfg.get("email") or "").lower()}
BAD_OPEN = re.compile(r"^(in today'?s|in this (article|post|guide)|welcome to|we all know|have you ever|when it comes to|it'?s no secret that|in the ever-changing|in the fast-moving|as the industry evolves)", re.I)
BACKREF = re.compile(r"^(this|that|these|those|it|they|he|she|such|here|above|below|as (mentioned|noted|discussed)|as we saw)\b", re.I)
FIG = re.compile(r"(\$\s?\d[\d,]*(\.\d+)?|\b\d[\d,]*(\.\d+)?\s?(%|percent)|\b(19|20)\d\d\b|\b\d[\d,]*(\.\d+)?\b)")
QUESTION = re.compile(r"\?\s*$|^(how|what|which|why|when|where|who|is|are|can|do|does|should|will)\b", re.I)

def words(t): return re.findall(r"[A-Za-z0-9$][\w'’.$%,-]*", t)
def sentences(t):
    parts = [s for s in re.split(r"(?<=[.!?])\s+", t) if len(words(s)) >= 3]
    return parts

def audit(path, url):
    raw = open(path, encoding="utf-8").read()
    soup = BeautifulSoup(raw, "lxml")
    R = []  # (priority, check, status, note)
    def add(pri, name, ok, note="", opp=False):
        R.append((pri, name, "pass" if ok else ("opportunity" if opp else "FAIL"), note))
    head = soup.head
    robots = (head.find("meta", attrs={"name": "robots"}) or {}).get("content", "") if head else ""
    noindex = "noindex" in robots.lower()
    # schema
    lds, bad_ld = [], 0
    for s in soup.find_all("script", type="application/ld+json"):
        try:
            o = json.loads(s.string or "")
            lds.extend(o if isinstance(o, list) else [o])
        except Exception: bad_ld += 1
    types = set()
    def walk(o):
        if isinstance(o, dict):
            t = o.get("@type");
            if t: types.update(t if isinstance(t, list) else [t])
            for k in ("@graph",):
                for x in o.get(k, []): walk(x)
    for o in lds: walk(o)
    top_types = set()
    for o in lds:
        t = o.get("@type"); top_types.update(t if isinstance(t, list) else [t])
    up = url.split(SITE, 1)[-1]
    if re.search(r"/(blog|blogs|news|article)/.", up) or top_types & {"Article", "BlogPosting", "NewsArticle"}: ptype = "article"
    elif "/product/" in up or "Product" in top_types: ptype = "product"
    elif "/collection/" in up or "CollectionPage" in top_types: ptype = "collection"
    else: ptype = "page"
    target, failbelow = {"article": (1200, 720), "page": (700, 420), "product": (300, 180), "collection": (200, 120)}[ptype]
    expected = {"article": {"Article", "BlogPosting", "NewsArticle"}, "page": {"WebPage", "Article", "Service", "FAQPage"}, "product": {"Product"}, "collection": {"CollectionPage", "ItemList"}}[ptype]

    add(3, "indexable (no noindex)", not noindex, robots)
    add(3, "https", url.startswith("https://"))
    can = head.find("link", rel="canonical") if head else None
    can_h = can.get("href") if can else None
    add(3, "canonical self", can_h == url, str(can_h), opp=bool(can_h))
    title = (soup.title.string or "").strip() if soup.title else ""
    add(3, "title 30-60", 30 <= len(title) <= 60, "%d: %s" % (len(title), title), opp=bool(title))
    md = head.find("meta", attrs={"name": "description"}) if head else None
    mdc = md.get("content", "") if md else ""
    add(2, "meta description 70-160", 70 <= len(mdc) <= 160, "%d" % len(mdc), opp=bool(mdc))
    add(1, "og:title + og:image", bool(head.find("meta", property="og:title")) and bool(head.find("meta", property="og:image")))

    body = soup.body
    for t in body.find_all(["script", "style", "noscript", "template", "svg"]): t.decompose()
    h1s = body.find_all("h1")
    add(3, "exactly one H1", len(h1s) == 1, str(len(h1s)))
    text_all = body.get_text(" ", strip=True)
    wc = len(words(text_all))
    add(3, "text in HTML >=150 words", wc >= 150, str(wc))
    add(3, "word count %s target %d" % (ptype, target), wc >= target, str(wc), opp=wc >= failbelow)
    # headings / sections
    hs = body.find_all(re.compile(r"^h[1-6]$"))
    levels = [int(h.name[1]) for h in hs]
    skipped = [(levels[i - 1], levels[i], hs[i].get_text(" ", strip=True)[:40]) for i in range(1, len(levels)) if levels[i] > levels[i - 1] + 1]
    add(2, "no skipped heading levels", not skipped, str(skipped[:3]))
    h2s = body.find_all("h2")
    if wc > 300: add(2, ">=3 H2 sections", len(h2s) >= 3, str(len(h2s)))
    # section text: everything after a heading until next heading
    secs = []
    for h in hs:
        if h.name not in ("h2", "h3"): continue
        txt = []
        for el in h.next_elements:
            if getattr(el, "name", None) and re.match(r"^h[1-6]$", el.name): break
            if isinstance(el, str) and el.parent is not None and not re.match(r"^h[1-6]$", el.parent.name or ""):
                if el.strip(): txt.append(el.strip())
        secs.append((h.name, h.get_text(" ", strip=True), " ".join(txt)))
    h2secs = []
    # H2 sections include their H3 children
    cur = None
    for name, ht, tx in secs:
        if name == "h2": cur = [ht, tx]; h2secs.append(cur)
        elif cur: cur[1] += " " + ht + " " + tx
    lens = [(ht[:40], len(words(tx))) for ht, tx in h2secs]
    thin = [x for x in lens if x[1] < 40]; fat = [x for x in lens if x[1] > 400]
    ok_len = not fat and not (len(thin) > len(lens) / 2)
    add(2, "H2 sections 40-400 words", ok_len, "thin %d/%d fat %s" % (len(thin), len(lens), fat[:3]), opp=True)
    if len(hs) >= 2:
        qn = sum(1 for h in hs if QUESTION.search(h.get_text(" ", strip=True)))
        add(2, ">=2 question headings", qn >= 2, str(qn))
    h23 = body.find_all(["h2", "h3"])
    if h23: add(1, "ids on 70% H2/H3", sum(1 for h in h23 if h.get("id")) / len(h23) >= .7)
    # opening paragraph
    main = body.find("main") or body
    first_p = None
    for p in main.find_all("p"):
        t = p.get_text(" ", strip=True)
        if len(words(t)) >= 8: first_p = t; break
    fpw = len(words(first_p or ""))
    add(3, "opening paragraph 40-60 words", bool(first_p) and 40 <= fpw <= 60 and not BAD_OPEN.match(first_p or ""), "%d: %s" % (fpw, (first_p or "")[:90]), opp=bool(first_p) and fpw <= 90 and fpw >= 40 and not BAD_OPEN.match(first_p or ""))
    # sentences
    # sentences: block elements end a sentence too (card titles, prices and list items are not run-on prose)
    blocks = [b.strip() for b in body.get_text("\n", strip=True).split("\n") if b.strip()]
    ss = [x for blk in blocks if len(words(blk)) >= 3 for x in sentences(blk)]
    avg = sum(len(words(s)) for s in ss) / max(1, len(ss))
    add(1, "avg sentence < 26", avg < 26, "%.1f" % avg, opp=True)
    # schema
    add(3, "JSON-LD present & parses", bool(lds) and bad_ld == 0, "types=%s bad=%d" % (sorted(t for t in types if t), bad_ld))
    add(2, "schema type matches (%s)" % ptype, bool(top_types & expected), str(sorted(t for t in top_types if t)), opp=True)
    faq_vis = bool(body.find("details")) or any(re.search(r"\bFAQ|frequently asked|quick answers", h.get_text(), re.I) for h in hs)
    nq = 0
    for o in lds:
        if o.get("@type") == "FAQPage": nq += len(o.get("mainEntity", []))
    add(2, "FAQ section 6-10 Qs", faq_vis and nq >= 6, "visible=%s schemaQs=%d" % (faq_vis, nq))
    add(2, "FAQ mirrored in FAQPage", (not faq_vis) or nq > 0)
    add(1, "BreadcrumbList", "BreadcrumbList" in types)
    has_date = any(o.get("dateModified") for o in lds) or bool(re.search(r"updated", text_all, re.I) and body.find("time"))
    add(2, "date (dateModified/visible)", has_date)
    if ptype == "article":
        auth = None
        for o in lds:
            if o.get("@type") in ("Article", "BlogPosting", "NewsArticle"): auth = o.get("author")
        add(1, "named Person author", isinstance(auth, dict) and auth.get("@type") == "Person", str(auth))
    # links/images
    host = SITE.split("//")[1]
    links = [a.get("href", "") for a in body.find_all("a")]
    internal = [h for h in links if h.startswith("/") or host in h]
    add(2, ">=3 internal links", len(set(internal)) >= 3, str(len(set(internal))), opp=True)
    outbound = [h for h in links if h.startswith("http") and host not in h and "1examprep.com" not in h and not re.search(r"facebook|instagram|twitter|youtube|pinterest", h)]
    if wc > 300: add(1, "outbound citation", bool(outbound), str(outbound[:2]))
    imgs = soup.body.find_all("img")
    noalt = [i.get("src", "")[-40:] for i in imgs if i.get("alt") is None or (i.get("alt") == "" and "decor" not in " ".join(i.get("class", [])))]
    add(2, "alt text on every image", not noalt, "%d missing e.g. %s" % (len(noalt), noalt[:2]), opp=True)
    # AI readiness
    bad_secs = [(ht[:40], tx[:50]) for name, ht, tx in secs if tx and BACKREF.match(tx)]
    add(3, "sections stand alone", not bad_secs, str(bad_secs[:3]))
    if wc >= 200:
        figs = len(FIG.findall(text_all))
        add(2, "1 figure / 100 words", figs / wc * 100 >= 1, "%.2f" % (figs / wc * 100), opp=True)
    add(2, "list or table", bool(body.find(["ul", "ol", "table"])))
    # pre-publish blockers
    blk = []
    if re.search(r"\{\{[^}]+\}\}|\[(INSERT|YOUR|TODO)[^\]]*\]|\bTODO\b|\bFIXME\b|\bXXX\b|lorem ipsum|your business name|company name here", text_all, re.I): blk.append("placeholder")
    if re.search(r"(^|\s)(#{1,6} |\*\*[^*]+\*\*|\[[^\]]+\]\([^)]+\))", text_all): blk.append("markdown")
    rb = BeautifulSoup(raw, "lxml").body
    m2 = rb.find("main")
    if m2 and m2.find("script", type=lambda t: t != "application/ld+json"): blk.append("script in main")
    if re.search(r"\son(click|load|error|change|submit|mouseover)\s*=", str(rb), re.I): blk.append("inline handler")
    if rb.find("iframe"): blk.append("iframe")
    if any(h.strip().lower().startswith("javascript:") for h in links): blk.append("js url")
    dead = [h for h in links if h.strip() in ("", "#")]
    if dead: blk.append("dead link x%d" % len(dead))
    phones = set(re.sub(r"\D", "", p)[-10:] for p in re.findall(r"(?:\+?1[\s.-]?)?\(?\d{3}\)?[\s.-]\d{3}[\s.-]\d{4}", text_all + " ".join(links)))
    if phones - PHONES_OK: blk.append("phone %s" % (phones - PHONES_OK))
    emails = set(e.lower() for e in re.findall(r"[\w.+-]+@[\w-]+\.[\w.]+", text_all + " ".join(links)))
    if emails - EMAILS_OK: blk.append("email %s" % (emails - EMAILS_OK))
    if bad_ld: blk.append("schema parse")
    add(3, "pre-publish blockers", not blk, ", ".join(blk))
    return ptype, wc, R

pages = []
for d, subs, files in os.walk(ROOT):
    subs[:] = [s for s in subs if not s.startswith(".") and s not in ("store", "tools", "designs", "admin", "search", "shared", "content", "brand", "node_modules")]
    if "index.html" in files:
        rel = os.path.relpath(d, ROOT); rel = "" if rel == "." else rel + "/"
        if ONLY and ONLY not in rel: continue
        raw = open(os.path.join(d, "index.html"), encoding="utf-8").read(2000 * 50)
        if 'content="noindex' in raw and "/tag/" in "/" + rel: continue  # noindex tag pages: not in sitemap, not graded
        pages.append((os.path.join(d, "index.html"), SITE + "/" + rel))
agg = collections.defaultdict(lambda: collections.Counter()); examples = {}
bytype = collections.Counter()
for path, url in sorted(pages):
    ptype, wc, R = audit(path, url)
    bytype[ptype] += 1
    for pri, name, st, note in R:
        agg[(pri, name)][st] += 1
        if st != "pass": examples.setdefault((pri, name, st), []).append((url.replace(SITE, ""), note))
    if VERBOSE:
        print("\n==", url, ptype, wc)
        for pri, name, st, note in R:
            if st != "pass": print("  [%d] %-32s %-11s %s" % (pri, name, st, note[:150]))
print("pages:", len(pages), dict(bytype))
for (pri, name), c in sorted(agg.items(), key=lambda kv: (-kv[0][0], kv[0][1])):
    if c["FAIL"] or c["opportunity"]:
        print("[%d] %-34s pass %4d  opp %4d  FAIL %4d" % (pri, name, c["pass"], c["opportunity"], c["FAIL"]))
        for st in ("FAIL", "opportunity"):
            ex = examples.get((pri, name, st), [])
            for u, n in ex[:3]: print("       %s %s :: %s" % (st[:4], u, n[:140]))
