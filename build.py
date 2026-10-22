#!/usr/bin/env python3
"""Build the 1 Exam Prep product site.

  python3 build.py                 # DEFAULT: one real page per state/level/year/package (own URL, indexable)
  python3 build.py --site https://prep.1examprep.com   # same, plus sitemap.xml, robots.txt and canonical tags
  python3 build.py --spa           # optional lighter mode: index.html + 404.html only, JS reads the URL

Run it again whenever store/template.html or shared/catalog.js changes.
Previously generated folders are removed first either way.
"""
import json, os, re, sys, shutil, html

ROOT = os.path.dirname(os.path.abspath(__file__))
SITE = None
STATIC = "--spa" not in sys.argv
if "--site" in sys.argv:
    SITE = sys.argv[sys.argv.index("--site") + 1].rstrip("/") + "/"

tpl = open(os.path.join(ROOT, "store", "template.html"), encoding="utf-8").read()
ptpl = open(os.path.join(ROOT, "store", "product.html"), encoding="utf-8").read()
FULL = json.load(open(os.path.join(ROOT, "store", "products-full.json"), encoding="utf-8"))
cat_js = open(os.path.join(ROOT, "shared", "catalog.js"), encoding="utf-8").read()
CATALOG = json.loads(cat_js[cat_js.index("window.CATALOG=") + len("window.CATALOG="):cat_js.index(";\nwindow.CATALOG_STATES")])
STATES = json.loads(cat_js[cat_js.index("window.CATALOG_STATES=") + len("window.CATALOG_STATES="):].rstrip().rstrip(";"))
TIERS = ["book-fc", "nec", "nec-tabs", "calc", "super", "ultimate"]
GENERAL = "General (any state)"
CFG = json.load(open(os.path.join(ROOT, "site-config.json"), encoding="utf-8"))
if not SITE and CFG.get("siteUrl"): SITE = CFG["siteUrl"].rstrip("/") + "/"
BRAND = CFG.get("brand", "1 Exam Prep")
SITE_HOST = re.sub(r"^www\.", "", (SITE or "").split("//")[-1].strip("/"))
CART_TAG = ("?attributes%%5BSite%%5D=%s&ref=%s" % (SITE_HOST, SITE_HOST)) if SITE_HOST else ""  # tags the Shopify order with this site so the dashboard counts it here
def cart(vid): return "https://1examprep.com/cart/%s:1%s" % (vid, CART_TAG)
FUL = CFG.get("fulfillment") or {"name": "1 Exam Prep", "url": CFG.get("storeUrl", "https://1examprep.com"), "note": ""}
WM = CFG.get("wordmark") or [BRAND, "", ""]
WORDMARK_TEXT = "%s<span>%s</span>%s" % (html.escape(WM[0]), html.escape(WM[1]), html.escape(WM[2])) if WM[1] else html.escape(WM[0])
LOGO_NAV = CFG.get("logoNav") if CFG.get("logoNav") and os.path.exists(os.path.join(ROOT, CFG.get("logoNav"))) else None
HAS_PNG_ICONS = os.path.exists(os.path.join(ROOT, "shared", "favicon.png"))
def wordmark(rel):
    if LOGO_NAV: return '<img class="brand-img" src="%s%s" alt="%s" width="%d" height="48" decoding="async">' % (rel, LOGO_NAV, html.escape(BRAND), round(345 / 2))
    return WORDMARK_TEXT
WORDMARK = "{{WORDMARK_REL}}"  # resolved per page in brand_tokens (needs the page's relative prefix)
def brand_tokens(out, rel=None):
    """tokens every template may use; {{WORDMARK}} needs the page's root-relative prefix, taken from the stylesheet link if not given"""
    if rel is None:
        m = re.search(r'href="((?:\.\./)*)shared/base\.css"', out); rel = m.group(1) if m else ""
    return (out.replace("{{WORDMARK}}", wordmark(rel)).replace("{{WORDMARK_REL}}", wordmark(rel)).replace("{{BRAND}}", html.escape(BRAND)).replace("{{FULFILL_NAME}}", html.escape(FUL["name"])).replace("{{FULFILL_URL}}", html.escape(FUL["url"])))
import datetime
TODAY = datetime.date.today().isoformat()
LAUNCH = CFG.get("launched", "2026-10-16")
def nice_day(d):
    try: return datetime.date.fromisoformat(d[:10]).strftime("%B %-d, %Y")
    except Exception: return d
sys.path.insert(0, os.path.join(ROOT, "tools")); import blogkit
ALL_POSTS = blogkit.load_posts(os.path.join(ROOT, "content", "posts"), SITE or "")
POSTS = [q for q in ALL_POSTS if q.get("kind", "blog") != "page"]
PAGES = [q for q in ALL_POSTS if q.get("kind", "blog") == "page"]

def trim_desc(d, n=158):
    d = re.sub(r"\s+", " ", d).strip()
    if len(d) <= n: return d
    cut = d[:n].rsplit(" ", 1)[0].rstrip(",;:")
    return cut + ("" if cut.endswith(".") else ".")
def anchor_ids(out):
    out = brand_tokens(out)
    """give every h2/h3 without an id a stable, unique id made from its text (heading anchors for SEO tools and deep links)"""
    seen = set(re.findall(r'\sid="([^"]+)"', out))
    def rep2(m):
        tag, attrs, inner = m.group(1), m.group(2) or "", m.group(3)
        if re.search(r'\sid=', attrs): return m.group(0)
        base = re.sub(r"[^a-z0-9]+", "-", html.unescape(re.sub(r"<[^>]+>", "", inner)).lower()).strip("-")[:60] or "section"
        i, hid = 1, base
        while hid in seen: i += 1; hid = "%s-%d" % (base, i)
        seen.add(hid)
        return '<%s%s id="%s">%s</%s>' % (tag, attrs, hid, inner, tag)
    return re.sub(r"<(h[23])(\s[^>]*)?>(.*?)</\1>", rep2, out, flags=re.S)
def absurl(path):  # path like "texas/master/2026/" -> absolute when the site URL is known, else relative to root
    return (SITE + path) if SITE else "/" + path
def ld(obj): return '<script type="application/ld+json">%s</script>\n' % json.dumps(obj, ensure_ascii=False)
def org_ld():
    o = {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "legalName": CFG.get("legalName", BRAND), "url": SITE or CFG["storeUrl"],
         "logo": CFG.get("logo"), "telephone": CFG.get("phoneTel"), "email": CFG.get("email"),
         "sameAs": [v for v in CFG.get("social", {}).values() if v],
         "parentOrganization": {"@type": "Organization", "name": FUL["name"], "url": FUL["url"]} if FUL["name"] != BRAND else None,
         "contactPoint": [{"@type": "ContactPoint", "telephone": CFG.get("phoneTel"), "contactType": "sales", "areaServed": "US", "availableLanguage": "English"}]}
    return {k: v for k, v in o.items() if v}
def publisher_ld():
    o = {"@type": "Organization", "name": BRAND, "url": SITE or CFG["storeUrl"], "logo": {"@type": "ImageObject", "url": CFG.get("logo")} if CFG.get("logo") else None,
         "telephone": CFG.get("phoneTel"), "email": CFG.get("email"), "parentOrganization": {"@type": "Organization", "name": FUL["name"], "url": FUL["url"]} if FUL["name"] != BRAND else None}
    return {k: v for k, v in o.items() if v}
def website_ld():
    w = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND, "url": SITE or "/",
         "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": absurl("search/?q={search_term_string}")}, "query-input": "required name=search_term_string"}}
    return w
def crumbs_ld(items):  # [(name, path)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absurl(pth)} for i, (n, pth) in enumerate(items)]}
def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
BLOG_FAQ = [("How long should I study for the journeyman or master electrician exam?", "Most candidates do well with six to eight weeks at about ninety minutes a day, as long as the time is split between three things: getting fast in the code book, working calculations until they are automatic, and sitting full-length timed practice exams in the last two weeks. People who only read the study guide tend to know the material and still run out of time, because the exam is a test of finding answers in the code under a clock as much as a test of knowledge."),
            ("Is the exam open book, and which code book do I bring?", "Nearly every state exam is open book for the code portion, and the book you bring has to be the edition named in your state's candidate bulletin. States adopt new editions at different times, so check the bulletin rather than assuming the newest code applies. Most boards allow permanent tabs and highlighting but not loose notes; the bulletin lists what is permitted."),
            ("What is the difference between the journeyman and master exam?", "The journeyman exam concentrates on the code a working electrician uses every day: branch circuits, feeders, grounding and bonding, wiring methods, box and conduit fill, motors and appliances. The master exam covers the same ground and adds services, load calculations, transformers, planning and supervision, and the parts of the code a contractor is responsible for. The study guides, calculations guides and flash cards are written separately for each level."),
            ("Are the practice questions the real exam questions?", "No. Licensing exam questions are confidential and are not published by any testing vendor. Practice questions are original material written to the same subjects, format and difficulty, with explanations that point you to the code section, so you learn where answers live rather than memorising answers."),
            ("Does buying a package register me for the exam?", "No. Applications, experience hours, approval to test and scheduling are handled by your state licensing board and its testing vendor, usually PSI, Prometric or Pearson VUE depending on the state. A package gets you ready for the test itself. The state posts on this blog explain who runs the process in each state and link to the board's own pages."),
            ("How do the packages arrive?", "Printed study guides, calculations guides, flash cards and code books ship from our fulfillment center, %s. Online test success kits and courses are delivered by email after purchase, so you can start the timed practice exams on a phone or laptop the same day the books are on their way.")]
LISTING_FAQ = [("Which NEC edition are these based on?", "Every product in this collection is built on the %s National Electrical Code. If your state is still testing on the 2023 or 2020 NEC, check your candidate bulletin first; our fulfillment center, {F}, also carries earlier editions.".replace("{F}", FUL["name"])),
               ("Are these the actual exam questions?", "No. Real exam questions are confidential. These are practice questions written to the same subjects, format and difficulty, with explanations."),
               ("What's the difference between Journeyman and Master?", "Journeyman guides cover the journeyman-level exam; Master guides go deeper on calculations, planning and supervision topics for the master or contractor exam. Pick the license you are applying for."),
               ("When will I get it?", "Online test success kits and courses are delivered by email after purchase. Books and code books ship from our fulfillment center, {F}; shipping options are shown at checkout.".replace("{F}", FUL["name"])),
               ("Does buying make me eligible to test?", "No. Eligibility, experience hours and exam approval come from your state licensing board. These materials get you ready for the test itself.")]
PRODUCT_FAQ = [("Which NEC edition is this based on?", "The %s National Electrical Code. If your state is still testing on an earlier edition, check your candidate bulletin first; our fulfillment center, {F}, also carries earlier editions.".replace("{F}", FUL["name"])),
               ("Are these the actual exam questions?", "No. Real exam questions are confidential. These are practice questions written to the same subjects, format and difficulty, with explanations."),
               ("When will I get it?", "Online kits and courses are delivered by email after purchase. Books and code books ship from our fulfillment center, {F}; shipping options are shown at checkout.".replace("{F}", FUL["name"])),
               ("Does buying make me eligible to test?", "No. Eligibility, experience hours and exam approval come from your state licensing board. This package gets you ready for the test itself.")]

