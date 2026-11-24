#!/usr/bin/env python3
"""يولّد صفحات SEO ثابتة من data.json: صفحة لكل شقة، صفحة لكل منطقة، صفحتين إيجار/تمليك،
sitemap.xml و robots.txt. بيشتغل تلقائي من GitHub Actions مع أي تعديل في data.json."""
import json, os, html, shutil, re
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
BASE = os.environ.get("SITE_URL", "https://aqarak-hadayek.github.io").rstrip("/")
AREA = "حدايق الأهرام"
DEAL = {"rent": ("إيجار", "للإيجار", "جنيه / شهر"), "sale": ("تمليك", "للبيع", "جنيه")}
ZL = {"أ": "a", "ب": "b", "ج": "g", "د": "d", "هـ": "h", "ه": "h", "و": "w", "ز": "z", "ح": "7", "ط": "t",
      "ي": "y", "ك": "k", "ل": "l", "م": "m", "ن": "n", "س": "s", "ع": "3", "ف": "f", "ص": "s2", "ق": "q", "ر": "r"}
FIN = {"new": "أول سكن", "used": "تاني سكن"}
e = html.escape

d = json.load(open(os.path.join(ROOT, "data.json"), encoding="utf-8"))
S = d.get("site", {})
NAME = S.get("name", "عقارك")
PH = re.sub(r"\D", "", S.get("phone", ""))
if PH.startswith("20"): PH = "0" + PH[2:]
WA = "2" + PH
APTS = [a for a in d.get("listings", []) if not a.get("hidden")]
TODAY = date.today().isoformat()

def money(n): return f"{int(n):,}" if n else "السعر عند التواصل"
def zslug(z): return "zone-" + ZL.get(z.replace("منطقة", "").strip(), re.sub(r"\W", "", z)) if z else None
def title(a):
    t = a.get("kind") or "شقة"
    if a.get("area"): t += f" {a['area']} متر"
    if a.get("rooms"): t += f"، {a['rooms']} غرف"
    return t
def floor(f):
    if f is None: return None
    return "أرضي" if f == 0 else f"الدور {f}"
def url(p): return f"{BASE}/{p}"
def img(p): return url(p) if p else url("og.jpg")

CSS = """:root{--bg:#f6f6f3;--s:#fff;--i:#141a21;--m:#69727d;--l:#e6e4de;--b:#12324a;--wa:#17874a}
*{box-sizing:border-box}body{margin:0;background:var(--bg);color:var(--i);font:16px/1.7 system-ui,-apple-system,"Segoe UI","Noto Sans Arabic",Tahoma,sans-serif}
a{color:var(--b)}.w{max-width:1000px;margin:auto;padding:16px}header{background:var(--s);border-bottom:1px solid var(--l)}
header .w{display:flex;gap:16px;align-items:center;padding:12px 16px}header b{font-size:1.2rem;margin-inline-end:auto}header a{text-decoration:none}
h1{font-size:1.5rem;line-height:1.4;margin:8px 0}.crumb{font-size:.85rem;color:var(--m)}.price{font-size:1.4rem;font-weight:700;color:var(--b)}
.gal{display:flex;gap:8px;overflow-x:auto;scroll-snap-type:x mandatory;border-radius:12px}.gal img{height:300px;width:auto;max-width:90vw;object-fit:cover;scroll-snap-align:start;border-radius:12px;background:#ddd}
table{border-collapse:collapse;width:100%;background:var(--s);border-radius:12px;overflow:hidden}td{padding:10px 14px;border-bottom:1px solid var(--l)}td:first-child{color:var(--m);width:40%}
.btns{display:flex;gap:10px;flex-wrap:wrap;margin:16px 0}.btn{padding:12px 20px;border-radius:10px;background:var(--b);color:#fff;text-decoration:none;font-weight:600}.btn.wa{background:var(--wa)}
.grid{display:grid;grid-template-columns:repeat(auto-fill,minmax(230px,1fr));gap:14px}.card{background:var(--s);border:1px solid var(--l);border-radius:12px;overflow:hidden;text-decoration:none;color:inherit}
.card img{width:100%;height:160px;object-fit:cover;display:block;background:#ddd}.card div{padding:10px 12px}.card small{color:var(--m)}
footer{border-top:1px solid var(--l);margin-top:32px;color:var(--m);font-size:.9rem}ul.f{columns:2;padding-inline-start:20px}"""

