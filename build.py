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
import datetime
TODAY = datetime.date.today().isoformat()
sys.path.insert(0, os.path.join(ROOT, "tools")); import blogkit
POSTS = blogkit.load_posts(os.path.join(ROOT, "content", "posts"))

def absurl(path):  # path like "texas/master/2026/" -> absolute when the site URL is known, else relative to root
    return (SITE + path) if SITE else "/" + path
def ld(obj): return '<script type="application/ld+json">%s</script>\n' % json.dumps(obj, ensure_ascii=False)
def org_ld():
    o = {"@context": "https://schema.org", "@type": "Organization", "name": BRAND, "legalName": CFG.get("legalName", BRAND), "url": SITE or CFG["storeUrl"],
         "logo": CFG.get("logo"), "telephone": CFG.get("phoneTel"), "email": CFG.get("email"),
         "sameAs": [v for v in CFG.get("social", {}).values() if v],
         "contactPoint": [{"@type": "ContactPoint", "telephone": CFG.get("phoneTel"), "contactType": "sales", "areaServed": "US", "availableLanguage": "English"}]}
    return {k: v for k, v in o.items() if v}
def website_ld():
    w = {"@context": "https://schema.org", "@type": "WebSite", "name": BRAND + " Electrician Exam Prep", "url": SITE or "/",
         "potentialAction": {"@type": "SearchAction", "target": {"@type": "EntryPoint", "urlTemplate": absurl("search/?q={search_term_string}")}, "query-input": "required name=search_term_string"}}
    return w
def crumbs_ld(items):  # [(name, path)]
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement": [{"@type": "ListItem", "position": i + 1, "name": n, "item": absurl(pth)} for i, (n, pth) in enumerate(items)]}
def faq_ld(pairs):
    return {"@context": "https://schema.org", "@type": "FAQPage", "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": a}} for q, a in pairs]}
LISTING_FAQ = [("Which NEC edition are these based on?", "Every product in this collection is built on the %s National Electrical Code. If your state is still testing on the 2023 or 2020 NEC, check your candidate bulletin first; 1examprep.com also carries earlier editions."),
               ("Are these the actual exam questions?", "No. Real exam questions are confidential. These are practice questions written to the same subjects, format and difficulty, with explanations."),
               ("What's the difference between Journeyman and Master?", "Journeyman guides cover the journeyman-level exam; Master guides go deeper on calculations, planning and supervision topics for the master or contractor exam. Pick the license you are applying for."),
               ("When will I get it?", "Online test success kits and courses are delivered by email after purchase. Books and code books ship from 1 Exam Prep; shipping options are shown at checkout."),
               ("Does buying make me eligible to test?", "No. Eligibility, experience hours and exam approval come from your state licensing board. These materials get you ready for the test itself.")]
PRODUCT_FAQ = [("Which NEC edition is this based on?", "The %s National Electrical Code. If your state is still testing on an earlier edition, check your candidate bulletin first; 1examprep.com also carries earlier editions."),
               ("Are these the actual exam questions?", "No. Real exam questions are confidential. These are practice questions written to the same subjects, format and difficulty, with explanations."),
               ("When will I get it?", "Online kits and courses are delivered by email after purchase. Books and code books ship from 1 Exam Prep; shipping options are shown at checkout."),
               ("Does buying make me eligible to test?", "No. Eligibility, experience hours and exam approval come from your state licensing board. This package gets you ready for the test itself.")]

