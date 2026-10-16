# 1 Exam Prep electrician landing pages

## The live product page (start here)

`index.html` is now the **1 Exam Prep product page**: the Scoreboard design (#3)
wired to your real Shopify catalog. It covers the whole "2026 Electrician Exam
Prep" collection (522 products pulled from 1examprep.com on 2026-10-16).

- Visitor picks a state (or "General (any state)") and Journeyman / Master.
- The page shows that combination's packages in price order: Study Guide +
  Flash Cards $99.95 → NEC with Tabs $249.95 → + Calculations $279.95 →
  Super Combo $349.95 → Ultimate Combo $399.95.
- **Buy now** uses a Shopify cart permalink (`1examprep.com/cart/VARIANT:1`) so
  the item is added and the shopper lands on your checkout in one click.
- **What's inside** opens the description, the add-on variants (online course,
  flash cards, instructor videos) with live prices, and a link to the full
  product page on 1examprep.com.
- Links like `#texas-master` or `#florida-journeyman` open the page already set
  to that state and level. Handy for ads and emails.
- Every product's image, title, description excerpt, price, compare-at price and
  variant IDs live in `shared/catalog.js`. Do not hand-edit it; when prices or
  products change, ask for a refresh and it is regenerated from Shopify.

Source file is `store/index.html`; `./make-homepage.sh store` copies it to
`index.html`. The ten template designs are still in `designs/` and previewable
from `gallery.html`.

Two catalog notes found while building it: Massachusetts Journeyman and
Minnesota Journeyman each have a duplicate "Study Guide + NEC with Tabs" listing
(handle ends in `-1`, $249.95) where the "+ Calculations" package ($279.95) is
for every other state, and the Pennsylvania Journeyman Ultimate Combo "+ Videos" variant
shows a compare-at price ($495) lower than its price ($499.95). The page hides
the duplicates; the compare-at is shown as Shopify has it.

---

# Template landing pages (designs 1–10)

Ten ready-to-host landing pages for selling master electrician exam prep packs.
Every page reads the same product list, so you edit prices, descriptions and
checkout links in **one file** and all five update.

```
electrician-site/
├── index.html            ← LIVE product page (Scoreboard design + real Shopify catalog)
├── gallery.html          ← preview of the 10 template designs
├── store/index.html      ← source of the product page
├── shared/catalog.js     ← 522 products pulled from Shopify (auto-generated)
├── designs/
│   ├── 1-livewire.html
│   ├── 2-blueprint.html
│   ├── 3-scoreboard.html
│   ├── 4-readiness.html
│   ├── 5-cobalt.html
│   ├── 6-kinetic.html      ← designs 6–10 use GSAP (loaded from a CDN) for scroll motion
│   ├── 7-storyboard.html
│   ├── 8-depth.html
│   ├── 9-signal.html
│   └── 10-glass.html
├── shared/
│   ├── products.js       ← EDIT THIS: names, prices, descriptions, checkout links
│   ├── app.js            ← renders products, detail popups, buy buttons (no edits needed)
│   └── base.css          ← shared structure (no edits needed)
├── make-homepage.sh      ← one command to turn a design into index.html
├── .nojekyll
└── CNAME.example         ← rename to CNAME when you connect your own domain
```

## 1. Add your checkout links

Open `shared/products.js`. Each product looks like this:

```js
{
  id: "master-520",
  name: "Master Study Pack",
  short: "520 questions + readiness tracker",
  price: "$74.95",
  compareAt: "",              // optional "was" price, e.g. "$89.95"
  badge: "Most popular",      // optional ribbon; "Most popular" also powers the hero Buy button
  access: "90-day access",
  description: "Long description shown in the 'What's inside' popup...",
  features: ["Bullet one", "Bullet two"],
  checkout: "PASTE_CHECKOUT_LINK_HERE"   // ← your Stripe / Shopify / PayPal / Gumroad link
}
```

Replace every `PASTE_CHECKOUT_LINK_HERE` with the real URL. Until you do, the
Buy buttons show a small reminder instead of going anywhere.