def head_extra(path, title, desc, image, rel, noindex=False, extra_ld=()):
    desc = trim_desc(desc)
    url = absurl(path) if SITE else None
    h = ['<meta name="robots" content="%s">' % ("noindex, nofollow" if noindex else "index, follow, max-image-preview:large")]
    if url: h.append('<meta property="og:url" content="%s">' % html.escape(url))
    if url and not noindex: h.append('<link rel="alternate" type="text/markdown" title="Markdown version for AI assistants" href="%s">' % html.escape(url + "index.md"))
    h.append('<meta property="og:site_name" content="%s">' % html.escape(BRAND)); h.append('<meta property="og:locale" content="en_US">')
    h.append('<meta name="twitter:card" content="summary_large_image">'); h.append('<meta name="twitter:title" content="%s">' % html.escape(title)); h.append('<meta name="twitter:description" content="%s">' % html.escape(desc))
    if image: h.append('<meta name="twitter:image" content="%s">' % html.escape(image))
    if CFG.get("social", {}).get("twitter"): h.append('<meta name="twitter:site" content="@%s">' % CFG["social"]["twitter"].rstrip("/").split("/")[-1])
    h.append('<meta name="theme-color" content="#1b1f3b">')
    h.append('<script>window.SITE=%s;</script>' % json.dumps({"brand": BRAND, "storeUrl": CFG["storeUrl"], "fulfillment": FUL["name"], "cartTag": CART_TAG, "aiFinder": CFG.get("aiFinderUrl", "")}))
    if len(BRAND) > 16 and not LOGO_NAV: h.append('<style>.nav .brand{font-size:%s;line-height:1.05;max-width:46vw}@media (max-width:720px){.nav .brand{font-size:.95rem}}</style>' % ("1.05rem" if len(BRAND) > 24 else "1.2rem"))
    if HAS_PNG_ICONS: h.append('<link rel="icon" href="%sshared/favicon.png" type="image/png" sizes="64x64">' % rel)
    else: h.append('<link rel="icon" href="%sshared/favicon.svg" type="image/svg+xml">' % rel)
    h.append('<link rel="apple-touch-icon" href="%sshared/apple-touch-icon.png">' % rel); h.append('<link rel="manifest" href="%smanifest.webmanifest">' % rel)
    if CFG.get("googleSiteVerification"): h.append('<meta name="google-site-verification" content="%s">' % html.escape(CFG["googleSiteVerification"]))
    if CFG.get("gtagId"): h.append('<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","%s",{"send_page_view":true});</script>' % (CFG["gtagId"], CFG["gtagId"]))
    if CFG.get("gtmId"): h.append("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','%s');</script>" % CFG["gtmId"])
    if CFG.get("metaPixelId"): h.append("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','%s');fbq('track','PageView');</script>" % CFG["metaPixelId"])
    if CFG.get("dashboardUrl") and CFG.get("siteKey"): h.append('<script>window.__dashCustom=true;</script><script src="%s/t.js" data-site="%s" defer></script>' % (html.escape(CFG["dashboardUrl"].rstrip("/")), html.escape(CFG["siteKey"])))
    for o in extra_ld: h.append(ld(o).rstrip())
    if url and not noindex:
        h.append(ld({"@context": "https://schema.org", "@type": "WebPage", "@id": url, "url": url, "name": title, "description": desc, "inLanguage": "en-US", "datePublished": LAUNCH, "dateModified": TODAY,
                     "isPartOf": {"@type": "WebSite", "url": SITE, "name": BRAND}, "publisher": publisher_ld(), "about": {"@type": "Thing", "name": "Journeyman and master electrician licensing exams"},
                     "encoding": {"@type": "MediaObject", "encodingFormat": "text/markdown", "contentUrl": url + "index.md"}}).rstrip())
    return "\n".join(h) + "\n"

ICON_PHONE = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"><path d="M22 16.9v3a2 2 0 0 1-2.2 2 19.8 19.8 0 0 1-8.6-3.1 19.5 19.5 0 0 1-6-6A19.8 19.8 0 0 1 2.1 4.2 2 2 0 0 1 4.1 2h3a2 2 0 0 1 2 1.7c.1.9.4 1.8.7 2.7a2 2 0 0 1-.5 2.1L8 9.8a16 16 0 0 0 6 6l1.3-1.3a2 2 0 0 1 2.1-.4c.9.3 1.8.6 2.7.7a2 2 0 0 1 1.7 2z"/></svg>'
ICON_SEARCH = '<svg viewBox="0 0 24 24" fill="none" stroke="currentColor" stroke-width="2.2" stroke-linecap="round" aria-hidden="true"><circle cx="11" cy="11" r="7"/><path d="m20 20-3.5-3.5"/></svg>'
def nav_tools(cta_html):
    return ('<div class="nav-tools"><a class="nav-phone" href="tel:%s" aria-label="Call %s">%s<span>%s</span></a>'
            '<button type="button" class="nav-search" data-sopen aria-label="Search the site">%s</button>%s</div>' % (CFG["phoneTel"], CFG["phone"], ICON_PHONE, html.escape(CFG["phone"]), ICON_SEARCH, cta_html))
def footer(rel, year0):
    soc = "".join('<li><a href="%s" rel="noopener" target="_blank">%s</a></li>' % (html.escape(u), k.capitalize()) for k, u in CFG.get("social", {}).items() if u)
    quick = "".join('<li><a href="%s%s/journeyman/%s/">%s</a></li>' % (rel, slug(x), year0, x) for x in ["Texas", "Florida", "California", "New York", "Georgia", "North Carolina"])
    return ('<footer class="site-footer"><div class="wrap"><div class="cols">'
            '<div><a class="brand" href="%s">%s</a><p>%s</p><p class="contact"><a href="tel:%s">%s</a><a href="mailto:%s">%s</a></p></div>'
            '<nav aria-label="Popular states"><h2>Popular states</h2><ul>%s<li><a href="%s">All 50 states</a></li></ul></nav>'
            '<nav aria-label="Shop"><h2>Shop</h2><ul><li><a href="%s#packs">Packages</a></li><li><a href="%s#compare">Compare packages</a></li><li><a href="%s#singles">Study guides &amp; flash cards</a></li><li><a href="%sfaq/">FAQ</a></li><li><a href="%sblog/">Blog</a></li><li><a href="%ssearch/">Search</a></li></ul></nav>'
            '<nav aria-label="Follow"><h2>Follow</h2><ul>%s</ul></nav></div>'
            '<p class="fine"><strong>%s</strong> &copy; <span data-year>%s</span> &middot; %s Prices and availability come from the fulfillment store and were last checked <time datetime="%s">%s</time>; the price at checkout is the one that applies. Not affiliated with any state licensing board or testing vendor. Purchasing does not grant exam eligibility or a license.</p></div></footer>'
            % (rel or "./", "{{WORDMARK}}", html.escape(CFG.get("tagline", "")), CFG["phoneTel"], html.escape(CFG["phone"]), CFG["email"], CFG["email"], quick, rel or "./", rel or "./", rel or "./", rel or "./", rel, rel, rel, soc, html.escape(BRAND), TODAY[:4], html.escape(FUL.get("note") or ("Orders are processed and shipped by %s, our fulfillment center." % FUL["name"])), TODAY, nice_day(TODAY)))

def slug(state): return "general" if state == GENERAL else state.lower().replace(" ", "-")
def words(text):
    out = []
    for i, w in enumerate(text.split()):
        hl = w.startswith("*"); w = w.lstrip("*")
        out.append('<span class="w%s" style="--n:%d">%s</span>' % (" hl" if hl else "", i, html.escape(w)))
    return " ".join(out)

FEATURED = "ultimate"
def products_for(state, level, year):
    st = None if state == GENERAL else state
    prods = sorted([p for p in CATALOG if p["state"] == st and p["level"] == level and p["year"] == year and p["tier"] in TIERS], key=lambda p: (p["rank"], p["id"]))
    seen, out = set(), []
    for p in prods:
        if p["tier"] in seen: continue
        seen.add(p["tier"]); out.append(p)
    return out
def card_html(p, href):
    c, n = float(p.get("compareAt") or 0), float(p["price"]); feat = p["tier"] == FEATURED
    save = ('<s class="pc-was">%s</s><span class="pc-save">Save %d%%</span>' % (money(c), round((c - n) / c * 100))) if c > n else ""
    return ('<article class="pc%s" data-id="%s">%s<div class="pc-img"><img src="%s" alt="%s" loading="lazy"></div><div class="pc-body">'
            '<span class="pc-tier">%s</span><h3 class="pc-name">%s</h3><p class="pc-sub">%s</p><p class="pc-desc">%s</p>'
            '<div class="pc-price"><span class="pc-now">%s</span>%s</div>'
            '<div class="pc-actions"><a class="btn btn-buy" href="%s" rel="noopener">Buy now</a><a class="btn btn-details" href="%s" data-details="%s" data-tier="%s">What\u2019s inside</a></div></div></article>'
            % (" pc--featured" if feat else "", p["id"], '<span class="pc-badge">Most complete</span>' if feat else "", html.escape(p["image"]), html.escape(clean_title(p["title"])),
               html.escape("%s · %s · %s" % (p["state"] or "Any state", p["level"], p["year"])), html.escape(p["tierName"]), html.escape(clean_title(p["title"])), html.escape(" ".join(p["desc"].replace(p["title"], "").strip().split()[:22]) + "…"),
               money(n), save, cart(p["variants"][0]["id"]), href, p["id"], p["tierSlug"]))
def singles_html():
    singles = sorted([p for p in CATALOG if not p["state"] and p["rank"] == 0], key=lambda p: float(p["price"]))
    return "".join('<article class="sg" data-id="%s"><div class="pc-img"><img src="%s" alt="%s" loading="lazy"></div><div class="pc-body"><span class="pc-tier">%s</span><h3 class="pc-name">%s</h3><div class="pc-price"><span class="pc-now">%s</span>%s</div>'
                   '<div class="pc-actions"><a class="btn btn-buy" href="%s" rel="noopener">Buy now</a><button class="btn btn-details" type="button" data-details="%s">What\u2019s inside</button></div></div></article>'
                   % (p["id"], html.escape(p["image"]), html.escape(clean_title(p["title"])), "All levels" if p["level"] == "General" else p["level"], html.escape(clean_title(p["title"])), money(p["price"]),
                      ('<small style="color:var(--muted)"> to %s</small>' % money(p["maxPrice"])) if p.get("maxPrice") and p["maxPrice"] != p["price"] else "", cart(p["variants"][0]["id"]), p["id"]) for p in singles)
def states_html(rel, year, level_first="journeyman"):
    items = []
    for st in STATES + [GENERAL]:
        sl = slug(st); name = "Any state (general)" if st == GENERAL else st
        links = "".join('<a href="%s%s/%s/%s/">%s</a>' % (rel, sl, lv, year, lv.capitalize()) for lv in ((level_first, "master" if level_first == "journeyman" else "journeyman")) if os.path.isdir(os.path.join(ROOT, sl, lv, year)) or True)
        items.append("<li><b>%s</b><span>%s</span></li>" % (html.escape(name), links))
    return '<ul class="states-grid">%s</ul>' % "".join(items)
NEIGHBORS = {"Alabama": ["Florida", "Georgia", "Mississippi", "Tennessee"], "Alaska": ["Washington", "Oregon", "Hawaii"], "Arizona": ["California", "Nevada", "Utah", "New Mexico", "Colorado"], "Arkansas": ["Missouri", "Tennessee", "Mississippi", "Louisiana", "Texas", "Oklahoma"],
    "California": ["Oregon", "Nevada", "Arizona"], "Colorado": ["Wyoming", "Nebraska", "Kansas", "Oklahoma", "New Mexico", "Utah"], "Connecticut": ["New York", "Massachusetts", "Rhode Island"], "Delaware": ["Maryland", "Pennsylvania", "New Jersey"],
    "Florida": ["Georgia", "Alabama"], "Georgia": ["Florida", "Alabama", "Tennessee", "North Carolina", "South Carolina"], "Hawaii": ["California", "Alaska", "Washington"], "Idaho": ["Washington", "Oregon", "Nevada", "Utah", "Wyoming", "Montana"],
    "Illinois": ["Wisconsin", "Iowa", "Missouri", "Kentucky", "Indiana"], "Indiana": ["Michigan", "Ohio", "Kentucky", "Illinois"], "Iowa": ["Minnesota", "Wisconsin", "Illinois", "Missouri", "Nebraska", "South Dakota"], "Kansas": ["Nebraska", "Missouri", "Oklahoma", "Colorado"],
    "Kentucky": ["Indiana", "Ohio", "West Virginia", "Virginia", "Tennessee", "Missouri", "Illinois"], "Louisiana": ["Texas", "Arkansas", "Mississippi"], "Maine": ["New Hampshire", "Massachusetts", "Vermont"], "Maryland": ["Virginia", "West Virginia", "Pennsylvania", "Delaware"],
    "Massachusetts": ["Rhode Island", "Connecticut", "New York", "New Hampshire", "Vermont"], "Michigan": ["Ohio", "Indiana", "Wisconsin"], "Minnesota": ["North Dakota", "South Dakota", "Iowa", "Wisconsin"], "Mississippi": ["Louisiana", "Arkansas", "Tennessee", "Alabama"],
    "Missouri": ["Iowa", "Illinois", "Kentucky", "Tennessee", "Arkansas", "Oklahoma", "Kansas", "Nebraska"], "Montana": ["North Dakota", "South Dakota", "Wyoming", "Idaho"], "Nebraska": ["South Dakota", "Iowa", "Missouri", "Kansas", "Colorado", "Wyoming"], "Nevada": ["California", "Oregon", "Idaho", "Utah", "Arizona"],
    "New Hampshire": ["Maine", "Massachusetts", "Vermont"], "New Jersey": ["New York", "Pennsylvania", "Delaware"], "New Mexico": ["Arizona", "Utah", "Colorado", "Oklahoma", "Texas"], "New York": ["New Jersey", "Pennsylvania", "Connecticut", "Massachusetts", "Vermont"],
    "North Carolina": ["Virginia", "Tennessee", "Georgia", "South Carolina"], "North Dakota": ["Minnesota", "South Dakota", "Montana"], "Ohio": ["Michigan", "Pennsylvania", "West Virginia", "Kentucky", "Indiana"], "Oklahoma": ["Kansas", "Missouri", "Arkansas", "Texas", "New Mexico", "Colorado"],
    "Oregon": ["Washington", "Idaho", "Nevada", "California"], "Pennsylvania": ["New York", "New Jersey", "Delaware", "Maryland", "West Virginia", "Ohio"], "Rhode Island": ["Connecticut", "Massachusetts"], "South Carolina": ["North Carolina", "Georgia"],
    "South Dakota": ["North Dakota", "Minnesota", "Iowa", "Nebraska", "Wyoming", "Montana"], "Tennessee": ["Kentucky", "Virginia", "North Carolina", "Georgia", "Alabama", "Mississippi", "Arkansas", "Missouri"], "Texas": ["New Mexico", "Oklahoma", "Arkansas", "Louisiana"],
    "Utah": ["Idaho", "Wyoming", "Colorado", "New Mexico", "Arizona", "Nevada"], "Vermont": ["New York", "New Hampshire", "Massachusetts"], "Virginia": ["Maryland", "West Virginia", "Kentucky", "Tennessee", "North Carolina"], "Washington": ["Oregon", "Idaho"],
    "West Virginia": ["Pennsylvania", "Maryland", "Virginia", "Kentucky", "Ohio"], "Wisconsin": ["Michigan", "Minnesota", "Iowa", "Illinois"], "Wyoming": ["Montana", "South Dakota", "Nebraska", "Colorado", "Utah", "Idaho"]}