def head_extra(path, title, desc, image, rel, noindex=False, extra_ld=()):
    url = absurl(path) if SITE else None
    h = ['<meta name="robots" content="%s">' % ("noindex, nofollow" if noindex else "index, follow, max-image-preview:large")]
    if url: h.append('<meta property="og:url" content="%s">' % html.escape(url))
    h.append('<meta property="og:site_name" content="%s">' % html.escape(BRAND)); h.append('<meta property="og:locale" content="en_US">')
    h.append('<meta name="twitter:card" content="summary_large_image">'); h.append('<meta name="twitter:title" content="%s">' % html.escape(title)); h.append('<meta name="twitter:description" content="%s">' % html.escape(desc))
    if image: h.append('<meta name="twitter:image" content="%s">' % html.escape(image))
    if CFG.get("social", {}).get("twitter"): h.append('<meta name="twitter:site" content="@%s">' % CFG["social"]["twitter"].rstrip("/").split("/")[-1])
    h.append('<meta name="theme-color" content="#1b1f3b">')
    h.append('<link rel="icon" href="%sshared/favicon.svg" type="image/svg+xml">' % rel); h.append('<link rel="apple-touch-icon" href="%sshared/apple-touch-icon.png">' % rel); h.append('<link rel="manifest" href="%smanifest.webmanifest">' % rel)
    if CFG.get("googleSiteVerification"): h.append('<meta name="google-site-verification" content="%s">' % html.escape(CFG["googleSiteVerification"]))
    if CFG.get("gtagId"): h.append('<script async src="https://www.googletagmanager.com/gtag/js?id=%s"></script><script>window.dataLayer=window.dataLayer||[];function gtag(){dataLayer.push(arguments);}gtag("js",new Date());gtag("config","%s",{"send_page_view":true});</script>' % (CFG["gtagId"], CFG["gtagId"]))
    if CFG.get("gtmId"): h.append("<script>(function(w,d,s,l,i){w[l]=w[l]||[];w[l].push({'gtm.start':new Date().getTime(),event:'gtm.js'});var f=d.getElementsByTagName(s)[0],j=d.createElement(s);j.async=true;j.src='https://www.googletagmanager.com/gtm.js?id='+i;f.parentNode.insertBefore(j,f);})(window,document,'script','dataLayer','%s');</script>" % CFG["gtmId"])
    if CFG.get("metaPixelId"): h.append("<script>!function(f,b,e,v,n,t,s){if(f.fbq)return;n=f.fbq=function(){n.callMethod?n.callMethod.apply(n,arguments):n.queue.push(arguments)};if(!f._fbq)f._fbq=n;n.push=n;n.loaded=!0;n.version='2.0';n.queue=[];t=b.createElement(e);t.async=!0;t.src=v;s=b.getElementsByTagName(e)[0];s.parentNode.insertBefore(t,s)}(window,document,'script','https://connect.facebook.net/en_US/fbevents.js');fbq('init','%s');fbq('track','PageView');</script>" % CFG["metaPixelId"])
    if CFG.get("dashboardUrl") and CFG.get("siteKey"): h.append('<script>window.__dashCustom=true;</script><script src="%s/t.js" data-site="%s" defer></script>' % (html.escape(CFG["dashboardUrl"].rstrip("/")), html.escape(CFG["siteKey"])))
    for o in extra_ld: h.append(ld(o).rstrip())
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
            '<div><a class="brand" href="%s">1 <span>Exam</span> Prep</a><p>%s</p><p class="contact"><a href="tel:%s">%s</a><a href="mailto:%s">%s</a></p></div>'
            '<nav aria-label="Popular states"><h2>Popular states</h2><ul>%s<li><a href="%s">All 50 states</a></li></ul></nav>'
            '<nav aria-label="Shop"><h2>Shop</h2><ul><li><a href="%s#packs">Packages</a></li><li><a href="%s#compare">Compare packages</a></li><li><a href="%s#singles">Study guides &amp; flash cards</a></li><li><a href="%sblog/">Blog</a></li><li><a href="%ssearch/">Search</a></li><li><a href="%s" rel="noopener" target="_blank">1examprep.com</a></li></ul></nav>'
            '<nav aria-label="Follow"><h2>Follow</h2><ul>%s</ul></nav></div>'
            '<p class="fine"><strong>%s</strong> &copy; <span data-year>%s</span> &middot; <a href="%s">1examprep.com</a>. Prices and availability pulled from the 1 Exam Prep store; the price at checkout is the one that applies. Not affiliated with any state licensing board or testing vendor. Purchasing does not grant exam eligibility or a license.</p></div></footer>'
            % (rel or "./", html.escape(CFG.get("tagline", "")), CFG["phoneTel"], html.escape(CFG["phone"]), CFG["email"], CFG["email"], quick, rel or "./", rel or "./", rel or "./", rel or "./", rel, rel, CFG["storeUrl"], soc, html.escape(BRAND), TODAY[:4], CFG["storeUrl"]))

