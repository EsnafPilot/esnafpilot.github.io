"""EsnafPilot blog builder.

Add a post to _blog/posts.json (newest first is not required; sorted by date),
then run:  python3 _blog/build.py
It regenerates blog/index.html, blog/<slug>.html, sitemap.xml and robots.txt.
"""
import json, os, html
from datetime import date

ROOT = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
SITE = "https://esnafpilot.com"
AYLAR = ["Ocak", "Şubat", "Mart", "Nisan", "Mayıs", "Haziran", "Temmuz", "Ağustos", "Eylül", "Ekim", "Kasım", "Aralık"]

def tr_date(d):
    y, m, dd = map(int, d.split("-"))
    return f"{dd} {AYLAR[m - 1]} {y}"

HEAD = """<!doctype html>
<html lang="tr">
<head>
<meta charset="utf-8">
<meta name="viewport" content="width=device-width, initial-scale=1">
<title>{title}</title>
<meta name="description" content="{desc}">
<meta name="theme-color" content="#4F46E5">
<link rel="canonical" href="{url}">
<meta property="og:type" content="{ogtype}">
<meta property="og:title" content="{ogtitle}">
<meta property="og:description" content="{desc}">
<meta property="og:image" content="{image}">
<meta property="og:url" content="{url}">
<meta name="twitter:card" content="summary_large_image">
<link rel="icon" type="image/png" href="/favicon.png">
<link rel="apple-touch-icon" href="/apple-touch-icon.png">
<link rel="preconnect" href="https://fonts.googleapis.com">
<link rel="preconnect" href="https://fonts.gstatic.com" crossorigin>
<link rel="stylesheet" href="https://fonts.googleapis.com/css2?family=Manrope:wght@400;600;700;800&display=swap">
<link rel="stylesheet" href="/style.css">
{extra}</head>
<body>
<header class="top"><div class="wrap">
  <a class="brand" href="/"><img src="/logo.png" alt="" width="34" height="34"><span>Esnaf<b>Pilot</b></span></a>
  <nav><a href="/#ozellikler">Özellikler</a><a href="/#fiyatlar">Fiyatlar</a><a href="/blog/" aria-current="page">Blog</a><a href="mailto:destek@esnafpilot.com">İletişim</a></nav>
</div></header>
<main><div class="wrap">
"""

FOOT = """</div></main>
<footer><div class="wrap">
  <span>© 2026 EsnafPilot</span>
  <nav><a href="/blog/">Blog</a><a href="/gizlilik">Gizlilik Politikası</a><a href="/kosullar">Kullanım Koşulları</a><a href="/hesap-sil">Hesap Silme</a><a href="https://www.instagram.com/esnafpilotcom/" rel="noopener">Instagram</a><a href="mailto:destek@esnafpilot.com">destek@esnafpilot.com</a></nav>
</div></footer>
</body>
</html>
"""

CTA = """<section class="cta">
  <h2>Yayın gününden haberdar ol</h2>
  <p>Yeni yazılar, ipuçları ve lansman duyuruları Instagram'da.</p>
  <div class="cta-row">
    <a class="btn" href="https://www.instagram.com/esnafpilotcom/" rel="noopener">Instagram'da takip et</a>
    <a class="btn ghost" href="/">EsnafPilot'u tanı</a>
  </div>
</section>
"""

def esc(s): return html.escape(s, quote=True)