def page(path, ttl, desc, body, ld, image=None, canon_app=None):
    canon = url(path)
    ldj = "".join(f'<script type="application/ld+json">{json.dumps(x, ensure_ascii=False)}</script>' for x in ld)
    links = " · ".join(f'<a href="{BASE}/{p}/">{n}</a>' for p, n in [("rent", "شقق للإيجار"), ("sale", "شقق للبيع")])
    doc = f"""<!DOCTYPE html>
<html lang="ar" dir="rtl"><head><meta charset="utf-8"><meta name="viewport" content="width=device-width, initial-scale=1">
<title>{e(ttl)}</title><meta name="description" content="{e(desc)}"><link rel="canonical" href="{canon}">
<meta property="og:type" content="website"><meta property="og:site_name" content="{e(NAME)}"><meta property="og:locale" content="ar_EG">
<meta property="og:title" content="{e(ttl)}"><meta property="og:description" content="{e(desc)}"><meta property="og:url" content="{canon}">
<meta property="og:image" content="{e(image or img(None))}"><meta name="twitter:card" content="summary_large_image">
<style>{CSS}</style>{ldj}</head><body>
<header><div class="w"><b><a href="{BASE}/">{e(NAME)}</a></b>{links}</div></header>
<main class="w">{body}</main>
<footer><div class="w"><p>{e(NAME)}: شقق إيجار وتمليك في {AREA}. للتواصل: <a href="tel:{PH}">{PH}</a></p></div></footer>
</body></html>"""
    out = os.path.join(ROOT, path, "index.html")
    os.makedirs(os.path.dirname(out), exist_ok=True)
    open(out, "w", encoding="utf-8").write(doc)

def card(a):
    p = f"shaqa/{a['code'].lower()}"
    im = a["imgs"][0] if a.get("imgs") else ""
    return (f'<a class="card" href="{BASE}/{p}/">' + (f'<img src="{BASE}/{im}" alt="{e(title(a))} {DEAL[a["deal"]][1]} في {AREA}" loading="lazy">' if im else "")
            + f'<div><b>{e(title(a))}</b><br><small>{e(a.get("zone") or AREA)} · كود {e(a["code"])}</small><br>'
            + f'<span class="price">{money(a.get("price"))}</span> <small>{DEAL[a["deal"]][2] if a.get("price") else ""}</small></div></a>')

def crumbs(items):
    return {"@context": "https://schema.org", "@type": "BreadcrumbList", "itemListElement":
            [{"@type": "ListItem", "position": i + 1, "name": n, "item": url(p)} for i, (n, p) in enumerate(items)]}

# امسح الصفحات القديمة عشان الشقق المتشالة متفضلش
for dname in ("shaqa", "rent", "sale", "zones"):
    shutil.rmtree(os.path.join(ROOT, dname), ignore_errors=True)

urls = [("", "1.0")]
org = {"@context": "https://schema.org", "@type": "RealEstateAgent", "name": NAME, "url": BASE + "/", "telephone": "+2" + PH,
       "areaServed": {"@type": "Place", "name": f"{AREA}، الجيزة، مصر"},
       "address": {"@type": "PostalAddress", "addressLocality": AREA, "addressRegion": "الجيزة", "addressCountry": "EG"}}

