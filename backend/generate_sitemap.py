import xml.etree.ElementTree as ET
from pathlib import Path

TOOLS = [
    "merge", "split", "organize", "compress",
    "word-to-pdf", "ppt-to-pdf", "excel-to-pdf", "pdf-to-word",
    "images-to-pdf", "pdf-to-images", "pdf-to-text",
    "protect", "unlock", "watermark", "page-numbers",
    "redact", "repair", "rotate", "metadata"
]

LANGS = ["en", "de", "es", "fr", "pt", "tr", "ru", "ja", "ar"]
TODAY = "2026-10-17"
BASE_URL = "https://podufu.onrender.com"

def generate():
    lines = [
        '<?xml version="1.0" encoding="UTF-8"?>',
        '<urlset xmlns="http://www.sitemaps.org/schemas/sitemap/0.9"',
        '        xmlns:xhtml="http://www.w3.org/1999/xhtml">'
    ]

    def add_entry(loc: str, priority: str, freq: str, alternates: list):
        lines.append("  <url>")
        lines.append(f"    <loc>{loc}</loc>")
        lines.append(f"    <lastmod>{TODAY}</lastmod>")
        lines.append(f"    <changefreq>{freq}</changefreq>")
        lines.append(f"    <priority>{priority}</priority>")
        for h_lang, h_href in alternates:
            lines.append(f'    <xhtml:link rel="alternate" hreflang="{h_lang}" href="{h_href}" />')
        lines.append("  </url>")

    # 1. Root URL
    root_alts = [(l, f"{BASE_URL}/{l}/") for l in LANGS] + [("x-default", f"{BASE_URL}/en/")]
    add_entry(f"{BASE_URL}/", "1.0", "daily", root_alts)

    # 2. Language Homepages
    for lang in LANGS:
        h_alts = [(l, f"{BASE_URL}/{l}/") for l in LANGS] + [("x-default", f"{BASE_URL}/en/")]
        add_entry(f"{BASE_URL}/{lang}/", "0.9", "daily", h_alts)

    # 3. Dedicated Tool URLs (19 tools x 9 languages = 171 tool pages)
    for tool in TOOLS:
        tool_alts = [(l, f"{BASE_URL}/{l}/{tool}") for l in LANGS] + [("x-default", f"{BASE_URL}/en/{tool}")]
        for lang in LANGS:
            add_entry(f"{BASE_URL}/{lang}/{tool}", "0.8", "weekly", tool_alts)

    lines.append("</urlset>")
    content = "\n".join(lines)

    out_file = Path(__file__).resolve().parent.parent / "frontend" / "sitemap.xml"
    out_file.write_text(content, encoding="utf-8")
    print(f"Generated {out_file} with {len(lines)} lines.")

    # Validate XML
    ET.fromstring(content)
    print("XML is 100% valid!")

if __name__ == "__main__":
    generate()
