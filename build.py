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
cat_js = open(os.path.join(ROOT, "shared", "catalog.js"), encoding="utf-8").read()
CATALOG = json.loads(cat_js[cat_js.index("window.CATALOG=") + len("window.CATALOG="):cat_js.index(";\nwindow.CATALOG_STATES")])
STATES = json.loads(cat_js[cat_js.index("window.CATALOG_STATES=") + len("window.CATALOG_STATES="):].rstrip().rstrip(";"))
TIERS = ["book-fc", "nec", "nec-tabs", "calc", "super", "ultimate"]
GENERAL = "General (any state)"

def slug(state): return "general" if state == GENERAL else state.lower().replace(" ", "-")
def words(text):
    out = []
    for i, w in enumerate(text.split()):
        hl = w.startswith("*"); w = w.lstrip("*")
        out.append('<span class="w%s" style="--n:%d">%s</span>' % (" hl" if hl else "", i, html.escape(w)))
    return " ".join(out)

def page(path_parts, route, title, desc, h1, lead, og_image=None):
    depth = len(path_parts)
    rel = "../" * depth
    url = (SITE + "/".join(path_parts) + ("/" if path_parts else "")) if SITE else None
    assets_head = '<link rel="stylesheet" href="%sshared/base.css">\n<link rel="stylesheet" href="%sshared/store.css">' % (rel, rel)
    assets_cat = '<script src="%sshared/catalog.js"></script>' % rel
    if route.get("spa"):
        boot = ("<script>window.__B=(function(){var S=%s;var parts=location.pathname.split('/').filter(Boolean);var i=-1;"
                "for(var k=0;k<parts.length;k++){if(S.indexOf(parts[k].toLowerCase())>-1){i=k;break;}}"
                "if(i<0)return location.pathname.replace(/[^\\/]*$/,'');var b='/'+parts.slice(0,i).join('/');return b==='/'?b:b+'/';})();"
                "document.write('<link rel=\"stylesheet\" href=\"'+__B+'shared/base.css\"><link rel=\"stylesheet\" href=\"'+__B+'shared/store.css\">');</script>") % json.dumps(sorted(slug(x) for x in STATES + [GENERAL]))
        assets_head = boot
        assets_cat = "<script>document.write('<script src=\"'+__B+'shared/catalog.js\"><\\/script>');</script>"
    out = (tpl.replace("{{ASSETS_HEAD}}", assets_head).replace("{{ASSETS_CATALOG}}", assets_cat)
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

# --- remove previously generated folders ---
manifest = os.path.join(ROOT, "generated-pages.txt")
if os.path.exists(manifest):
    for line in open(manifest):
        top = line.strip().split("/")[0]
        if top and os.path.isdir(os.path.join(ROOT, top)) and top not in ("shared", "designs", "store"):
            shutil.rmtree(os.path.join(ROOT, top))
generated, urls = [], []

# --- root ---
years = sorted({p["year"] for p in CATALOG}, reverse=True)
u = page([], {"state": None, "level": None, "year": None, "tier": None, "depth": 0, "spa": not STATIC},
         "%s Electrician Exam Prep for All 50 States | 1 Exam Prep" % years[0],
         "%s journeyman and master electrician exam prep for all 50 states. Pick your state, pick your level, pick a package. Study guides, flash cards, NEC code books with tabs, calculations guides and online practice." % years[0],
         "Your state. *Your *license. %s code." % years[0],
         "Journeyman and master electrician exam prep for all 50 states, built on the %s National Electrical Code. Pick your state and level, then choose how much help you want." % years[0])
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
                     uniq[-1]["image"])
            generated.append("/".join(parts)); urls.append(u) if u else None
            for p in uniq:
                pparts = parts + [p["tierSlug"]]
                r = dict(route, tier=p["tierSlug"], depth=4)
                clean = re.sub(r"\s*\(Based on the \d{4} NEC\)\s*", "", p["title"]).replace(": Trusted by 50k Electricians", "")
                u = page(pparts, r, "%s | 1 Exam Prep" % clean,
                         (p["desc"].replace(p["title"], "").strip()[:155] + "…"),
                         "%s. *%s. %s code." % ("Any state" if st is None else state, level, year),
                         "%s for %s. $%s. Buy now goes straight to checkout at 1examprep.com." % (p["tierName"], name, p["price"]), p["image"])
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

if SITE:
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n' + "".join("  <url><loc>%s</loc></url>\n" % html.escape(u) for u in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    open(os.path.join(ROOT, "robots.txt"), "w").write("User-agent: *\nAllow: /\nSitemap: %ssitemap.xml\n" % SITE)

print("Built root + %d pages%s" % (len(generated), (" and sitemap.xml with %d URLs" % len(urls)) if SITE else ""))