def slug(state): return "general" if state == GENERAL else state.lower().replace(" ", "-")
def words(text):
    out = []
    for i, w in enumerate(text.split()):
        hl = w.startswith("*"); w = w.lstrip("*")
        out.append('<span class="w%s" style="--n:%d">%s</span>' % (" hl" if hl else "", i, html.escape(w)))
    return " ".join(out)

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
    if crumbs: lds.append(crumbs_ld(crumbs))
    out = (tpl.replace("{{ASSETS_HEAD}}", assets_head).replace("{{ASSETS_CATALOG}}", assets_cat).replace("{{ASSETS_APP}}", assets_app)
           .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel))
           .replace("{{HEAD_EXTRA}}", head_extra(path, title, desc, og_image, rel, noindex, lds))
           .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="#packs">Pick my package</a>'))
           .replace("{{FOOTER}}", footer(rel, sorted({p["year"] for p in CATALOG}, reverse=True)[0]))
           .replace("{{TITLE}}", html.escape(title)).replace("{{DESC}}", html.escape(desc))
           .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % url) if url else "")
           .replace("{{OGIMAGE}}", ('<meta property="og:image" content="%s">\n' % html.escape(og_image)) if og_image else "")
           .replace("{{REL}}", rel).replace("{{HOME}}", rel if rel else "./")
           .replace("{{H1_TEXT}}", html.escape(h1.replace("*", ""))).replace("{{H1_HTML}}", words(h1))
           .replace("{{LEAD}}", html.escape(lead)).replace("{{ROUTE}}", json.dumps(route)))
    d = os.path.join(ROOT, *path_parts) if path_parts else ROOT
    os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f: f.write(out)
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
    imgs = full["images"] or [p["image"]]
    v0 = p["variants"][0]
    c, n = float(v0.get("compareAt") or 0), float(v0["price"])
    compare_html = ('<s class="pc-was" id="pWas">%s</s><span class="pc-save" id="pSave">Save %d%%</span>' % (money(c), round((c - n) / c * 100))) if c > n else '<s class="pc-was" id="pWas" hidden></s><span class="pc-save" id="pSave" hidden></span>'
    variants_html = "".join('<label class="m-opt"><input type="radio" name="v" value="%s"%s><span>%s</span><b>%s%s</b></label>' % (
        v["id"], " checked" if i == 0 else "", html.escape(v["title"]), money(v["price"]),
        ('<s>%s</s>' % money(v["compareAt"])) if v.get("compareAt") and float(v["compareAt"]) > float(v["price"]) else "") for i, v in enumerate(p["variants"]))
    thumbs = "".join('<button type="button" data-src="%s" class="%s" aria-label="Image %d"><img src="%s" alt="" loading="lazy"></button>' % (html.escape(u), "on" if i == 0 else "", i + 1, html.escape(u)) for i, u in enumerate(imgs))
    S = "" if state_name == "any state" else state_name
    inc = "".join("<li>%s</li>" % html.escape(x.format(Y=p["year"], S=S, L=p["level"]).replace("  ", " ")) for x in INCLUDED.get(p["tier"], []))
    addons = [v["title"] for v in p["variants"][1:]]
    addons_html = ('<p class="addons"><b>Optional add-ons at checkout:</b> %s. Pick one above and the price updates.</p>' % html.escape("; ".join(addons))) if addons else ""
    related = "".join('<a class="rel" href="../%s/"><img src="%s" alt="" loading="lazy"><span><b>%s</b><small>%s</small></span><span class="pc-now">%s</span></a>' % (
        q["tierSlug"], html.escape(q["image"]), html.escape(q["tierName"]), html.escape(clean_title(q["title"])[:60] + ("…" if len(clean_title(q["title"])) > 60 else "")), money(q["price"])) for q in siblings if q["id"] != p["id"])
    desc = (p["desc"].replace(p["title"], "").strip()[:158]).rsplit(" ", 1)[0] + "…"
    path = "/".join(path_parts) + "/"
    jsonld = {"@context": "https://schema.org", "@type": "Product", "name": clean_title(p["title"]), "image": imgs[:6], "description": p["desc"].replace(p["title"], "").strip()[:500],
              "brand": {"@type": "Brand", "name": BRAND}, "sku": p["id"], "productID": p["id"], "category": "%s Electrician Exam Prep" % p["level"], "url": absurl(path),
              "offers": [{"@type": "Offer", "name": v["title"], "priceCurrency": "USD", "price": v["price"], "availability": "https://schema.org/InStock", "itemCondition": "https://schema.org/NewCondition", "url": absurl(path), "seller": {"@type": "Organization", "name": BRAND}} for v in p["variants"]]}
    crumbs = [("All states", ""), (state_name.capitalize() if state_name == "any state" else state_name, "/".join(path_parts[:3]) + "/"), (p["level"], "/".join(path_parts[:3]) + "/"), (p["tierName"], path)]
    extra = head_extra(path, clean_title(p["title"]) + " | " + BRAND, desc, imgs[0], rel, False, [crumbs_ld(crumbs), faq_ld([(q, a % p["year"] if "%s" in a else a) for q, a in PRODUCT_FAQ])])
    pjson = json.dumps({"id": p["id"], "variants": p["variants"], "title": clean_title(p["title"]), "state": p["state"], "level": p["level"], "tierName": p["tierName"], "price": p["price"]})
    assets_head = '<link rel="stylesheet" href="%sshared/base.css">\n<link rel="stylesheet" href="%sshared/store.css">' % (rel, rel)
    out = (ptpl.replace("{{TITLE}}", html.escape(clean_title(p["title"]) + " | 1 Exam Prep")).replace("{{DESC}}", html.escape(desc))
           .replace("{{CANONICAL}}", ('<link rel="canonical" href="%s">\n' % url) if url else "")
           .replace("{{OGIMAGE}}", '<meta property="og:image" content="%s">\n' % html.escape(imgs[0]))
           .replace("{{ASSETS_HEAD}}", assets_head).replace("{{ASSETS_PRODUCT}}", '<script src="%sshared/product.js"></script>' % rel)
           .replace("{{ASSETS_SEARCH}}", '<script src="%sshared/search.js" defer></script>\n<script src="%sshared/track.js" defer></script>' % (rel, rel)).replace("{{HEAD_EXTRA}}", extra)
           .replace("{{NAV_TOOLS}}", nav_tools('<a class="btn btn-buy" href="%s" rel="noopener">Buy now</a>' % ("https://1examprep.com/cart/%s:1" % v0["id"])))
           .replace("{{FOOTER}}", footer(rel, p["year"])).replace("{{ROUTE}}", json.dumps({"state": path_parts[0], "level": p["level"], "year": p["year"], "tier": p["tierSlug"], "depth": depth}))
           .replace("{{JSONLD}}", json.dumps(jsonld, ensure_ascii=False)).replace("{{P_JSON}}", pjson)
           .replace("{{HOME}}", rel).replace("{{LEVEL_URL}}", "../").replace("{{OTHER_LEVEL_URL}}", other_level_url).replace("{{OTHER_LEVEL}}", other_level)
           .replace("{{STATE}}", html.escape(state_name.capitalize() if state_name == "any state" else state_name)).replace("{{LEVEL}}", p["level"]).replace("{{YEAR}}", p["year"])
           .replace("{{TIER_NAME}}", html.escape(p["tierName"])).replace("{{H1}}", html.escape(clean_title(p["title"])))
           .replace("{{IMAGE}}", html.escape(imgs[0])).replace("{{THUMBS}}", thumbs if len(imgs) > 1 else "")
           .replace("{{PRICE}}", money(v0["price"])).replace("{{COMPARE_HTML}}", compare_html).replace("{{VARIANTS_HTML}}", variants_html)
           .replace("{{BUY_URL}}", "https://1examprep.com/cart/%s:1" % v0["id"]).replace("{{SHOP_URL}}", html.escape(p["url"]))
           .replace("{{INCLUDED_HTML}}", inc).replace("{{ADDONS_HTML}}", addons_html).replace("{{DESCRIPTION_HTML}}", full["html"]).replace("{{RELATED_HTML}}", related))
    d = os.path.join(ROOT, *path_parts); os.makedirs(d, exist_ok=True)
    with open(os.path.join(d, "index.html"), "w", encoding="utf-8") as f: f.write(out)
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
         "%s Electrician Exam Prep for All 50 States | 1 Exam Prep" % years[0],
         "%s journeyman and master electrician exam prep for all 50 states. Pick your state, pick your level, pick a package. Study guides, flash cards, NEC code books with tabs, calculations guides and online practice." % years[0],
         "Your state. *Your *license. %s code." % years[0],
         "Journeyman and master electrician exam prep for all 50 states, built on the %s National Electrical Code. Pick your state and level, then choose how much help you want." % years[0],
         CFG.get("logo"), extra_ld=[org_ld(), website_ld(), faq_ld([(q, a % years[0] if "%s" in a else a) for q, a in LISTING_FAQ])])
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
                     "%s %s %s Electrician Exam Prep (%s NEC) | 1 Exam Prep" % (year, "" if st is None else state, level, year),
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
</script></head><body><p>Taking you to the right page…</p></body></html>""" % (json.dumps(sorted(state_slugs)), json.dumps(years))
open(os.path.join(ROOT, "404.html"), "w", encoding="utf-8").write(nf)

# --- /search/ page (also the target of the schema.org SearchAction) ---
search_body = ('<main id="main" class="wrap search-page"><h1 id="h1">Search</h1><form id="searchPage" class="srch-form" role="search"><input class="srch-q" name="q" type="search" placeholder="State, package or product\u2026" aria-label="Search" autocomplete="off"><button class="btn btn-buy" type="submit">Search</button></form><div id="searchOut"></div></main>')
sp = tpl[:tpl.index("<body>")]
sp = (sp.replace("{{ASSETS_HEAD}}", '<link rel="stylesheet" href="../shared/base.css">\n<link rel="stylesheet" href="../shared/store.css">').replace("{{TITLE}}", "Search | " + BRAND).replace("{{DESC}}", "Search %s electrician exam prep packages by state, level or product." % BRAND)
      .replace("{{CANONICAL}}", "").replace("{{OGIMAGE}}", "").replace("{{HEAD_EXTRA}}", head_extra("search/", "Search | " + BRAND, "Search electrician exam prep packages.", CFG.get("logo"), "../", noindex=True)))
sp += ('<body><a class="skip" href="#main">Skip to content</a><header class="nav"><div class="wrap"><a class="brand" href="../" id="homeLink">1 <span>Exam</span> Prep</a>' + nav_tools('<a class="btn btn-buy" href="../#packs">Pick my package</a>') + '</div></header>'
       + search_body + footer("../", years[0]) + '<script>window.ROUTE={"depth":1};</script><script src="../shared/catalog.js"></script><script src="../shared/search.js"></script><script src="../shared/track.js"></script></body></html>')
os.makedirs(os.path.join(ROOT, "search"), exist_ok=True); open(os.path.join(ROOT, "search", "index.html"), "w", encoding="utf-8").write(sp)

# --- /admin/ dashboard (noindex; analytics needs Google sign-in) ---
atpl = open(os.path.join(ROOT, "store", "admin.html"), encoding="utf-8").read()
admin_cfg = {"gtagId": CFG.get("gtagId", ""), "ga4PropertyId": CFG.get("ga4PropertyId", ""), "googleOAuthClientId": CFG.get("googleOAuthClientId", ""), "repo": CFG.get("repo", ""), "siteUrl": SITE or ""}
os.makedirs(os.path.join(ROOT, "admin"), exist_ok=True)
open(os.path.join(ROOT, "admin", "index.html"), "w", encoding="utf-8").write(atpl.replace("{{ADMIN_JSON}}", json.dumps(admin_cfg)))

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
    title = ("%s | Blog | %s" % (tag.title(), BRAND)) if tag else ("Electrician Exam Prep Blog: Study Tips, NEC Changes & Licensing News | %s" % BRAND)
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
    out = blog_common(bitpl, rel, path, title, desc, (feat or {}).get("image") or CFG.get("logo"), lds, {"depth": len(dest_parts), "blog": True})
    out = out.replace("{{H1}}", html.escape(h1)).replace("{{LEAD}}", html.escape(lead)).replace("{{TAG_FILTER}}", tagf).replace("{{FEATURED_HTML}}", feat_html).replace("{{CARDS_HTML}}", cards).replace("{{EMPTY_HTML}}", empty)
    d = os.path.join(ROOT, *dest_parts); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
    if SITE: urls.append(absurl(path))
blog_index(["blog"], POSTS)
for t in all_tags: blog_index(["blog", "tag", blogkit.slugify(t)], [q for q in POSTS if t in q["tags"]], t)
from urllib.parse import quote
for q in POSTS:
    parts = ["blog", q["slug"]]; rel = "../../"; path = "blog/%s/" % q["slug"]; url = absurl(path)
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
    out = blog_common(btpl, rel, path, "%s | %s" % (q["title"], BRAND), q["excerpt"], q["image"] or CFG.get("logo"), lds, {"depth": 2, "blog": True, "post": q["slug"]})
    out = (out.replace("{{H1}}", html.escape(q["title"])).replace("{{TITLE_SHORT}}", html.escape(q["title"][:60] + ("…" if len(q["title"]) > 60 else ""))).replace("{{EXCERPT}}", html.escape(q["excerpt"]))
           .replace("{{DATE}}", q["date"]).replace("{{UPDATED}}", q["updated"]).replace("{{DATE_NICE}}", nice_date(q["date"])).replace("{{AUTHOR_HTML}}", ('<span>%s</span>' % html.escape(q["author"])) if q["author"] else "")
           .replace("{{READ_MIN}}", str(max(1, round(q["words"] / 220)))).replace("{{TAGS_HTML}}", tags_html).replace("{{HERO_HTML}}", hero).replace("{{BODY_HTML}}", q["html"])
           .replace("{{URL_ENC}}", quote(url, safe="")).replace("{{TITLE_ENC}}", quote(q["title"], safe="")).replace("{{MORE_LINK}}", more_link)
           .replace("{{CTA_KICKER}}", html.escape(cta_kicker)).replace("{{CTA_TITLE}}", html.escape(cta_title)).replace("{{CTA_TEXT}}", html.escape(cta_text)).replace("{{CTA_URL}}", cta_url).replace("{{CTA_LABEL}}", html.escape(cta_label))
           .replace("{{RELATED_HTML}}", rel_html))
    d = os.path.join(ROOT, *parts); os.makedirs(d, exist_ok=True); open(os.path.join(d, "index.html"), "w", encoding="utf-8").write(out)
    if SITE: urls.append(url)
# RSS feed
feed_items = "".join("<item><title>%s</title><link>%s</link><guid isPermaLink=\"true\">%s</guid><pubDate>%s</pubDate><description>%s</description>%s</item>\n" % (
    html.escape(q["title"]), absurl("blog/%s/" % q["slug"]), absurl("blog/%s/" % q["slug"]), datetime.datetime.fromisoformat(q["date"][:10]).strftime("%a, %d %b %Y 09:00:00 -0500"), html.escape(q["excerpt"]),
    ("<enclosure url=\"%s\" type=\"image/jpeg\" length=\"0\"/>" % html.escape(q["image"])) if q["image"] else "") for q in POSTS[:30])
open(os.path.join(blog_dir, "feed.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<rss version="2.0"><channel><title>%s Blog</title><link>%s</link><description>Electrician exam prep study tips, NEC changes and licensing news.</description><language>en-us</language>\n%s</channel></rss>\n' % (html.escape(BRAND), absurl("blog/"), feed_items))
open(os.path.join(blog_dir, "posts.json"), "w", encoding="utf-8").write(json.dumps([{k: q[k] for k in ("slug", "title", "date", "updated", "excerpt", "image", "tags", "state", "level", "author", "words")} for q in POSTS], ensure_ascii=False))

# --- icons + manifest ---
fav = '<svg xmlns="http://www.w3.org/2000/svg" viewBox="0 0 64 64"><rect width="64" height="64" rx="14" fill="#ff5a1f"/><path d="M36 14v36h-9V24l-8 5v-9l10-6z" fill="#fff"/></svg>'
open(os.path.join(ROOT, "shared", "favicon.svg"), "w").write(fav)
try:
    from PIL import Image, ImageDraw
    im = Image.new("RGBA", (180, 180), (255, 90, 31, 255)); dr = ImageDraw.Draw(im)
    dr.polygon([(101, 40), (101, 140), (76, 140), (76, 68), (54, 82), (54, 57), (82, 40)], fill="white")
    im.save(os.path.join(ROOT, "shared", "apple-touch-icon.png"))
except Exception as e: print("apple-touch-icon skipped:", e)
open(os.path.join(ROOT, "manifest.webmanifest"), "w").write(json.dumps({"name": BRAND + " Electrician Exam Prep", "short_name": BRAND, "start_url": "./", "display": "browser", "background_color": "#f7f6f2", "theme_color": "#1b1f3b", "icons": [{"src": "shared/apple-touch-icon.png", "sizes": "180x180", "type": "image/png"}, {"src": "shared/favicon.svg", "sizes": "any", "type": "image/svg+xml"}]}, indent=1))

# --- robots.txt (AI crawlers explicitly welcome) + llms.txt ---
bots = ["GPTBot", "ChatGPT-User", "OAI-SearchBot", "ClaudeBot", "Claude-User", "anthropic-ai", "PerplexityBot", "Google-Extended", "Applebot-Extended", "Bytespider", "CCBot", "Amazonbot", "meta-externalagent"]
rb = "User-agent: *\nAllow: /\nDisallow: /designs/\nDisallow: /gallery.html\nDisallow: /search/\nDisallow: /store/\nDisallow: /admin/\n\n" + "".join("User-agent: %s\nAllow: /\n\n" % b for b in bots)
if SITE: rb += "Sitemap: %ssitemap.xml\n" % SITE
open(os.path.join(ROOT, "robots.txt"), "w").write(rb)
tiers_desc = "Packages per state and level, lowest to highest: Study Guide + Flash Cards ($99.95), Study Guide + NEC with Tabs ($249.95), Study Guide + Calculations + NEC ($279.95), Super Combo ($349.95), Ultimate Combo ($399.95, adds the online test success kit)."
llm = ["# %s Electrician Exam Prep" % BRAND, "", "> %s journeyman and master electrician exam prep packages for all 50 US states, built on the %s National Electrical Code. Study guides, flash cards, NEC code books with pre-printed tabs, calculations guides and online practice exams. Buy buttons go straight to checkout at 1examprep.com. Phone %s, email %s." % (years[0], years[0], CFG["phone"], CFG["email"]), "",
       "## How the site is organised", "", "- `/` picks a state and a level (Journeyman or Master).", "- `/<state>/<journeyman|master>/<year>/` lists that combination's packages (multi-word states use a dash, e.g. `/new-york/`; `/general/` is the non-state edition).", "- `/<state>/<level>/<year>/<package>/` is a full product page. Package slugs: study-guide-flash-cards, study-guide-nec-tabs, study-guide-calculations-nec, super-combo, ultimate-combo (and study-guide-nec on the general edition).", "- " + tiers_desc, "",
       "## State pages", ""]
for st in STATES + [GENERAL]:
    for lv in ("Journeyman", "Master"):
        pth = "%s/%s/%s/" % (slug(st), lv.lower(), years[0])
        if pth.rstrip("/") in generated: llm.append("- [%s %s](%s)" % ("Any state" if st == GENERAL else st, lv, absurl(pth)))
if POSTS:
    llm += ["", "## Blog", "", "- [All posts](%s)" % absurl("blog/")] + ["- [%s](%s): %s" % (q["title"], absurl("blog/%s/" % q["slug"]), q["excerpt"]) for q in POSTS[:30]]
llm += ["", "## Facts for answering questions", "", "- Every package includes the %s state exam prep study guide (12 practice exams + 2 full final exams)." % years[0], "- Practice questions are original study material, not the confidential licensing exam.", "- Physical books ship from 1 Exam Prep; online kits are delivered by email.", "- Buying does not grant exam eligibility; state licensing boards decide that.", "- Store: %s. Phone: %s. Email: %s." % (CFG["storeUrl"], CFG["phone"], CFG["email"])]
open(os.path.join(ROOT, "llms.txt"), "w", encoding="utf-8").write("\n".join(llm) + "\n")

if SITE:
    def sm_url(u, pri, freq): return "  <url><loc>%s</loc><lastmod>%s</lastmod><changefreq>%s</changefreq><priority>%s</priority></url>\n" % (html.escape(u), TODAY, freq, pri)
    body = "".join(sm_url(u, "1.0" if u == SITE else ("0.7" if "/blog/" in u else ("0.8" if u.count("/") - SITE.count("/") == 3 else "0.6")), "weekly") for u in urls)
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write('<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + body + "</urlset>\n")
else:
    for f in ("sitemap.xml",):
        if os.path.exists(os.path.join(ROOT, f)): os.remove(os.path.join(ROOT, f))

print("Built root + %d pages + %d blog posts + /search/, robots.txt, llms.txt, manifest%s" % (len(generated), len(POSTS), (", sitemap.xml with %d URLs" % len(urls)) if SITE else ". Set siteUrl in site-config.json to add canonical tags and sitemap.xml"))
