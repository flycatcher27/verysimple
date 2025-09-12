#!/usr/bin/env python3
"""
Regenerate theme pages from images on disk.

Usage:
  python3 regen_themes.py                 # rebuild themes/*.html
  python3 regen_themes.py --update-index  # also refresh covers/counts on index.html

Assumptions:
- Repo root has:
    styles.css
    index.html
    media/photography/<ThemeName>/*.jpg|jpeg|png|webp
- Output pages:
    themes/<theme-slug>.html  (slug = lowercased ThemeName)
"""

from __future__ import annotations
import os, sys, re
from pathlib import Path
from html import escape
from urllib.parse import quote
from datetime import datetime

# ---- Config (edit if you add/remove themes) ----
THEME_DIR = Path("media/photography")
THEMES_ORDER = ["Trees", "CityLife", "Landscapes"]  # display order on index
VALID_EXT = {".jpg", ".jpeg", ".png", ".webp"}      # web-friendly files
GRID_CLASS = "grid cols-3"                          # from styles.css

REPO = Path(__file__).resolve().parent

def slugify(s: str) -> str:
    return re.sub(r"[^a-z0-9]+", "-", s.lower()).strip("-")

def find_images(theme_folder: Path) -> list[Path]:
    if not theme_folder.exists():
        return []
    files = []
    for p in sorted(theme_folder.iterdir()):
        if p.is_file() and p.suffix.lower() in VALID_EXT:
            files.append(p)
    return files

def rel_url(p: Path) -> str:
    """Return POSIX path with URL-encoding for spaces etc."""
    # Convert to posix relative path from repo root
    rp = p.relative_to(REPO).as_posix()
    # Encode each path segment
    return "/".join(quote(seg) for seg in rp.split("/"))

def write_theme_page(theme: str, images: list[Path]) -> None:
    slug = slugify(theme)
    out_path = REPO / "themes" / f"{slug}.html"
    out_path.parent.mkdir(parents=True, exist_ok=True)

    rows = []
    rows.append('<!doctype html><html lang="en"><head>')
    rows.append('<meta charset="utf-8"><meta name="viewport" content="width=device-width,initial-scale=1">')
    rows.append(f"<title>{escape(theme)} — Arvind</title>")
    rows.append('<link rel="stylesheet" href="../styles.css">')
    rows.append("</head><body>")

    rows.append('<header class="wrap">')
    rows.append(f'<div class="breadcrumb"><a href="../index.html">Home</a> › <span>{escape(theme)}</span></div>')
    rows.append(f"<h1>{escape(theme)}</h1>")
    rows.append('<button id="backBtn" class="pill">← Back</button>')
    rows.append(f'<p class="muted">Updated {datetime.now().strftime("%Y-%m-%d")}</p>')
    rows.append("</header>")

    rows.append('<main class="wrap">')
    rows.append(f'<div class="{GRID_CLASS}">')
    if images:
        for img in images:
            filename = img.name
            url = rel_url(img)
            rows.append(
                f'<figure class="card"><img src="../{escape(url)}" alt="{escape(filename)}">'
                f'<div class="body muted">{escape(filename)}</div></figure>'
            )
    else:
        rows.append('<p class="muted">No images found for this theme.</p>')
    rows.append("</div></main>")

    rows.append('<footer class="wrap">© <span id="y"></span> Arvind</footer>')

    # Shared lightbox overlay
    rows.append("""
<div id="lightbox" aria-hidden="true">
  <img src="" alt="enlarged">
  <button id="closeBtn">× Close</button>
</div>
<script>
  document.getElementById('y').textContent = new Date().getFullYear();

  // Back behavior
  window.addEventListener('keydown', e => {
    if (e.key === 'Escape') {
      if (lb.style.display === 'flex') closeLB();
      else history.back();
    }
  });
  document.getElementById('backBtn').addEventListener('click', () => history.back());

  // Lightbox
  const lb = document.getElementById('lightbox');
  const lbImg = lb.querySelector('img');
  const closeBtn = document.getElementById('closeBtn');
  function openLB(src, alt){ lb.style.display='flex'; lbImg.src=src; lbImg.alt=alt||''; document.body.classList.add('lb-open'); }
  function closeLB(){ lb.style.display='none'; lbImg.src=''; document.body.classList.remove('lb-open'); }

  document.querySelectorAll('figure img').forEach(img=>{
    img.addEventListener('click',()=>openLB(img.src,img.alt));
  });
  closeBtn.addEventListener('click',closeLB);
  lb.addEventListener('click',e=>{ if(e.target===lb) closeLB(); });
</script>
</body></html>
""")

    out_path.write_text("\n".join(rows), encoding="utf-8")
    print(f"[write] {out_path}")

def update_index_covers_and_counts(index_path: Path, theme_map: dict[str, list[Path]]) -> None:
    """
    Updates index.html cards with the first image as cover + photo counts.
    Looks for blocks like:
      <a class="card" href="themes/trees.html">
        <img src="..." ...>
        <div class="body"><strong>Trees</strong><div class="muted">X photos</div></div>
      </a>
    and replaces the img src + count.
    """
    html = index_path.read_text(encoding="utf-8")

    def repl_card(theme: str, imgs: list[Path]) -> None:
        nonlocal html
        slug = slugify(theme)
        cover_src = rel_url(imgs[0]) if imgs else "media/placeholder.jpg"
        count = f"{len(imgs)} photo" + ("s" if len(imgs) != 1 else "")
        # Build a small regex to replace img src and the muted count within the correct card
        card_re = re.compile(
            rf'(<a\s+class="card"\s+href="themes/{slug}\.html">.*?<img\s+src=")([^"]*)(".*?<div\s+class="body"><strong>{re.escape(theme)}</strong><div\s+class="muted">)([^<]*)(</div></div></a>)',
            flags=re.DOTALL
        )
        html = card_re.sub(rf'\1{escape(cover_src)}\3{count}\5', html, count=1)

    for theme in THEMES_ORDER:
        repl_card(theme, theme_map.get(theme, []))

    index_path.write_text(html, encoding="utf-8")
    print(f"[update] {index_path} (covers + counts)")

def main():
    # Flags
    update_index = "--update-index" in sys.argv

    # Collect themes (only those that exist on disk)
    theme_map: dict[str, list[Path]] = {}
    for theme in THEMES_ORDER:
        imgs = find_images(REPO / THEME_DIR / theme)
        theme_map[theme] = imgs

    # Write theme pages
    (REPO / "themes").mkdir(exist_ok=True)
    for theme, imgs in theme_map.items():
        write_theme_page(theme, imgs)

    # Optionally update the home cards (cover + counts)
    if update_index:
        index_path = REPO / "index.html"
        if index_path.exists():
            update_index_covers_and_counts(index_path, theme_map)
        else:
            print("[skip] index.html not found; cannot update covers/counts", file=sys.stderr)

if __name__ == "__main__":
    main()