def state_posts(state, level, n=3):
    out = [q for q in POSTS if (state and q.get("state") == state)] + [q for q in POSTS if (not state or q.get("state") != state) and (q.get("level", "").lower() == level.lower() or level.lower() in [t.lower() for t in q["tags"]])]
    seen, res = set(), []
    for q in out:
        if q["slug"] in seen: continue
        seen.add(q["slug"]); res.append(q)
    return res[:n]
def related_pages_html(rel, state, level, year, tier_slug=None, tier_name=""):
    """Related pages block for a state page (tier_slug None) or a product page (links to the same package elsewhere)."""
    other = "Master" if level == "Journeyman" else "Journeyman"; st = None if state == GENERAL else state
    def L(stt, lv, label=None):
        path = "%s%s/%s/%s/%s" % (rel, slug(stt), lv.lower(), year, (tier_slug + "/") if tier_slug and os.path.isdir(os.path.join(ROOT, slug(stt), lv.lower(), year, tier_slug)) else "")
        return '<li><a href="%s">%s</a></li>' % (path, html.escape(label or ("%s %s %s" % ("Any state" if stt == GENERAL else stt, lv.lower(), tier_name if (tier_slug and path.endswith(tier_slug + "/")) else "packages"))))
    cols = []
    same = [L(state, other, "%s %s %s" % ("Any state" if not st else state, other.lower(), (tier_name + " edition") if tier_slug else "packages"))]
    if st: same.append(L(GENERAL, level, "Any-state %s %s" % (level.lower(), tier_name if tier_slug else "packages")))
    else: same += [L(x, level) for x in ("Texas", "Florida", "California")]
    cols.append(("Same exam, other options", same))
    if st and NEIGHBORS.get(st): cols.append(("Nearby states, %s" % level.lower(), [L(x, level) for x in NEIGHBORS[st][:5]]))
    posts = state_posts(st, level)
    if posts: cols.append(("From the blog", ['<li><a href="%sblog/%s/">%s</a></li>' % (rel, q["slug"], html.escape(q["title"])) for q in posts]))
    cols.append(("Also on this site", ['<li><a href="%sblog/">All blog posts</a></li>' % rel, '<li><a href="%s#states">Every state and level</a></li>' % (rel or "./"), '<li><a href="%s#compare">Compare the five packages</a></li>' % (rel or "./")]))
    inner = "".join("<div><h3>%s</h3><ul>%s</ul></div>" % (html.escape(h), "".join(items)) for h, items in cols)
    return inner
def takeaways_html(items):
    items = [i for i in items if i][:4]
    if not items: return ""
    return ('<aside class="takeaways" aria-labelledby="key-takeaways"><h2 id="key-takeaways">Key takeaways</h2><ul>%s</ul><p class="upd">Updated <time datetime="%s">%s</time> \u00b7 prices checked against the %s store</p></aside>'
            % ("".join("<li>%s</li>" % html.escape(i) for i in items), TODAY, nice_day(TODAY), html.escape(FUL["name"])))
def listing_takeaways(state, level, year, prods):
    if not prods: return ""
    name = "any state" if state == GENERAL else state
    lo, hi = min(float(p["price"]) for p in prods), max(float(p["price"]) for p in prods)
    ult = next((p for p in prods if p["tier"] == "ultimate"), prods[-1]); c = float(ult.get("compareAt") or 0)
    items = ["%d %s electrician exam prep packages for %s, from %s to %s, all built on the %s National Electrical Code." % (len(prods), level.lower(), name, money(lo), money(hi), year),
             ("Every package includes the %s %s %s study guide with 12 practice exams and 2 full-length final exams." % (year, "" if state == GENERAL else state, level)).replace("  ", " "),
             ("The %s at %s is the most complete option%s." % (ult["tierName"], money(ult["price"]), (", %d%% below the %s price of its parts" % (round((c - float(ult["price"])) / c * 100), money(c))) if c > float(ult["price"]) else "")),
             "Buy now goes straight to secure checkout; books ship from our fulfillment center, %s, and online kits arrive by email." % FUL["name"]]
    return takeaways_html(items)
def page(path_parts, route, title, desc, h1, lead, og_image=None, extra_ld=(), crumbs=None, noindex=False):
    depth = len(path_parts)
    rel = "../" * depth
    url = (SITE + "/".join(path_parts) + ("/" if path_parts else "")) if SITE else None
    assets_head = '<link rel="stylesheet" href="%sshared/base.css">\n<link rel="stylesheet" href="%sshared/store.css">' % (rel, rel)
    assets_cat = '<script src="%sshared/catalog.js"></script>' % rel
    assets_app = '<script src="%sshared/store.js"></script>' % rel
    if route.get("spa"):
        boot = ("<script>window.__B=(function(){var S=%s;var parts=location.pathname.split('/').filter(Boolean);var i=-1;"
                "for(var k=0;k<parts.length;k++){if(S.indexOf(parts[k].toLowerCase())>-1){i=k;break;}}"
                "if(i<0)return location.pathname.replace(/[^\\/]*$/,'');var b='/'+parts.slice(0,i).join('/');return b==='/'?b:b+'/';})();"
                "document.write('<link rel=\"stylesheet\" href=\"'+__B+'shared/base.css\"><link rel=\"stylesheet\" href=\"'+__B+'shared/store.css\">');</script>") % json.dumps(sorted(slug(x) for x in STATES + [GENERAL]))
        assets_head = boot
        assets_cat = "<script>document.write('<script src=\"'+__B+'shared/catalog.js\"><\\/script>');</script>"
    path = "/".join(path_parts) + ("/" if path_parts else "")
    lds = list(extra_ld)
    qa_html = ""
    if route.get("state") and route.get("level"):
        _st = next((x for x in STATES + [GENERAL] if slug(x) == route["state"]), None); _lv = route["level"]; _yr = route.get("year")
        _ps = products_for(_st, _lv, _yr) if _st else []
        if _ps:
            _nm = "any state" if _st == GENERAL else _st; _lo, _hi = min(float(p["price"]) for p in _ps), max(float(p["price"]) for p in _ps)
            _ult = next((p for p in _ps if p["tier"] == "ultimate"), None)
            qa = [("How much does %s %s electrician exam prep cost?" % (_nm, _lv.lower()), "%s %s electrician exam prep runs from %s to %s: %s." % (_nm.capitalize() if _st == GENERAL else _st, _lv.lower(), money(_lo), money(_hi), "; ".join("%s %s" % (p["tierName"], money(p["price"])) for p in _ps))),
                  ("Which %s %s exam prep package should I choose?" % (_nm, _lv.lower()), "Pick by how much help you want. The %s at %s is the lightest option%s. Every package includes the %s %s study guide with 12 practice exams and 2 full-length final exams." % (_ps[0]["tierName"], money(_ps[0]["price"]), (", and the %s at %s is the most complete, adding the NEC with tabs, flash cards and the online test success kit" % (_ult["tierName"], money(_ult["price"]))) if _ult else "", _yr, _lv.lower())),
                  ("Which NEC edition are these %s %s packages built on?" % (_nm, _lv.lower()), "The %s National Electrical Code. If your state still tests on an earlier edition, check the candidate bulletin first; %s also carries earlier editions." % (_yr, FUL["name"]))]
            qa_html = '<aside class="takeaways qa" aria-labelledby="quick-answers"><h2 id="quick-answers">Quick answers</h2>%s</aside>' % "".join('<div class="qa-item"><h3>%s</h3><p>%s</p></div>' % (html.escape(q), html.escape(a)) for q, a in qa)
            for o in lds:
                if o.get("@type") == "FAQPage": o["mainEntity"] = faq_ld(qa)["mainEntity"] + o["mainEntity"]; break
            else: lds.append(faq_ld(qa))
    if crumbs: lds.append(crumbs_ld(crumbs))
    sel_state = next((st for st in STATES + [GENERAL] if slug(st) == route.get("state")), None) or "Texas"
    sel_level = route.get("level") or "Journeyman"; sel_year = route.get("year") or sorted({p["year"] for p in CATALOG}, reverse=True)[0]
    prods = products_for(sel_state, sel_level, sel_year)
    pbase = "" if route.get("state") else "%s/%s/%s/" % (slug(sel_state), sel_level.lower(), sel_year)
    rail_html = "".join(card_html(q, pbase + q["tierSlug"] + "/") for q in prods)  # on a state page the packages sit one level below it; on the home page pbase holds the full path
    sel_path = (rel if route.get("state") else pbase) if route.get("state") else pbase
    crumb_html = '<a href="%s">All states</a><span>/</span><a href="%s">%s</a><span>/</span><a href="%s">%s</a><span>/</span><a href="%s">%s</a>' % (rel or "./", sel_path or "./", html.escape(sel_state), sel_path or "./", sel_level, sel_path or "./", sel_year)
    marq = "".join('<span><a href="%s%s/journeyman/%s/" style="color:inherit;text-decoration:none">%s</a></span>' % (rel, slug(st), sel_year, html.escape(st)) for st in STATES)
    tk = listing_takeaways(sel_state, sel_level, sel_year, prods) if route.get("state") else takeaways_html([
        "Journeyman and master electrician exam prep for all 50 states plus a general edition, built on the %s National Electrical Code." % sel_year,
        "5 package levels per state and level, from the study guide with flash cards at %s to the Ultimate Combo at %s." % (money(min(float(p["price"]) for p in CATALOG if p["tier"] in TIERS)), money(max(float(p["price"]) for p in CATALOG if p["tier"] in TIERS))),
        "Every package includes the state study guide with 12 practice exams and 2 full-length final exams.",
        "Pick a state and level, press Buy now, and checkout opens at our fulfillment center, %s." % FUL["name"]])
    out = (tpl.replace("{{TAKEAWAYS_HTML}}", qa_html + tk).replace("{{RAIL_HTML}}", rail_html).replace("{{SINGLES_HTML}}", singles_html()).replace("{{SEL_TITLE}}", html.escape("%s · %s · %s" % (sel_state, sel_level, sel_year)))
           .replace("{{CRUMB_HTML}}", crumb_html).replace("{{MARQ_HTML}}", marq + marq).replace("{{STATES_HTML}}", states_html(rel, sel_year, sel_level.lower())).replace("{{YEAR}}", sel_year)
           .replace("{{GUIDE_FOR}}", (" for the %s %s exam" % (sel_state, sel_level.lower())) if route.get("state") and sel_state != GENERAL else "")
           .replace("{{RELATED_HTML}}", '<section class="related-pages" aria-labelledby="h-related-pages"><div class="wrap"><h2 id="h-related-pages">Related pages</h2><div class="rp-cols">%s</div></div></section>' % related_pages_html(rel, sel_state, sel_level, sel_year))
           .replace("{{LINK_J}}", '<a href="%s%s/journeyman/%s/">journeyman exam</a>' % (rel, slug(sel_state), sel_year)).replace("{{LINK_M}}", '<a href="%s%s/master/%s/">master exam</a>' % (rel, slug(sel_state), sel_year))
           .replace("{{ASSETS_HEAD}}", assets_head).replace("{{ASSETS_CATALOG}}", assets_cat).replace("{{ASSETS_APP}}", assets_app)
           .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel))
           .replace("{{HEAD_EXTRA}}", head_extra(path, title, desc, og_image, rel, noindex, lds))
           .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="#packs">Pick my package</a>'))
           .replace("{{FOOTER}}", footer(rel, sorted({p["year"] for p in CATALOG}, reverse=True)[0]))
           .replace("{{TITLE}}", html.escape(title)).replace("{{DESC}}", html.escape(trim_desc(desc)))
           .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % url) if url else "")
           .replace("{{OGIMAGE}}", ('<meta property="og:image" content="%s">\n' % html.escape(og_image)) if og_image else "")
           .replace("{{REL}}", rel).replace("{{HOME}}", rel if rel else "./")
           .replace("{{H1_TEXT}}", html.escape(h1.replace("*", ""))).replace("{{H1_HTML}}", words(h1))
           .replace("{{LEAD}}", html.escape(lead)).replace("{{ROUTE}}", json.dumps(route)))
    d = os.path.join(ROOT, *path_parts) if path_parts else ROOT
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f: f.write(anchor_ids(out))
    return url