# صفحة لكل شقة
for a in APTS:
    code = a["code"]; p = f"shaqa/{code.lower()}"; dn, dl, unit = DEAL[a["deal"]]
    z = a.get("zone"); where = f"{z}، {AREA}" if z else AREA
    ttl = f"{title(a)} {dl} في {where} | كود {code} | {NAME}"
    desc = (a.get("desc") or f"{title(a)} {dl} في {where}.")[:150]
    rows = [("الكود", code), ("النوع", f"{a.get('kind','')} ({dn})"), ("المنطقة", where), ("المساحة", f"{a['area']} م²" if a.get("area") else None),
            ("الغرف", a.get("rooms")), ("الحمامات", a.get("baths")), ("الدور", floor(a.get("floor"))),
            ("التشطيب", " · ".join(x for x in [FIN.get(a.get("finish")), a.get("grade")] if x) or None),
            ("السعر", f"{money(a.get('price'))} {unit if a.get('price') else ''}" + (f" ({a['pnote']})" if a.get("pnote") else "")),
            ("العدادات والخدمات", "، ".join(f"{m[0]}: {m[1]}" for m in a.get("meters") or []) or None)]
    tbl = "".join(f"<tr><td>{k}</td><td>{e(str(v))}</td></tr>" for k, v in rows if v not in (None, ""))
    gal = "".join(f'<img src="{BASE}/{im}" alt="{e(title(a))} {dl} في {e(where)} صورة {i+1}" loading="{"eager" if i == 0 else "lazy"}">' for i, im in enumerate(a.get("imgs") or []))
    feats = "".join(f"<li>{e(f)}</li>" for f in a.get("feats") or [])
    msg = f"السلام عليكم، عايز أستفسر عن شقة كود {code} ({dn})\n{BASE}/{p}/"
    from urllib.parse import quote
    same = [x for x in APTS if x is not a and x["deal"] == a["deal"] and x.get("zone") == z][:4] or [x for x in APTS if x is not a and x["deal"] == a["deal"]][:4]
    zs = zslug(z)
    body = (f'<p class="crumb"><a href="{BASE}/">الرئيسية</a> › <a href="{BASE}/{a["deal"]}/">شقق {dl}</a>'
            + (f' › <a href="{BASE}/zones/{zs}/">{e(z)}</a>' if zs else "") + f' › كود {e(code)}</p>'
            + f'<h1>{e(title(a))} {dl} في {e(where)}</h1><p class="price">{money(a.get("price"))} <small>{unit if a.get("price") else ""}</small></p>'
            + (f'<div class="gal">{gal}</div>' if gal else "")
            + f'<div class="btns"><a class="btn" href="{BASE}/#apt-{code.lower()}">شوف الشقة بالفيديو والتفاصيل</a>'
            + f'<a class="btn wa" href="https://wa.me/{WA}?text={quote(msg)}">استفسر على واتساب</a><a class="btn" href="tel:{PH}">اتصل {PH}</a></div>'
            + (f'<h2>عن الشقة</h2><p>{e(a["desc"])}</p>' if a.get("desc") else "")
            + f'<h2>المواصفات</h2><table>{tbl}</table>' + (f'<h2>المميزات</h2><ul class="f">{feats}</ul>' if feats else "")
            + (f'<h2>شقق مشابهة</h2><div class="grid">{"".join(card(x) for x in same)}</div>' if same else ""))
    ld = {"@context": "https://schema.org", "@type": ["Product", "Apartment"] if "فيلا" not in (a.get("kind") or "") else ["Product", "House"],
          "name": f"{title(a)} {dl} في {where}", "description": a.get("desc") or desc, "sku": code, "url": url(p + "/"),
          "image": [img(i) for i in a.get("imgs") or []][:6],
          "address": {"@type": "PostalAddress", "addressLocality": where, "addressRegion": "الجيزة", "addressCountry": "EG"}}
    if a.get("area"): ld["floorSize"] = {"@type": "QuantitativeValue", "value": a["area"], "unitCode": "MTK"}
    if a.get("rooms"): ld["numberOfRooms"] = a["rooms"]
    if a.get("baths"): ld["numberOfBathroomsTotal"] = a["baths"]
    if a.get("price"):
        ld["offers"] = {"@type": "Offer", "price": a["price"], "priceCurrency": "EGP", "availability": "https://schema.org/InStock",
                        "businessFunction": "http://purl.org/goodrelations/v1#" + ("LeaseOut" if a["deal"] == "rent" else "Sell"), "seller": {"@type": "RealEstateAgent", "name": NAME}}
    bc = crumbs([("الرئيسية", ""), (f"شقق {dl}", a["deal"] + "/")] + ([(z, f"zones/{zs}/")] if zs else []) + [(code, p + "/")])
    page(p, ttl, desc, body, [ld, bc], img(a["imgs"][0]) if a.get("imgs") else None)
    urls.append((p + "/", "0.8"))