Add a product by copying a whole `{ ... }` block. Remove one by deleting it.
At the top of the same file, `SITE.brand`, `SITE.supportEmail` and
`SITE.states` fill in the brand name, support email and the states list.

How buying works on every page: **Buy now** goes straight to your checkout URL.
**What's inside** opens a popup with the full description and a bigger
Buy now button that also goes straight to checkout.

## 2. Pick a design and make it the homepage

Preview all five by opening `index.html` in a browser (or on GitHub Pages after step 3).

Then either run:

```bash
./make-homepage.sh 3        # 1–10, the design number
```

or do it by hand: copy the design file over `index.html` and change the two
`../shared/` paths inside it to `shared/`.

Compare the designs on the gallery page; one line on each:

| # | Name | Feel | Signature motion |
|---|------|------|------------------|
| 1 | Live Wire | Dark navy + hazard yellow | Current pulses running through a circuit panel |
| 2 | Blueprint | Drafting paper + cobalt ink | One-line diagram draws itself on load |
| 3 | Scoreboard | Off-white + hot orange | Headline animates word by word, spinning gauge, marquee |
| 4 | Readiness | White + forest green, serif | Live readiness-score widget cycling through sittings |
| 5 | Cobalt | Cobalt blue + lime | Interactive sample question, cursor glow, 3D tilt cards |
| 6 | Kinetic | Cool grey + violet | Giant drifting type, pinned horizontal product rail, line reveals |
| 7 | Storyboard | Plum mesh gradient + peach | Custom cursor, magnetic buttons, pinned 3-card story |
| 8 | Depth | Pale blue + tangerine | Parallax floating cards, mouse depth, scroll-scrubbed exam clock |
| 9 | Signal | White + black + signal red | Decoding headline, giant outlined scroll type, expandable list |
| 10 | Glass | Lavender/aqua mesh | Frosted bento hero, sample question, 3D cover-flow packs |

Designs 6–10 load GSAP 3.13 from cdnjs for the scroll-driven motion. They degrade
cleanly: if the CDN is blocked, the pages still render and every Buy button works,
you just lose the fancy motion. All ten respect "reduce motion" settings.

## 3. Put it on GitHub Pages

1. Create a new repository on GitHub (e.g. `masterprep-site`).
2. Upload everything in this folder (drag and drop on github.com works, or `git push`).
3. In the repo go to **Settings → Pages**. Under *Build and deployment* choose
   **Deploy from a branch**, branch `main`, folder `/ (root)`. Save.
4. After a minute your site is live at `https://YOUR-USERNAME.github.io/masterprep-site/`.

`.nojekyll` is included so GitHub serves the files exactly as they are.

## 4. Connect your own domain

1. Rename `CNAME.example` to `CNAME` and put your domain inside it on one line,
   e.g. `www.yourdomain.com`. Commit and push.
2. At your domain registrar add DNS records:
   - For `www`: a **CNAME** record pointing to `YOUR-USERNAME.github.io`
   - For the bare domain (`yourdomain.com`): four **A** records to
     `185.199.108.153`, `185.199.109.153`, `185.199.110.153`, `185.199.111.153`
3. Back in **Settings → Pages**, enter the domain under *Custom domain* and tick
   **Enforce HTTPS** once the certificate appears (can take up to an hour).

## Optional tweaks

- **Hero button product**: the hero and sticky-bar Buy buttons point at the product
  whose `badge` contains "popular". Change the badge to move it.
- **Colours and fonts**: each design's colours are the `:root` variables at the top
  of its HTML file.
- **Topic percentages** in the "What's covered" sections are plain text in each
  design file; edit them to match your bank.
- **FAQ**: plain `<details>` blocks in each file. Add your refund policy there.
- **Analytics**: paste your tag snippet before `</head>` in the design you use.

## Honesty notes baked in

The pages say the questions are original practice material, not the real exam,
and that buying does not grant eligibility or a license. Keep those lines; they
protect you and they match what the research report found about these products.