INCLUDED = {
    "book-fc":  ["{Y} {S} {L} Electrician Exam Prep and Study Guide: 12 practice exams + 2 full final exams", "{Y} {L} Electrician Exam Flash Cards"],
    "nec":      ["{Y} {S} {L} Electrician Study Guide", "National Electrical Code {Y} paperback"],
    "nec-tabs": ["{Y} {S} {L} Electrician Study Guide", "National Electrical Code {Y} paperback", "Pre-printed NEC tabs"],
    "calc":     ["{Y} {S} {L} Electrician Study Guide", "{Y} Electrician Calculations Study Guide", "National Electrical Code {Y} paperback"],
    "super":    ["{Y} {S} {L} Electrician Study Guide", "{Y} Electrician Calculations Study Guide", "{Y} {L} Electrician Exam Flash Cards", "National Electrical Code {Y} paperback", "Pre-printed NEC tabs"],
    "ultimate": ["{Y} {S} {L} Electrician Study Guide", "{Y} Electrician Calculations Study Guide", "National Electrical Code {Y} paperback with tabs", "{Y} {L} Electrician Exam Flash Cards", "{Y} {L} Electrician Exam Questions and Study Guide: Online Test Success Kit"],
}
def money(v): return "$%.2f" % float(v)
def clean_title(t): return re.sub(r"\s*\(Based on the \d{4} NEC\)\s*", "", t).replace(": Trusted by 50k Electricians", "")

def product_page(path_parts, p, siblings, state_name, level_url, other_level_url, other_level):
    depth = len(path_parts); rel = "../" * depth
    url = (SITE + "/".join(path_parts) + "/") if SITE else None
    full = FULL.get(p["id"], {"html": "", "images": [p["image"]]})
    if FUL["name"] != BRAND and full.get("html"):  # store descriptions talk about the fulfillment brand; this site speaks as itself
        full = dict(full, html=re.sub(r"(?<![\w/.-])1 ?Exam ?Prep(?![\w.-])", BRAND, full["html"]))
    desc_faq = []
    if full.get("html"):  # store descriptions use h3 for their sections; on this page they are the main sections, so h2. Their FAQ block keeps h3 questions.
        hx = full["html"]; m = re.search(r"<h3>\s*(FAQ[^<]*|Frequently Asked Questions[^<]*)</h3>", hx, re.I)
        if m:
            head, tail = hx[:m.start()], hx[m.end():]
            for qm in re.finditer(r"<h3>(.*?)</h3>\s*((?:(?!<h3>).)*)", tail, re.S):
                a = re.sub(r"<[^>]+>", " ", qm.group(2)); a = re.sub(r"\s+", " ", html.unescape(a)).strip()
                if a: desc_faq.append((html.unescape(re.sub(r"<[^>]+>", "", qm.group(1))).strip(), a))
            hx = re.sub(r"<(/?)h3\b", r"<\1h2", head) + "<h2>Frequently asked questions</h2>" + tail
        else:
            hx = re.sub(r"<(/?)h3\b", r"<\1h2", hx)
        # sections should stand on their own: open each H2 section with the product's name instead of "This combo" / "It"
        subject = ("%s %s %s" % ("" if state_name == "any state" else state_name, p["level"], p["tierName"])).strip()
        subject = re.sub(r"\s+", " ", subject)
        def _open(m):
            lead, first = m.group(1), m.group(2)
            first2 = re.sub(r"^(This|this)\s+(?=(\d{4}\s+)?[A-Z][\w'’-]*\s+[A-Z])", "The ", first)           # "This 2026 Idaho Master … Combo is" -> "The 2026 Idaho …"
            if first2 == first:
                first2 = re.sub(r"^(This|this)\s+(?:(?:study guide and flash card|study|exam prep|complete|printed)\s+)?(combo|package|product|bundle|kit|set|study guide|guide|option)\b", "The " + subject, first)
            if first2 == first: first2 = re.sub(r"^It\s+(?=\w)", "The " + subject + " ", first)
            if first2 == first: first2 = re.sub(r"^(These|Those)\s+(materials|books|guides|resources|items|tools)\b", "The " + subject + " materials", first)
            return lead + first2
        hx = re.sub(r"(<h2[^>]*>.*?</h2>\s*(?:<p[^>]*>)?\s*)([^<]{0,200})", _open, hx, flags=re.S)
        hx = re.sub(r"^(\s*(?:<p[^>]*>)?\s*)([^<]{0,200})", _open, hx, count=1, flags=re.S)  # the description's own first paragraph sits under the "About this package" H2
        full = dict(full, html=hx)
    imgs = full["images"] or [p["image"]]
    v0 = p["variants"][0]
    c, n = float(v0.get("compareAt") or 0), float(v0["price"])
    compare_html = ('<s class="pc-was" id="pWas">%s</s><span class="pc-save" id="pSave">Save %d%%</span>' % (money(c), round((c - n) / c * 100))) if c > n else '<s class="pc-was" id="pWas" hidden></s><span class="pc-save" id="pSave" hidden></span>'
    variants_html = "".join('<label class="m-opt"><input type="radio" name="v" value="%s"%s><span>%s</span><b>%s%s</b></label>' % (
        v["id"], " checked" if i == 0 else "", html.escape(v["title"]), money(v["price"]),
        ('<s>%s</s>' % money(v["compareAt"])) if v.get("compareAt") and float(v["compareAt"]) > float(v["price"]) else "") for i, v in enumerate(p["variants"]))
    thumbs = "".join('<button type="button" data-src="%s" class="%s" aria-label="Image %d"><img src="%s" alt="%s, image %d" loading="lazy"></button>' % (html.escape(u), "on" if i == 0 else "", i + 1, html.escape(u), html.escape(p["tierName"]), i + 1) for i, u in enumerate(imgs))
    S = "" if state_name == "any state" else state_name
    inc_items = [x.format(Y=p["year"], S=S, L=p["level"]).replace("  ", " ") for x in INCLUDED.get(p["tier"], [])]
    inc = "".join("<li>%s</li>" % html.escape(x) for x in inc_items)
    ptk = takeaways_html([
        "%s %s %s: %s%s." % (state_name.capitalize() if state_name == "any state" else state_name, p["level"].lower(), p["tierName"], money(n), (", down from %s (save %d%%)" % (money(c), round((c - n) / c * 100))) if c > n else ""),
        ("%d items in the box: %s." % (len(inc_items), "; ".join(i.replace(p["year"] + " ", "", 1) for i in inc_items))) if inc_items else "Built on the %s National Electrical Code." % p["year"],
        ("%d optional add-on%s can be chosen at checkout, and the price updates when you pick one." % (len(p["variants"]) - 1, "" if len(p["variants"]) == 2 else "s")) if len(p["variants"]) > 1 else "Built on the %s National Electrical Code; check your candidate bulletin for the edition your state tests on." % p["year"],
        "Online kits arrive by email; books ship from our fulfillment center, %s. Buying does not grant exam eligibility, which comes from the state licensing board." % FUL["name"]])
    addons = [v["title"] for v in p["variants"][1:]]
    addons_html = ('<p class="addons"><b>Optional add-ons at checkout:</b> %s. Pick one above and the price updates.</p>' % html.escape("; ".join(addons))) if addons else ""
    related = "".join('<a class="rel" href="../%s/"><img src="%s" alt="%s" loading="lazy"><span><b>%s</b><small>%s</small></span><span class="pc-now">%s</span></a>' % (
        q["tierSlug"], html.escape(q["image"]), html.escape(q["tierName"]), html.escape(q["tierName"]), html.escape(clean_title(q["title"])[:60] + ("…" if len(clean_title(q["title"])) > 60 else "")), money(q["price"])) for q in siblings if q["id"] != p["id"])
    desc = trim_desc(p["desc"].replace(p["title"], "").strip())
    path = "/".join(path_parts) + "/"
    jsonld = {"@context": "https://schema.org", "@type": "Product", "name": clean_title(p["title"]), "image": imgs[:6], "description": p["desc"].replace(p["title"], "").strip()[:500],
              "brand": {"@type": "Brand", "name": FUL["name"]}, "sku": p["id"], "productID": p["id"], "category": "%s Electrician Exam Prep" % p["level"], "url": absurl(path),
              "offers": [{"@type": "Offer", "name": v["title"], "priceCurrency": "USD", "price": v["price"], "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition", "url": absurl(path), "seller": {"@type": "Organization", "name": BRAND}} for v in p["variants"]]}
    crumbs = [("All states", ""), (state_name.capitalize() if state_name == "any state" else state_name, "/".join(path_parts[:3]) + "/"), (p["level"], "/".join(path_parts[:3]) + "/"), (p["tierName"], path)]
    short_t = "%s %s %s" % ("" if state_name == "any state" else state_name, p["level"], p["tierName"]); short_t = re.sub(r"\s+", " ", short_t).strip()
    if len(short_t) + len(" (%s NEC)" % p["year"]) <= 60: short_t += " (%s NEC)" % p["year"]
    extra = head_extra(path, short_t, desc, imgs[0], rel, False, [crumbs_ld(crumbs), faq_ld([(q, a % p["year"] if "%s" in a else a) for q, a in PRODUCT_FAQ] + desc_faq[:12])])
    pjson = json.dumps({"id": p["id"], "variants": p["variants"], "title": clean_title(p["title"]), "state": p["state"], "level": p["level"], "tierName": p["tierName"], "price": p["price"]})
    assets_head = '<link rel="stylesheet" href="%sshared/base.css">\n<link rel="stylesheet" href="%sshared/store.css">' % (rel, rel)
    short_t = "%s %s %s" % ("" if state_name == "any state" else state_name, p["level"], p["tierName"]); short_t = re.sub(r"\s+", " ", short_t).strip()
    if len(short_t) + len(" (%s NEC)" % p["year"]) <= 60: short_t += " (%s NEC)" % p["year"]
    out = (ptpl.replace("{{TITLE}}", html.escape(short_t)).replace("{{DESC}}", html.escape(desc))
           .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % url) if url else "")
           .replace("{{OGIMAGE}}", '<meta property="og:image" content="%s">\n' % html.escape(imgs[0]))
           .replace("{{ASSETS_HEAD}}", assets_head).replace("{{ASSETS_PRODUCT}}", '<script src="%sshared/product.js"></script>' % rel)
           .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel)).replace("{{HEAD_EXTRA}}", extra)
           .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="%s" rel="noopener">Buy now</a>' % cart(v0["id"])))
           .replace("{{FOOTER}}", footer(rel, p["year"])).replace("{{ROUTE}}", json.dumps({"state": path_parts[0], "level": p["level"], "year": p["year"], "tier": p["tierSlug"], "depth": depth}))
           .replace("{{JSONLD}}", json.dumps(jsonld, ensure_ascii=False)).replace("{{P_JSON}}", pjson)
           .replace("{{HOME}}", rel).replace("{{LEVEL_URL}}", "../").replace("{{OTHER_LEVEL_URL}}", other_level_url).replace("{{OTHER_LEVEL}}", other_level)
           .replace("{{STATE}}", html.escape(state_name.capitalize() if state_name == "any state" else state_name)).replace("{{LEVEL}}", p["level"]).replace("{{YEAR}}", p["year"])
           .replace("{{TIER_NAME}}", html.escape(p["tierName"])).replace("{{H1}}", html.escape(clean_title(p["title"])))
           .replace("{{IMAGE}}", html.escape(imgs[0])).replace("{{THUMBS}}", thumbs if len(imgs) > 1 else "")
           .replace("{{PRICE}}", money(v0["price"])).replace("{{COMPARE_HTML}}", compare_html).replace("{{VARIANTS_HTML}}", variants_html)
           .replace("{{BUY_URL}}", cart(v0["id"])).replace("{{SHOP_URL}}", html.escape(p["url"]))
           .replace("{{MORE_LINKS_HTML}}", '<div class="more-links">%s</div>' % re.sub(r"<div><h3>(.*?)</h3><ul>(.*?)</ul></div>", lambda m: "<h3>%s</h3>%s" % (m.group(1), re.sub(r"<li>(.*?)</li>", r"\1", m.group(2))), related_pages_html(rel, GENERAL if state_name == "any state" else state_name, p["level"], p["year"], p["tierSlug"], p["tierName"]), flags=re.S))
           .replace("{{TAKEAWAYS_HTML}}", ptk).replace("{{INCLUDED_HTML}}", inc).replace("{{ADDONS_HTML}}", addons_html).replace("{{DESCRIPTION_HTML}}", full["html"]).replace("{{RELATED_HTML}}", related))
    d = os.path.join(ROOT, *path_parts); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f: f.write(anchor_ids(out))
    return url