# صفحات إيجار / تمليك
for k, (dn, dl, unit) in DEAL.items():
    L = [a for a in APTS if a["deal"] == k]
    zones = sorted({a["zone"] for a in L if a.get("zone")})
    ttl = f"شقق {dl} في {AREA} بالصور والأسعار | {NAME}"
    desc = f"{len(L)} شقة وفيلا {dl} في {AREA}، بالصور والفيديو والمساحة وعدد الغرف والسعر. تواصل على واتساب {PH}."
    zl = " · ".join(f'<a href="{BASE}/zones/{zslug(z)}/">{e(z)}</a>' for z in zones)
    body = (f'<h1>شقق {dl} في {AREA}</h1><p>{len(L)} وحدة متاحة دلوقتي {dl} في {AREA}. كل شقة بكودها وصورها وتفاصيلها، والتواصل على واتساب أو تليفون {PH}.</p>'
            + (f"<p>حسب المنطقة: {zl}</p>" if zl else "") + f'<div class="grid">{"".join(card(a) for a in L)}</div>')
    page(k, ttl, desc, body, [org, crumbs([("الرئيسية", ""), (f"شقق {dl}", k + "/")])])
    urls.append((k + "/", "0.9"))

# صفحة لكل منطقة
for z in sorted({a["zone"] for a in APTS if a.get("zone")}):
    L = [a for a in APTS if a.get("zone") == z]; zs = zslug(z)
    ns = sum(a["deal"] == "sale" for a in L); nr = len(L) - ns
    kinds = "شقق للبيع والإيجار" if ns and nr else ("شقق للبيع" if ns else "شقق للإيجار")
    ttl = f"{kinds} في {z} {AREA} | {NAME}"
    desc = f"{len(L)} وحدة في {z} بـ{AREA}: صور ومساحات وأسعار وأكواد. تواصل على واتساب {PH}."
    body = f'<h1>{kinds} في {e(z)}، {AREA}</h1><p>الوحدات المتاحة في {e(z)} دلوقتي: {len(L)}.</p><div class="grid">{"".join(card(a) for a in L)}</div>'
    page(f"zones/{zs}", ttl, desc, body, [crumbs([("الرئيسية", ""), (z, f"zones/{zs}/")])])
    urls.append((f"zones/{zs}/", "0.7"))

sm = "".join(f"<url><loc>{url(u)}</loc><lastmod>{TODAY}</lastmod><priority>{pr}</priority></url>" for u, pr in urls)
open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(
    f'<?xml version="1.0" encoding="UTF-8"?><urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">{sm}</urlset>')
open(os.path.join(ROOT, "robots.txt"), "w").write(f"User-agent: *\nAllow: /\nDisallow: /admin.html\n\nSitemap: {BASE}/sitemap.xml\n")

# حقن روابط ثابتة + Schema في الصفحة الرئيسية بين علامات
idx = os.path.join(ROOT, "index.html"); h = open(idx, encoding="utf-8").read()
nav = "".join(f'<li><a href="{BASE}/shaqa/{a["code"].lower()}/">{e(title(a))} {DEAL[a["deal"]][1]} - {e(a.get("zone") or AREA)}</a></li>' for a in APTS)
block = (f'<!--SEO-->\n<nav class="seo-links" aria-label="كل الشقق"><a href="{BASE}/rent/">شقق للإيجار في {AREA}</a> · <a href="{BASE}/sale/">شقق للبيع في {AREA}</a><ul>{nav}</ul></nav>\n'
         f'<script type="application/ld+json">{json.dumps(org, ensure_ascii=False)}</script>\n<!--/SEO-->')
h = re.sub(r"<!--SEO-->.*?<!--/SEO-->", lambda m: block, h, flags=re.S) if "<!--SEO-->" in h else h.replace("</footer>", "</footer>\n" + block, 1)
open(idx, "w", encoding="utf-8").write(h)
print(f"built {len(APTS)} listings, {len(urls)} urls")