def main():
    posts = json.load(open(os.path.join(ROOT, "_blog", "posts.json"), encoding="utf-8"))
    posts.sort(key=lambda p: p["date"], reverse=True)
    os.makedirs(os.path.join(ROOT, "blog"), exist_ok=True)

    for i, p in enumerate(posts):
        url = f"{SITE}/blog/{p['slug']}"
        ld = {
            "@context": "https://schema.org", "@type": "BlogPosting",
            "headline": p["title"], "description": p["description"],
            "image": SITE + p["image"], "datePublished": p["date"], "dateModified": p.get("updated", p["date"]),
            "inLanguage": "tr-TR", "mainEntityOfPage": url,
            "author": {"@type": "Organization", "name": "EsnafPilot", "url": SITE},
            "publisher": {"@type": "Organization", "name": "EsnafPilot", "logo": {"@type": "ImageObject", "url": SITE + "/logo.png"}},
        }
        extra = '<script type="application/ld+json">' + json.dumps(ld, ensure_ascii=False) + "</script>\n"
        others = [o for o in posts if o is not p][:3]
        more = ""
        if others:
            more = '<aside class="more"><h2>Diğer yazılar</h2><ul>' + "".join(
                f'<li><a href="/blog/{o["slug"]}">{esc(o["title"])}</a></li>' for o in others) + "</ul></aside>\n"
        body = HEAD.format(title=esc(p["title"]) + " · EsnafPilot Blog", desc=esc(p["description"]), url=url,
                           ogtype="article", ogtitle=esc(p["title"]), image=SITE + p["image"], extra=extra)
        body += f"""<article class="doc post">
<p class="crumbs"><a href="/blog/">Blog</a> · <span>{esc(p['tag'])}</span></p>
<h1>{esc(p['title'])}</h1>
<p class="meta"><time datetime="{p['date']}">{tr_date(p['date'])}</time> · EsnafPilot</p>
<img class="cover" src="{p['image']}" alt="{esc(p['image_alt'])}" width="1080" height="1350">
{p['body']}
</article>
{more}{CTA}"""
        body += FOOT
        open(os.path.join(ROOT, "blog", p["slug"] + ".html"), "w", encoding="utf-8").write(body)

    cards = "".join(f"""<a class="card" href="/blog/{p['slug']}">
  <img src="{p['image']}" alt="" width="1080" height="1350" loading="lazy">
  <div><span class="ctag">{esc(p['tag'])}</span><h2>{esc(p['title'])}</h2><p>{esc(p['description'])}</p><time datetime="{p['date']}">{tr_date(p['date'])}</time></div>
</a>
""" for p in posts)
    idx = HEAD.format(title="Blog · EsnafPilot", desc="Esnaflar, e-ticaret ve sosyal medya satıcıları için işletme yönetimi, ürün açıklaması ve satış ipuçları.",
                      url=SITE + "/blog/", ogtype="website", ogtitle="EsnafPilot Blog", image=SITE + "/logo.png", extra="")
    idx += f"""<section class="blog-head">
  <span class="eyebrow">EsnafPilot Blog</span>
  <h1>İşini büyütmek için pratik ipuçları</h1>
  <p>Gelir-gider takibinden satan ürün açıklamasına; esnaflar, e-ticaret ve sosyal medya satıcıları için kısa ve uygulanabilir yazılar.</p>
</section>
<div class="cards">
{cards}</div>
{CTA}"""
    idx += FOOT
    open(os.path.join(ROOT, "blog", "index.html"), "w", encoding="utf-8").write(idx)

    today = date.today().isoformat()
    urls = [(SITE + "/", today), (SITE + "/blog/", posts[0]["date"] if posts else today),
            (SITE + "/gizlilik", "2026-10-05"), (SITE + "/kosullar", "2026-10-05")]
    urls += [(f"{SITE}/blog/{p['slug']}", p.get("updated", p["date"])) for p in posts]
    sm = '<?xml version="1.0" encoding="UTF-8"?>\n<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9">\n'
    sm += "".join(f"  <url><loc>{u}</loc><lastmod>{d}</lastmod></url>\n" for u, d in urls) + "</urlset>\n"
    open(os.path.join(ROOT, "sitemap.xml"), "w", encoding="utf-8").write(sm)
    open(os.path.join(ROOT, "robots.txt"), "w", encoding="utf-8").write(f"User-agent: *\nAllow: /\n\nSitemap: {SITE}/sitemap.xml\n")
    print(f"built {len(posts)} posts")

if __name__ == "__main__":
    main()