# --- remove previously generated folders ---
manifest = os.path.join(ROOT, "generated-pages.txt")
if os.path.exists(manifest):
    for line in open(manifest):
        top = line.strip().split("/")[0]
        if top and os.path.isdir(os.path.join(ROOT, top)) and top not in ("shared", "designs", "store", "content", "tools"):
            shutil.rmtree(os.path.join(ROOT, top))
generated, urls = [], []

# --- root ---
years = sorted({p["year"] for p in CATALOG}, reverse=True)
u = page([], {"state": None, "level": None, "year": None, "tier": None, "depth": 0, "spa": not STATIC},
         "%s: %s Prep for All 50 States" % (BRAND, years[0]),
         "%s journeyman and master electrician exam prep for all 50 states. Pick your state, pick your level, pick a package. Study guides, flash cards, NEC code books with tabs, calculations guides and online practice." % years[0],
         "Your state. *Your *license. %s code." % years[0],
         "Journeyman and master electrician exam prep for all 50 states, built on the %s National Electrical Code. Pick your state and level, then choose how much help you want." % years[0],
         CFG.get("logo"), extra_ld=[org_ld(), website_ld(), faq_ld([(q, a % years[0] if "%s" in a else a) for q, a in LISTING_FAQ])], crumbs=[("Home", "")])
if u: urls.append(u)

# --- single-page mode: 404.html is the same app, so deep URLs render without folders ---
if not STATIC:
    shutil.copyfile(os.path.join(ROOT, "index.html"), os.path.join(ROOT, "404.html"))
    with open(manifest, "w") as f: f.write("")
    print("Built single-page site: index.html + 404.html (JS reads the URL). Run without --spa for one real page per URL.")
    sys.exit(0)

# --- state / level / year pages and package pages ---
for state in STATES + [GENERAL]:
    st = None if state == GENERAL else state
    for level in ("Journeyman", "Master"):
        for year in years:
            prods = [p for p in CATALOG if p["state"] == st and p["level"] == level and p["year"] == year and p["tier"] in TIERS]
            if not prods: continue
            prods.sort(key=lambda p: (p["rank"], p["id"]))
            seen, uniq = set(), []
            for p in prods:
                if p["tier"] in seen: continue
                seen.add(p["tier"]); uniq.append(p)
            name = "any state" if st is None else state
            parts = [slug(state), level.lower(), year]
            lo, hi = min(float(p["price"]) for p in uniq), max(float(p["price"]) for p in uniq)
            route = {"state": slug(state), "level": level, "year": year, "tier": None, "depth": 3}
            u = page(parts, route,
                     ("%s %s Electrician Exam Prep (%s NEC)" % (state, level, year)) if st is not None else ("%s Electrician Exam Prep, Any State (%s NEC)" % (level, year)),
                     "%s %s electrician exam prep for %s: %d packages from $%.2f to $%.2f. Study guide, flash cards, %s NEC with tabs, calculations guide and online practice. One click to checkout." % (year, level.lower(), name, len(uniq), lo, hi, year),
                     "%s. *%s. %s code." % ("Any state" if st is None else state, level, year),
                     "%s electrician exam prep for %s, built on the %s National Electrical Code. Choose how much help you want, from the study guide alone to the Ultimate Combo." % (level, name, year),
                     uniq[-1]["image"],
                     extra_ld=[{"@context": "https://schema.org", "@type": "CollectionPage", "name": "%s %s %s Electrician Exam Prep" % (year, name.capitalize() if st is None else state, level), "url": absurl("/".join(parts) + "/"),
                                "mainEntity": {"@type": "ItemList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "url": absurl("/".join(parts) + "/" + q["tierSlug"] + "/"), "name": clean_title(q["title"])} for i, q in enumerate(uniq)]}},
                               faq_ld([(qq, a % year if "%s" in a else a) for qq, a in LISTING_FAQ])],
                     crumbs=[("All states", ""), (name.capitalize() if st is None else state, "/".join(parts) + "/"), (level, "/".join(parts) + "/"), (year, "/".join(parts) + "/")])
            generated.append("/".join(parts)); urls.append(u) if u else None
            other = "Master" if level == "Journeyman" else "Journeyman"
            for p in uniq:
                pparts = parts + [p["tierSlug"]]
                u = product_page(pparts, p, uniq, name, "../", "../../../%s/%s/" % (other.lower(), year), other)
                generated.append("/".join(pparts)); urls.append(u) if u else None

with open(manifest, "w") as f: f.write("\n".join(generated) + "\n")

# --- 404.html: send unknown paths to the closest real page ---
state_slugs = {slug(s): s for s in STATES + [GENERAL]}
nf = """<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Redirecting…</title><meta name="robots" content="noindex">
<script>
(function(){var S=%s,Y=%s;var parts=location.pathname.split("/").filter(Boolean).map(function(x){return x.toLowerCase();});
var i=-1;for(var k=0;k<parts.length;k++){if(S.indexOf(parts[k])>-1){i=k;break;}}
var prefix="/"+parts.slice(0,Math.max(i,0)).join("/");if(prefix!=="/")prefix+="/";
if(i<0){location.replace(prefix);return;}
var lv=(parts[i+1]==="master")?"master":"journeyman";var yr=(/^\\d{4}$/.test(parts[i+2]||"")&&Y.indexOf(parts[i+2])>-1)?parts[i+2]:Y[0];
location.replace(prefix+parts[i]+"/"+lv+"/"+yr+"/");})();
</script></head><body><h1>Taking you to the right page…</h1><p><a href="/">Home</a></p></body></html>""" % (json.dumps(sorted(state_slugs)), json.dumps(years))
open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(nf)

# --- /search/ page (also the target of the schema.org SearchAction) ---
search_body = ('<main id="main" class="wrap search-page"><h1 id="h1">Search</h1><form id="searchPage" class="srch-form" role="search"><input class="srch-q" name="q" type="search" placeholder="State, package or product\u2026" aria-label="Search" autocomplete="off"><button class="btn btn-buy" type="submit">Search</button></form><div id="searchOut"></div></main>')
sp = tpl[:tpl.index("<body>")]
sp = (sp.replace("{{ASSETS_HEAD}}", '<link rel="stylesheet" href="../shared/base.css">\n<link rel="stylesheet" href="../shared/store.css">').replace("{{TITLE}}", "Search | " + BRAND).replace("{{DESC}}", "Search %s electrician exam prep packages by state, level or product." % BRAND)
      .replace("{{CANONICAL}}", "").replace("{{OGIMAGE}}", "").replace("{{HEAD_EXTRA}}", head_extra("search/", "Search | " + BRAND, "Search electrician exam prep packages.", CFG.get("logo"), "../", noindex=True)))
sp += ('<body><a class="skip" href="#main">Skip to content</a><header class="nav"><div class="wrap"><a class="brand" href="../" id="homeLink">{{WORDMARK}}</a>' + nav_tools('<a class="btn btn-buy" href="../#packs">Pick my package</a>') + '</div></header>'
       + search_body + footer("../", years[0]) + '<script>window.ROUTE={"depth":1};</script><script src="../shared/catalog.js"></script><script src="../shared/search.js"></script><script src="../shared/track.js"></script></body></html>')
os.makedirs(os.path.join(ROOT, "search"), exist_ok=True); open(os.path.join(ROOT, "search", "index.html"), "w", encoding="utf-8").write(anchor_ids(sp))

# --- /admin/ dashboard (noindex; analytics needs Google sign-in) ---
atpl = open(os.path.join(ROOT, "store", "admin.html"), encoding="utf-8").read()
admin_cfg = {"gtagId": CFG.get("gtagId", ""), "ga4PropertyId": CFG.get("ga4PropertyId", ""), "googleOAuthClientId": CFG.get("googleOAuthClientId", ""), "repo": CFG.get("repo", ""), "siteUrl": SITE or ""}
os.makedirs(os.path.join(ROOT, "admin"), exist_ok=True)
open(os.path.join(ROOT, "admin", "index.html"), "w", encoding="utf-8").write(brand_tokens(atpl.replace("{{ADMIN_JSON}}", json.dumps(admin_cfg))))

# --- blog: content/posts/*.md -> /blog/, /blog/<slug>/, /blog/feed.xml ---
btpl = open(os.path.join(ROOT, "store", "blog-post.html"), encoding="utf-8").read()
bitpl = open(os.path.join(ROOT, "store", "blog-index.html"), encoding="utf-8").read()
def nice_date(d):
    try: return datetime.date.fromisoformat(d[:10]).strftime("%B %-d, %Y")
    except Exception: return d
def post_card(q, rel):
    img = ('<img src="%s" alt="" loading="lazy">' % html.escape(q["image"])) if q["image"] else ('<div class="noimg">%s</div>' % html.escape(q["title"][:48]))
    return ('<a class="card" href="%sblog/%s/" data-track="blog_card">%s<div class="card-body"><p class="post-meta"><time datetime="%s">%s</time><span>%d min read</span></p><h2>%s</h2><p>%s</p></div></a>'
            % (rel, q["slug"], img, q["date"], nice_date(q["date"]), max(1, round(q["words"] / 220)), html.escape(q["title"]), html.escape(q["excerpt"])))
def blog_common(out, rel, path, title, desc, image, lds, route, extra_noindex=False):
    desc = trim_desc(desc)
    return (out.replace("{{TITLE}}", html.escape(title)).replace("{{DESC}}", html.escape(desc)).replace("{{BRAND}}", html.escape(BRAND))
            .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % absurl(path)) if SITE else "")
            .replace("{{OGIMAGE}}", ('<meta property="og:image" content="%s">\n' % html.escape(image)) if image else "")
            .replace("{{HEAD_EXTRA}}", head_extra(path, title, desc, image, rel, extra_noindex, lds))
            .replace("{{ASSETS_HEAD}}", '<link rel="stylesheet" href="%sshared/base.css">\n<link rel="stylesheet" href="%sshared/store.css">' % (rel, rel))
            .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/catalog.js" defer></script>\n<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel, rel))
            .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="%s#packs">Pick my package</a>' % rel)).replace("{{FOOTER}}", footer(rel, years[0]))
            .replace("{{ROUTE}}", json.dumps(route)).replace("{{REL}}", rel).replace("{{HOME}}", rel))
blog_dir = os.path.join(ROOT, "blog"); shutil.rmtree(blog_dir, ignore_errors=True); os.makedirs(blog_dir, exist_ok=True)
all_tags = sorted({t for q in POSTS for t in q["tags"]}, key=str.lower)
def blog_index(dest_parts, posts, tag=None):
    rel = "../" * len(dest_parts); path = "/".join(dest_parts) + "/"
    title = ("Posts tagged %s | %s" % (tag, BRAND)) if tag else ("Electrician Exam Prep Blog | %s" % BRAND)
    desc = ("Posts tagged %s from the %s electrician exam prep blog." % (tag, BRAND)) if tag else ("Study tips, NEC code changes, state licensing updates and exam strategy from %s. New posts every month." % BRAND)
    h1 = ("Posts tagged \u201c%s\u201d" % tag) if tag else "The Electrician Exam Prep Blog"
    lead = ("%d post%s." % (len(posts), "" if len(posts) == 1 else "s")) if tag else "Study strategies, code changes, licensing news and the questions we hear every day on the phone. Written by the people who write the exam prep."
    feat, rest = (posts[0], posts[1:]) if posts and not tag else (None, posts)
    feat_html = ""
    if feat:
        fimg = ('<img src="%s" alt="">' % html.escape(feat["image"])) if feat["image"] else ""
        feat_html = ('<a class="feature%s" href="%sblog/%s/" data-track="blog_featured">%s<div><span class="pc-tier">Latest</span><h2>%s</h2><p>%s</p><p class="post-meta"><time datetime="%s">%s</time><span>%d min read</span></p></div></a>'
                     % ("" if fimg else " noimg", rel, feat["slug"], fimg, html.escape(feat["title"]), html.escape(feat["excerpt"]), feat["date"], nice_date(feat["date"]), max(1, round(feat["words"] / 220))))
    tagf = ('<nav class="tagbar" aria-label="Topics"><a class="tag" href="%sblog/"%s>All</a>%s</nav>' % (rel, "" if tag else ' aria-current="page"', "".join('<a class="tag" href="%sblog/tag/%s/"%s>%s</a>' % (rel, blogkit.slugify(t), ' aria-current="page"' if tag == t else "", html.escape(t)) for t in all_tags))) if all_tags else ""
    cards = "".join(post_card(q, rel) for q in rest)
    empty = '' if posts else '<p class="empty">No posts yet. The first one is on its way.</p>'
    lds = [crumbs_ld([("Home", ""), ("Blog", "blog/")] + ([(tag, path)] if tag else [])),
           {"@context": "https://schema.org", "@type": "Blog" if not tag else "CollectionPage", "name": h1, "url": absurl(path), "publisher": {"@type": "Organization", "name": BRAND},
            "blogPost" if not tag else "hasPart": [{"@type": "BlogPosting", "headline": q["title"], "url": absurl("blog/%s/" % q["slug"]), "datePublished": q["date"], "image": q["image"] or None} for q in posts[:20]]}]
    bfaq = [(q, a % FUL["name"] if "%s" in a else a) for q, a in BLOG_FAQ]
    if not tag: lds.append(faq_ld(bfaq))
    out = blog_common(bitpl, rel, path, title, desc, (feat or {}).get("image") or CFG.get("logo"), lds, {"depth": len(dest_parts), "blog": True}, extra_noindex=bool(tag))
    out = out.replace("{{YEAR}}", years[0])
    intro = "" if tag else ('<div class="blog-intro"><p>Most people who fail a licensing exam do not fail on knowledge. They run out of time in the code book, misread an exception, or walk in with the wrong edition. These posts are about the parts of passing that the study guide cannot do for you: how to tab and navigate the %s NEC, how to pace a timed exam, what each state board actually asks for, and what changes between code cycles.</p><p>New posts land here first and in the <a href="%sblog/feed.xml">RSS feed</a>. When a post is about one state, it links straight to that state\u2019s journeyman and master packages so you can act on it.</p></div>' % (years[0], rel))
    btk = takeaways_html([
        "%d post%s so far%s, written for people sitting the journeyman or master electrician exam." % (len(posts), "" if len(posts) == 1 else "s", (" tagged %s" % tag) if tag else ""),
        "Topics: %s." % ", ".join(all_tags[:8]) if all_tags else "Topics cover study strategy, NEC navigation and state licensing rules.",
        "Every post links to the matching state packages, built on the %s National Electrical Code." % years[0],
        "New posts appear in the RSS feed at /blog/feed.xml the moment they are published."])
    out = out.replace("{{BLOG_FAQ_HTML}}", "".join('<details%s><summary>%s</summary><p>%s</p></details>' % (" open" if i == 0 else "", html.escape(q), html.escape(a)) for i, (q, a) in enumerate(bfaq)))
    out = out.replace("{{TAKEAWAYS_HTML}}", btk).replace("{{INTRO_HTML}}", intro).replace("{{H1}}", html.escape(h1)).replace("{{LEAD}}", html.escape(lead)).replace("{{TAG_FILTER}}", tagf).replace("{{FEATURED_HTML}}", feat_html).replace("{{CARDS_HTML}}", cards).replace("{{EMPTY_HTML}}", empty)
    d = os.path.join(ROOT, *dest_parts); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(anchor_ids(out))
    if SITE and not tag: urls.append(absurl(path))  # tag pages are thin by nature: noindex, not in the sitemap
blog_index(["blog"], POSTS)
for t in all_tags: blog_index(["blog", "tag", blogkit.slugify(t)], [q for q in POSTS if t in q["tags"]], t)
from urllib.parse import quote
pages_dir = os.path.join(ROOT, "pages"); shutil.rmtree(pages_dir, ignore_errors=True)
for q in POSTS + PAGES:
    is_page = q.get("kind") == "page"
    parts = ["pages" if is_page else "blog", q["slug"]]; rel = "../../"; path = "%s/%s/" % (parts[0], q["slug"]); url = absurl(path)
    st_slug = slug(q["state"]) if q["state"] and q["state"] in STATES else None
    lv = q["level"].capitalize() if q["level"].lower() in ("journeyman", "master") else None
    if st_slug:
        cta_url = "%s%s/%s/%s/" % (rel, st_slug, (lv or "journeyman").lower(), years[0]); cta_kicker = "%s %s exam" % (q["state"], lv or "Journeyman")
        cta_title = "Ready to study for the %s %s exam?" % (q["state"], (lv or "journeyman").lower()); cta_text = "Packages built on the %s NEC, from the study guide alone to the Ultimate Combo. One click to checkout." % years[0]; cta_label = "See %s packages" % q["state"]
        more_link = '<a href="%s">%s packages</a>' % (cta_url, html.escape(q["state"]))
    else:
        cta_url = rel + "#packs"; cta_kicker = "Ready to study?"; cta_title = "Pick your state and level, then choose a package."; cta_text = "Every package starts with the state exam prep study guide, built on the %s National Electrical Code." % years[0]; cta_label = "Pick my package"; more_link = ""
    related = [r for r in POSTS if r["slug"] != q["slug"] and (set(r["tags"]) & set(q["tags"]))][:3] or [r for r in POSTS if r["slug"] != q["slug"]][:3]
    rel_html = ('<section class="related-posts" aria-labelledby="h-more"><h2 id="h-more">Keep reading</h2><div class="post-grid">%s</div></section>' % "".join(post_card(r, rel) for r in related)) if related else ""
    tags_html = ('<nav class="tagbar" aria-label="Topics">%s</nav>' % "".join('<a class="tag" href="%sblog/tag/%s/">%s</a>' % (rel, blogkit.slugify(t), html.escape(t)) for t in q["tags"])) if q["tags"] else ""
    hero = ('<figure class="hero"><img src="%s" alt="%s" fetchpriority="high"></figure>' % (html.escape(q["image"]), html.escape(q["title"]))) if q["image"] and ('src="%s"' % q["image"]) not in q["html"] else ""
    lds = [crumbs_ld([("Home", ""), ("Blog", "blog/"), (q["title"], path)]),
           {"@context": "https://schema.org", "@type": "BlogPosting", "headline": q["title"][:110], "description": q["excerpt"], "image": [q["image"]] if q["image"] else None, "datePublished": q["date"], "dateModified": q["updated"],
            "author": {"@type": "Organization" if not q["author"] or q["author"] == BRAND else "Person", "name": q["author"] or BRAND}, "publisher": {"@type": "Organization", "name": BRAND, "logo": {"@type": "ImageObject", "url": CFG.get("logo")}},
            "mainEntityOfPage": url, "url": url, "wordCount": q["words"], "keywords": ", ".join(q["tags"]) or None, "articleSection": "Electrician Exam Prep", "inLanguage": "en-US"}]
    lds[1] = {k: v for k, v in lds[1].items() if v}
    ptitle = q.get("meta_title") or (q["title"] if len(q["title"]) + len(BRAND) + 3 > 60 else "%s | %s" % (q["title"], BRAND))
    pdesc = q.get("meta_description") or q["excerpt"]
    if is_page: lds[0] = crumbs_ld([("Home", ""), (q["title"], path)]); lds[1]["@type"] = "Article"
    out = blog_common(btpl, rel, path, ptitle, pdesc, q["image"] or CFG.get("logo"), lds, {"depth": 2, "blog": True, "post": q["slug"]})
    if is_page: out = out.replace('<a href="{{REL}}blog/">Blog</a><span>/</span>', "").replace('<p class="post-meta">', '<p class="post-meta" hidden>')
    out = (out.replace("{{H1}}", html.escape(q["title"])).replace("{{TITLE_SHORT}}", html.escape(q["title"][:60] + ("…" if len(q["title"]) > 60 else ""))).replace("{{EXCERPT}}", html.escape(q["excerpt"]))
           .replace("{{DATE}}", q["date"]).replace("{{UPDATED}}", q["updated"]).replace("{{DATE_NICE}}", nice_date(q["date"])).replace("{{AUTHOR_HTML}}", ('<span>%s</span>' % html.escape(q["author"])) if q["author"] else "")
           .replace("{{READ_MIN}}", str(max(1, round(q["words"] / 220)))).replace("{{TAGS_HTML}}", tags_html).replace("{{HERO_HTML}}", hero).replace("{{TAKEAWAYS_HTML}}", takeaways_html(q.get("takeaways") or [])).replace("{{BODY_HTML}}", q["html"])
           .replace("{{URL_ENC}}", quote(url, safe="")).replace("{{TITLE_ENC}}", quote(q["title"], safe="")).replace("{{MORE_LINK}}", more_link)
           .replace("{{CTA_KICKER}}", html.escape(cta_kicker)).replace("{{CTA_TITLE}}", html.escape(cta_title)).replace("{{CTA_TEXT}}", html.escape(cta_text)).replace("{{CTA_URL}}", cta_url).replace("{{CTA_LABEL}}", html.escape(cta_label))
           .replace("{{RELATED_HTML}}", rel_html))
    d = os.path.join(ROOT, *parts); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(anchor_ids(out))
    if SITE: urls.append(url)
# redirects for renamed posts (written by the dashboard when a handle changes)
rpath = os.path.join(ROOT, "content", "redirects.json")
if os.path.exists(rpath):
    try: RED = json.load(open(rpath, encoding="utf-8"))
    except Exception: RED = {}
    for old, new in RED.items():
        old = old.strip("/"); new = new.strip("/")
        if not old or old == new or os.path.exists(os.path.join(ROOT, *old.split("/"), "index.html")): continue
        target = absurl(new + "/")
        os.makedirs(os.path.join(ROOT, *old.split("/")), exist_ok=True)
        open(os.path.join(ROOT, *old.split("/"), "index.html"), "w", encoding="utf-8").write('<!doctype html><html lang="en"><head><meta charset="utf-8"><title>Moved</title><meta name="robots" content="noindex"><link rel="canonical" href="%s"><meta http-equiv="refresh" content="0; url=%s"><script>location.replace(%s)</script></head><body><p>This page has moved to <a href="%s">%s</a>.</p></body></html>' % (html.escape(target), html.escape(target), json.dumps(target), html.escape(target), html.escape(target)))
# RSS feed
feed_items = "".join("<item><title>%s</title><link>%s</link><guid isPermaLink=\"true\">%s</guid><pubDate>%s</pubDate><description>%s</description>%s</item>\n" % (
    html.escape(q["title"]), absurl("blog/%s/" % q["slug"]), absurl("blog/%s/" % q["slug"]), datetime.datetime.fromisoformat(q["date"][:10]).strftime("%a, %d %b %Y 09:00:00 -0500"), html.escape(q["excerpt"]),
    ("<enclosure url=\"%s\" type=\"image/jpeg\" length=\"0\"/>" % html.escape(q["image"])) if q["image"] else "") for q in POSTS[:30])
open(os.path.join(blog_dir, "feed.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>%s Blog</title><link>%s</link><description>Electrician exam prep study tips, NEC changes and licensing news.</description><language>en-us</language>\n%s</channel></rss>\n' % (html.escape(BRAND), absurl("blog/"), feed_items))
open(os.path.join(blog_dir, "posts.json"), "w", encoding="utf-8").write(json.dumps([{k: q[k] for k in ("slug", "title", "date", "updated", "excerpt", "image", "tags", "state", "level", "author", "words")} for q in POSTS], ensure_ascii=False))

# --- FAQ: /faq/ (nationwide) + /faq/<state>/<level>/ (from the product descriptions) ---
ftpl = open(os.path.join(ROOT, "store", "faq.html"), encoding="utf-8").read()
GEN_FAQ = json.load(open(os.path.join(ROOT, "content", "faq-general.json"), encoding="utf-8"))["categories"]
STOP = set("the a an is are do does i my for of in on to and or what which who how can be with this that it its exam exams electrician electricians licensing license test".split())
def qkey(q):
    q = re.sub(r"^\s*faq\s*:\s*", "", q, flags=re.I).lower(); q = re.sub(r"[^a-z0-9 ]", " ", q)
    return frozenset(w for w in q.split() if w not in STOP and len(w) > 2)
PRODUCT_Q = re.compile(r"\b(this|the)\s+([\w+\- ]*?)(combo|package|product|kit|bundle|set|course|guide)\b|\bincluded\b|\binclude\b|\bcourse access\b|\bships?\b|\bshipping\b|\bdelivered\b|\brefund|\bprice|\bcost\b|\bdiscount", re.I)
def state_faqs():
    groups = {}
    for p in CATALOG:
        full = FULL.get(p["id"]); hx = full and full.get("html")
        if not hx or p["tier"] not in TIERS: continue
        m = re.search(r"<h3>\s*(FAQ[^<]*|Frequently Asked Questions[^<]*)</h3>", hx, re.I)
        if not m: continue
        key = (p["state"] or GENERAL, p["level"]); g = groups.setdefault(key, [])
        for q, a in re.findall(r"<h3>(.*?)</h3>\s*((?:(?!<h3>).)*)", hx[m.end():], re.S):
            q = html.unescape(re.sub(r"<[^>]+>", "", q)).strip(); q = re.sub(r"^\s*faq\s*:\s*", "", q, flags=re.I)
            a = re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", a))).strip()
            if not a or not q or PRODUCT_Q.search(q): continue
            if FUL["name"] != BRAND: a = re.sub(r"(?<![\w/.-])1 ?Exam ?Prep(?![\w.-])", BRAND, a)
            k = qkey(q)
            if not k: continue
            dup = None
            for item in g:
                inter = len(k & item["k"]); uni = len(k | item["k"]) or 1
                if inter / uni >= 0.75: dup = item; break
            if dup:
                if len(a) > len(dup["a"]): dup["q"], dup["a"] = q, a
            else: g.append({"q": q, "a": a, "k": k})
    return groups
STATE_FAQS = state_faqs()
def faq_details(items, open_first=True):
    return '<div class="faq">%s</div>' % "".join('<details%s><summary>%s</summary><p>%s</p></details>' % (" open" if open_first and i == 0 else "", html.escape(q), html.escape(a)) for i, (q, a) in enumerate(items))
def faq_page(parts, title, h1, lead, sections, pairs_for_schema, crumbs, takeaways, cta, related_html, more_link=""):
    rel = "../" * len(parts); path = "/".join(parts) + "/"
    jump = "".join('<a class="tag" href="#%s">%s <small>%d</small></a>' % (sid, html.escape(name), n) for sid, name, n in [(sid, name, n) for sid, name, n, _ in sections])
    secs = "".join('<section class="faq-sec" aria-labelledby="%s"><h2 id="%s">%s</h2>%s</section>' % (sid, sid, html.escape(name), body) for sid, name, n, body in sections)
    lds = [crumbs_ld(crumbs), faq_ld(pairs_for_schema[:80])]
    desc = trim_desc(lead)
    out = (ftpl.replace("{{TITLE}}", html.escape(title)).replace("{{DESC}}", html.escape(desc)).replace("{{BRAND}}", html.escape(BRAND))
           .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % absurl(path)) if SITE else "").replace("{{OGIMAGE}}", ('<meta property="og:image" content="%s">\n' % html.escape(CFG.get("logo"))) if CFG.get("logo") else "")
           .replace("{{HEAD_EXTRA}}", head_extra(path, title, desc, CFG.get("logo"), rel, False, lds))
           .replace("{{ASSETS_HEAD}}", '<link rel="stylesheet" href="%sshared/base.css">\n<link rel="stylesheet" href="%sshared/store.css">' % (rel, rel))
           .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/catalog.js" defer></script>\n<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel, rel))
           .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="%s#packs">Pick my package</a>' % rel)).replace("{{FOOTER}}", footer(rel, years[0]))
           .replace("{{ROUTE}}", json.dumps({"depth": len(parts), "faq": True})).replace("{{REL}}", rel).replace("{{HOME}}", rel)
           .replace("{{CRUMB_HTML}}", "".join(('<a href="%s">%s</a><span>/</span>' % (rel + cp, html.escape(cn))) if i < len(crumbs) - 1 else html.escape(cn) for i, (cn, cp) in enumerate(crumbs)))
           .replace("{{H1}}", html.escape(h1)).replace("{{LEAD}}", html.escape(lead)).replace("{{TAKEAWAYS_HTML}}", takeaways_html(takeaways)).replace("{{JUMP_HTML}}", jump).replace("{{SECTIONS_HTML}}", secs)
           .replace("{{CTA_KICKER}}", html.escape(cta[0])).replace("{{CTA_TITLE}}", html.escape(cta[1])).replace("{{CTA_TEXT}}", html.escape(cta[2])).replace("{{CTA_URL}}", cta[3]).replace("{{CTA_LABEL}}", html.escape(cta[4]))
           .replace("{{RELATED_HTML}}", related_html).replace("{{MORE_LINK}}", more_link))
    d = os.path.join(ROOT, *parts); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(anchor_ids(out))
    if SITE: urls.append(absurl(path))
shutil.rmtree(os.path.join(ROOT, "faq"), ignore_errors=True)
total_state_q = sum(len(v) for v in STATE_FAQS.values())
# state/level pages
for (st, lv), items in sorted(STATE_FAQS.items(), key=lambda kv: (kv[0][0] == GENERAL, kv[0])):
    name = "any state" if st == GENERAL else st; parts = ["faq", slug(st), lv.lower()]; rel = "../../../"
    pairs = [(i["q"], i["a"]) for i in items]
    other = "Master" if lv == "Journeyman" else "Journeyman"
    # group loosely by topic for scannability
    buckets = [("exam", "The exam", lambda q: re.search(r"open book|question|portion|score|pass|time|minutes|hours|structure|format|administer|vendor|psi|prometric|pearson|schedul|retake|fail", q, re.I)),
               ("license", "Licensing and experience", lambda q: re.search(r"licens|regulat|board|experience|hours|apprentice|apply|application|eligib|reciproc|renew|continuing|contractor|supervis|permit", q, re.I)),
               ("code", "Code book and materials", lambda q: re.search(r"nec|code|edition|book|reference|calculat|allowed|bring|write|highlight", q, re.I))]
    used, sections = set(), []
    for sid, sname, test in buckets:
        sel = [(q, a) for (q, a) in pairs if (q, a) not in used and test(q)]
        if sel: sections.append((sid, sname, len(sel), faq_details(sel))); used.update(sel)
    rest = [(q, a) for (q, a) in pairs if (q, a) not in used]
    if rest: sections.append(("more", "More questions", len(rest), faq_details(rest, False)))
    tk = ["%d questions and answers about the %s %s electrician exam and license, compiled from our %s package descriptions." % (len(pairs), name, lv.lower(), lv.lower()),
          next((a for q, a in pairs if re.search(r"open book", q, re.I)), "Check the candidate bulletin for the edition of the NEC your exam is written to."),
          next((a for q, a in pairs if re.search(r"regulat|licens.*(board|through)|who (issues|handles|administers)", q, re.I)), "Licensing rules come from the state board; the questions below name it."),
          "Prep packages for this exam start at %s; every one includes the state study guide with 12 practice exams and 2 finals." % money(min(float(p["price"]) for p in products_for(st, lv, years[0])) if products_for(st, lv, years[0]) else "$99.95")]
    cta = ("%s %s exam" % (name.capitalize() if st == GENERAL else st, lv.lower()), "Ready to study for the %s %s exam?" % (name, lv.lower()), "Packages built on the %s NEC, from the study guide alone to the Ultimate Combo. One click to checkout." % years[0], "%s%s/%s/%s/" % (rel, slug(st), lv.lower(), years[0]), "See %s %s packages" % (name if st != GENERAL else "any-state", lv.lower()))
    related = '<section class="related-pages" style="background:transparent;padding:0;margin-top:2.5rem"><div class="wrap" style="padding:0"><h2 style="font-size:1.3rem;text-transform:none">Related pages</h2><div class="rp-cols">%s</div></div></section>' % (
        related_pages_html(rel, st, lv, years[0]).replace('<li><a href="%s%s/%s/%s/">' % (rel, slug(st), other.lower(), years[0]), '<li><a href="%sfaq/%s/%s/">' % (rel, slug(st), other.lower())) )
    related = related.replace("packages</a>", " FAQ</a>", 1)
    faq_page(parts, "%s %s Electrician Exam FAQ (%d answers)" % ("Any-State" if st == GENERAL else st, lv, len(pairs)) if len("%s %s Electrician Exam FAQ (%d answers)" % (st, lv, len(pairs))) <= 60 else "%s %s Electrician Exam FAQ" % (st, lv),
             "%s %s electrician exam: frequently asked questions" % (name.capitalize() if st == GENERAL else st, lv.lower()),
             "%d answers about the %s %s electrician exam and license: who issues it, open-book rules, the NEC edition, experience hours, exam structure and passing scores. Filter the list or jump to a section." % (len(pairs), name, lv.lower()),
             sections, pairs, [("Home", ""), ("FAQ", "faq/"), ("%s %s" % (name.capitalize() if st == GENERAL else st, lv), "faq/%s/%s/" % (slug(st), lv.lower()))], tk, cta, related,
             '<a href="%s%s/%s/%s/">%s %s packages</a>' % (rel, slug(st), lv.lower(), years[0], html.escape(name.capitalize() if st == GENERAL else st), lv.lower()))
# hub
gen_sections = [(c["slug"], c["name"], len(c["items"]), faq_details([(q, a.replace("1 Exam Prep", FUL["name"])) for q, a in c["items"]])) for c in GEN_FAQ]
gen_pairs = [(q, a) for c in GEN_FAQ for q, a in c["items"]]
state_list = "".join('<li><a href="%s/%s/">%s</a><span><a href="%s/journeyman/">Journeyman %d</a><a href="%s/master/">Master %d</a></span></li>' % (slug(st), "journeyman", "Any state (general)" if st == GENERAL else st, slug(st), len(STATE_FAQS.get((st, "Journeyman"), [])), slug(st), len(STATE_FAQS.get((st, "Master"), []))) for st in STATES + [GENERAL] if (st, "Journeyman") in STATE_FAQS or (st, "Master") in STATE_FAQS)
gen_sections.append(("states", "State by state", total_state_q, '<p class="faq-count">%d state-specific answers across %d pages. Each page covers who issues the license, the open-book rules, the NEC edition, experience and the exam format for that state and level.</p><ul class="faq-states">%s</ul>' % (total_state_q, len(STATE_FAQS), state_list)))
faq_page(["faq"], "Electrician Exam FAQ: %d Answers | %s" % (len(gen_pairs) + total_state_q, BRAND) if len("Electrician Exam FAQ: %d Answers | %s" % (len(gen_pairs) + total_state_q, BRAND)) <= 60 else "Electrician Exam FAQ: %d Answers" % (len(gen_pairs) + total_state_q),
         "Electrician exam FAQ", "%d answers about journeyman and master electrician exams: getting licensed, the exam itself, studying, the code book, calculations, exam day and what comes after, plus %d state-specific answers for all 50 states." % (len(gen_pairs) + total_state_q, total_state_q),
         gen_sections, gen_pairs, [("Home", ""), ("FAQ", "faq/")],
         ["%d questions answered on this page, nationwide, and %d more on the state pages linked at the bottom." % (len(gen_pairs), total_state_q),
          "Most states need about 8,000 hours of supervised experience for the journeyman exam and set the pass mark at 70 to 75 percent.",
          "Nearly every exam is open book for the code portion; the edition you bring must match the one in your state's candidate bulletin.",
          "Six to eight weeks at about 90 minutes a day, split between code navigation, calculations and timed practice, is enough for most candidates."],
         ("Ready to study?", "Pick your state and level, then choose a package.", "Every package starts with the state study guide, 12 practice exams and 2 full-length finals, built on the %s National Electrical Code." % years[0], "../#packs", "Pick my package"),
         '<section class="related-pages" style="background:transparent;padding:0;margin-top:2.5rem"><div class="wrap" style="padding:0"><h2 style="font-size:1.3rem;text-transform:none">Keep reading</h2><div class="rp-cols"><div><h3>Guides</h3><ul><li><a href="../blog/">Blog: study plans and code navigation</a></li><li><a href="../#compare">Compare the five packages</a></li><li><a href="../#states">Every state and level</a></li></ul></div></div></div></section>')
print("FAQ: %d general + %d state-specific answers on %d pages" % (len(gen_pairs), total_state_q, len(STATE_FAQS) + 1))

# --- icons + manifest ---
fav = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#1b1f3b"/><path d="M36 8 18 36h12l-4 20 20-30H34z" fill="#ff5a1f"/></svg>'
if not HAS_PNG_ICONS: open(os.path.join(ROOT, "shared", "favicon.svg"), "w").write(fav)
if HAS_PNG_ICONS: pass  # real logo assets from tools/make_logo.py: keep them
else:
  try:
      from PIL import Image, ImageDraw
      from PIL import ImageFont
      bolt = lambda sc, ox, oy: [(ox + x * sc, oy + y * sc) for x, y in [(36, 8), (18, 36), (30, 36), (26, 56), (46, 26), (34, 26)]]
      im = Image.new("RGBA", (180, 180), (27, 31, 59, 255)); ImageDraw.Draw(im).polygon(bolt(2.6, 7, 7), fill=(255, 90, 31, 255)); im.save(os.path.join(ROOT, "shared", "apple-touch-icon.png"))
      # logo.png: 1200x630 social card / Organization logo with the brand name
      def font(sz):
          for f in ("/usr/share/fonts/truetype/dejavu/DejaVuSans-Bold.ttf", "/usr/share/fonts/truetype/liberation/LiberationSans-Bold.ttf"):
              if os.path.exists(f): return ImageFont.truetype(f, sz)
          return ImageFont.load_default()
      lg = Image.new("RGB", (1200, 630), (27, 31, 59)); d = ImageDraw.Draw(lg)
      d.polygon(bolt(4.2, 90, 150), fill=(255, 90, 31))
      words, lines, cur = BRAND.split(), [], ""
      for w in words:
          t = (cur + " " + w).strip()
          if d.textlength(t, font=font(78)) > 820: lines.append(cur); cur = w
          else: cur = t
      lines.append(cur); y = 315 - 46 * len(lines)
      for ln in lines: d.text((330, y), ln, font=font(78), fill="white"); y += 92
      tl, tcur, tlines = CFG.get("tagline", "").split(), "", []
      for w in tl:
          t = (tcur + " " + w).strip()
          if d.textlength(t, font=font(30)) > 820: tlines.append(tcur); tcur = w
          else: tcur = t
      tlines.append(tcur)
      for ln in tlines[:2]: d.text((330, y + 10), ln, font=font(30), fill=(255, 176, 143)); y += 40
      d.text((330, 560), "Fulfilled by %s" % FUL["name"], font=font(24), fill=(170, 175, 205))
      lg.save(os.path.join(ROOT, "shared", "logo.png"), optimize=True)
  except Exception as e: print("apple-touch-icon skipped:", e)
open(os.path.join(ROOT, "manifest.webmanifest"), "w").write(json.dumps({"name": BRAND, "short_name": WM[1] or BRAND[:12], "start_url": "./", "display": "browser", "background_color": "#f7f6f2", "theme_color": "#1b1f3b", "icons": ([{"src": "shared/logo-mark.png", "sizes": "512x512", "type": "image/png"}] if HAS_PNG_ICONS else []) + [{"src": "shared/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}] + ([] if HAS_PNG_ICONS else [{"src": "shared/favicon.svg", "sizes": "any", "type": "image/svg+xml"}])}, indent=1))

# --- robots.txt (AI crawlers explicitly welcome) + llms.txt ---
bots = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-User", "anthropic-ai", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bytespider", "CCBot", "Amazonbot", "meta-externalagent"]
rb = ("# robots.txt for %s Electrician Exam Prep (%s)\n# Search engines and AI assistants are both welcome. Internal search, the design gallery,\n# raw data files and the admin page are held back because they are not useful in results.\n\n" % (BRAND, (SITE or "/").rstrip("/"))
      + "User-agent: *\nAllow: /\nDisallow: /designs/\nDisallow: /gallery.html\nDisallow: /search/\nDisallow: /store/\nDisallow: /admin/\nDisallow: /*?q=\n\n# Named so the allow is explicit for AI crawlers.\n" + "".join("User-agent: %s\nAllow: /\n\n" % b for b in bots))
if SITE: rb += "Sitemap: %ssitemap.xml\n# Blog: %sblog/ (RSS at %sblog/feed.xml). FAQ: %sfaq/\n# Guides for AI assistants: %sllms.txt and %sagents.md\n" % (SITE, SITE, SITE, SITE, SITE, SITE)
open(os.path.join(ROOT, "robots.txt"), "w").write(rb)
tiers_desc = "Packages per state and level, lowest to highest: Study Guide + Flash Cards ($99.95), Study Guide + NEC with Tabs ($249.95), Study Guide + Calculations + NEC ($279.95), Super Combo ($349.95), Ultimate Combo ($399.95, adds the online test success kit)."
llm = ["# %s" % BRAND, "", "> %s journeyman and master electrician exam prep packages for all 50 US states, built on the %s National Electrical Code. Study guides, flash cards, NEC code books with pre-printed tabs, calculations guides and online practice exams. Buy buttons go straight to secure checkout; orders are fulfilled by %s. Phone %s, email %s." % (years[0], years[0], FUL["name"], CFG["phone"], CFG["email"]), "",
       "## How the site is organised", "", "- `/` picks a state and a level (Journeyman or Master).", "- `/<state>/<journeyman|master>/<year>/` lists that combination's packages (multi-word states use a dash, e.g. `/new-york/`; `/general/` is the non-state edition).", "- `/<state>/<level>/<year>/<package>/` is a full product page. Package slugs: study-guide-flash-cards, study-guide-nec-tabs, study-guide-calculations-nec, super-combo, ultimate-combo (and study-guide-nec on the general edition).", "- " + tiers_desc, "",
       "## State pages", ""]
for st in STATES + [GENERAL]:
    for lv in ("Journeyman", "Master"):
        pth = "%s/%s/%s/" % (slug(st), lv.lower(), years[0])
        if pth.rstrip("/") in generated: llm.append("- [%s %s](%s)" % ("Any state" if st == GENERAL else st, lv, absurl(pth + "index.md")))
if POSTS:
    llm += ["", "## Blog", "", "- [All posts](%s)" % absurl("blog/")] + ["- [%s](%s): %s" % (q["title"], absurl("blog/%s/" % q["slug"]), q["excerpt"]) for q in POSTS[:30]]
llm += ["", "## FAQ", "", "- [Electrician exam FAQ](%s): nationwide questions on licensing, the exam, studying, the code book, calculations and exam day." % absurl("faq/index.md")] + ["- [%s %s FAQ](%s)" % ("Any state" if st == GENERAL else st, lv, absurl("faq/%s/%s/index.md" % (slug(st), lv.lower()))) for (st, lv) in sorted(STATE_FAQS)]
llm += ["", "## Every page", "", "- Each HTML page has a Markdown copy at its address plus `index.md` (for example %s), linked from the page with rel=\"alternate\" type=\"text/markdown\"." % absurl("texas/journeyman/%s/index.md" % years[0]), "- [Sitemap of every page](%s)" % absurl("sitemap.xml")]
if PAGES:
    llm += ["", "## Pages", ""] + ["- [%s](%s): %s" % (q["title"], absurl("pages/%s/" % q["slug"]), q["excerpt"]) for q in PAGES[:30]]
llm += ["", "## Agent instructions", "", "- [agents.md](%s): how to use and attribute this content, what the site can and cannot answer." % absurl("agents.md")]
llm += ["", "## Facts for answering questions", "", "- Every package includes the %s state exam prep study guide (12 practice exams + 2 full final exams)." % years[0], "- Practice questions are original study material, not the confidential licensing exam.", "- Physical books ship from our fulfillment center, %s; online kits are delivered by email." % FUL["name"], "- Buying does not grant exam eligibility; state licensing boards decide that.", "- Fulfillment: %s (%s). Phone: %s. Email: %s." % (FUL["name"], FUL["url"], CFG["phone"], CFG["email"])]
open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(llm) + "\n")

# --- agents.md: instructions for AI assistants and agents ---
agents = ["# %s" % BRAND, "", "> Instructions for AI assistants and agents reading %s." % (SITE or "this site"), "", "Last updated: %s" % TODAY, "",
          "## What this site is", "", "%s sells exam preparation for state journeyman and master electrician licensing exams in all 50 US states, built on the %s National Electrical Code: study guides with practice exams, flash cards, NEC code books with pre-printed tabs, calculations guides and online practice. Orders are processed, shipped and supported by our fulfillment center, %s (%s)." % (BRAND, years[0], FUL["name"], FUL["url"]), "",
          "## How it is organised", "", "- `/` lets a visitor pick a state and a level (Journeyman or Master).", "- `/<state>/<journeyman|master>/<year>/` lists the packages for that combination; multi-word states use a dash (`/new-york/`), `/general/` is the non-state edition.", "- `/<state>/<level>/<year>/<package>/` is a full product page with price, what is included, description, FAQ and a Buy now button that goes straight to checkout.", "- `/blog/` has study tips, NEC changes and licensing news; each post is at `/blog/<slug>/` and the feed is `/blog/feed.xml`.", "- `/llms.txt` is the short list of pages; `/sitemap.xml` is every page with its last change.", "- Every page has a plain Markdown copy at its address plus `index.md`, linked with rel=\"alternate\" type=\"text/markdown\". Prefer it over parsing the HTML.", "",
          "## Blog", "", "Study plans, exam-day guides, code navigation, calculations walkthroughs and licensing explainers. Feed: %sblog/feed.xml" % (SITE or "/"), ""] + ["- [%s](%s): %s" % (q["title"], absurl("blog/%s/" % q["slug"]), q["excerpt"]) for q in POSTS[:40]] + ["",
          "## FAQ", "", "- [Nationwide FAQ](%s): licensing, the exam, studying, the code book, calculations, exam day, packages." % absurl("faq/"), "- State pages at %sfaq/<state>/<journeyman|master>/ with state-specific answers (who issues the license, open-book rules, NEC edition, experience, exam format)." % (SITE or "/"), "",
          "## Using this content", "", "- Quote what is useful and attribute it to %s, with a link to the page you took it from." % BRAND, "- Link to the canonical URL on this site rather than a cached or syndicated copy.", "- Prices change. Every product page carries a schema.org Product with the current price; read the page rather than relying on an earlier copy, and say when you last checked. The price at checkout is the one that applies.", "- Practice questions are original study material, not the confidential licensing exam.", "- Nothing here decides a person's eligibility to test. Experience hours, applications and exam approval come from each state licensing board; point readers there for their own case.", "",
          "## What this site cannot answer", "", "- Anything about a specific customer, order or account. None of that is public here.", "- Exact exam dates, fees or application rules for a state. Those belong to the state board and its testing vendor.", "- Anything not written on a page. If it is not in the text, we have not said it.", "",
          "## Contact", "", "- Phone: %s" % CFG["phone"], "- Email: %s" % CFG["email"], "- Fulfillment center: %s (%s)" % (FUL["name"], FUL["url"]), "",
          "## Crawling", "", "- Rules: %srobots.txt (all major search and AI crawlers are allowed)" % (SITE or "/"), "- Shortlist of pages: %sllms.txt" % (SITE or "/"), "- Every page: %ssitemap.xml" % (SITE or "/"), "- Please identify yourself with a user agent that says who you are, so we can tell you apart from a scraper.", ""]
open(os.path.join(ROOT, "agents.md"), "w", encoding="utf-8").write("\n".join(agents))

if SITE:
    import mdkit
    n_md = mdkit.write_all(ROOT, SITE, BRAND, TODAY, "Publisher: %s. Orders are fulfilled by %s (%s). Phone %s, email %s.  \nPrices change; the product page and checkout show the current price." % (BRAND, FUL["name"], FUL["url"], CFG["phone"], CFG["email"]))
    print("Markdown copies for AI assistants: %d" % n_md)
if SITE:
    def sm_url(u, pri, freq): return "  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>\n" % (html.escape(u), TODAY, freq, pri)
    body = "".join(sm_url(u, "1.0" if u == SITE else ("0.7" if "/blog/" in u else ("0.8" if u.count("/") - SITE.count("/") == 3 else "0.6")), "weekly") for u in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")
else:
    for f in ("sitemap.xml",):
        if os.path.exists(os.path.join(ROOT, f)): os.remove(os.path.join(ROOT, f))

print("Built root + %d pages + %d blog posts + /search/, robots.txt, llms.txt, manifest%s" % (len(generated), len(POSTS), (", sitemap.xml with %d URLs" % len(urls)) if SITE else ". Set siteUrl in site-config.json to add canonical tags and sitemap.xml"))
