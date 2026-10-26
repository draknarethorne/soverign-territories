"""Shared look for local library reports: theme, banner masthead, page tabs and footer.

Every generated gallery page puts ``CSS`` first in its <style> block, then its own page rules.
The banner image is one shared file, ``<_reports>/_assets/gallery-banner.jpg``, copied once
from this package; an existing file is never overwritten, so a user-chosen banner stays.
When the file is missing the masthead falls back to a gradient.
"""
import html
import os
import pathlib
import tempfile

BANNER_NAME = "gallery-banner.jpg"
BANNER_SOURCE = pathlib.Path(__file__).with_name("assets") / BANNER_NAME
ASSETS_DIR = "_assets"
GALLERY_VERSION = "2026.10.26.1"
SECTIONS = (("People", "library/people_gallery.html"), ("Artists", "artists/artists_gallery.html"),
            ("Rendering", "../_generation/index.html"), ("Outputs", "../_generation/outputs.html"))
CARD_USE_GUIDANCE = {
    "Potentials": "Browsing guidance: consider for common/uncommon card art.",
    "Prospects": "Browsing guidance: consider for broader card-art use.",
    "Models": "Browsing guidance: not the preferred pool for common/uncommon card art.",
}

CSS = """
:root{--st-ink:#1f2a33;--st-muted:#5d6872;--st-paper:#f6f3ed;--st-card:#fff;--st-line:#ddd5c8;--st-accent:#28527a;--st-accent-dark:#1d3e5e;--st-accent-soft:#e7eef4;--st-gold:#c29a45;--st-radius:10px;--st-shadow:0 1px 2px rgba(31,42,51,.05),0 6px 18px rgba(31,42,51,.06)}
*{box-sizing:border-box}
body{margin:0;font:15px/1.45 "Segoe UI",system-ui,Arial,sans-serif;background:var(--st-paper);color:var(--st-ink)}
a{color:var(--st-accent)}h1{font-size:1.65rem;margin:0 0 4px;letter-spacing:.01em}
:focus-visible{outline:3px solid #f0c45a;outline-offset:2px}
input,select,button{font:inherit;padding:6px 9px;border:1px solid #b9c2ca;border-radius:6px;background:#fff;color:inherit}
button{cursor:pointer;background:var(--st-accent);border-color:var(--st-accent);color:#fff}
button:hover:not(:disabled){background:var(--st-accent-dark)}button:disabled{opacity:.5;cursor:default}
.site-masthead{color:#fff;border-bottom:3px solid var(--st-gold);background:linear-gradient(90deg,rgba(13,17,32,.9),rgba(13,17,32,.55) 48%,rgba(13,17,32,.2)),var(--st-banner,none) center 58%/cover no-repeat,linear-gradient(120deg,#1b2140,#3b2f5c 55%,#7a5a2a)}
.site-masthead-inner{max-width:1680px;margin:auto;padding:22px 24px 18px;min-height:136px;display:flex;justify-content:space-between;align-items:flex-end;gap:16px;flex-wrap:wrap}
.site-brand{display:flex;gap:12px;align-items:center;color:#fff;text-decoration:none}
.site-mark{display:grid;place-items:center;width:46px;height:46px;border:2px solid var(--st-gold);border-radius:50%;background:rgba(0,0,0,.35);font-weight:700;letter-spacing:.05em}
.site-brand strong{display:block;font-size:1.4rem;letter-spacing:.02em;text-shadow:0 1px 4px #000}
.site-brand small{display:block;color:#f0e2c2;text-transform:uppercase;letter-spacing:.14em;font-size:.72rem;text-shadow:0 1px 3px #000}
.site-sections{display:flex;gap:6px;flex-wrap:wrap}
.site-sections a{color:#fff;text-decoration:none;padding:7px 15px;border-radius:999px;background:rgba(10,14,28,.5);border:1px solid rgba(255,255,255,.3)}
.site-sections a:hover{background:rgba(10,14,28,.75)}
.site-sections a[aria-current=page]{background:var(--st-gold);border-color:var(--st-gold);color:#1b1608;font-weight:600}
.site-menu{display:none;position:relative}.site-menu summary{cursor:pointer;padding:8px 12px;border:1px solid rgba(255,255,255,.4);border-radius:6px;list-style:none;background:rgba(10,14,28,.65)}
.site-menu summary::-webkit-details-marker{display:none}
.site-menu summary::before{content:"";display:inline-block;width:16px;height:2px;margin:0 9px 4px 0;background:currentColor;box-shadow:0 -5px currentColor,0 5px currentColor}
.site-menu .site-sections{margin-top:8px;flex-direction:column;min-width:160px}
.site-page{max-width:1680px;margin:0 auto;padding:18px 24px 8px}
.page-header{display:flex;justify-content:space-between;align-items:flex-start;gap:24px;padding:16px 20px;background:var(--st-card);border:1px solid var(--st-line);border-radius:var(--st-radius);box-shadow:var(--st-shadow);margin-bottom:12px}
.page-header p{margin:5px 0 0}.header-side{text-align:right}.header-label{font-size:.75em;color:var(--st-muted);text-transform:uppercase;letter-spacing:.06em}
.score-legend{display:flex;justify-content:flex-end;gap:6px;flex-wrap:wrap;margin-top:5px}
.eyebrow{text-transform:uppercase;letter-spacing:.1em;color:#526e81;font-size:.78rem}
.badge,.category-badge,.score-badge,.history,.photo-count{display:inline-block;border-radius:4px;padding:2px 6px;font-size:.82em;font-weight:600;background:#eee;color:#555}
.badge{margin:0 4px 4px 0}.history,.photo-count{margin-left:4px}
.category-sisters{background:#e8e0f2;color:#493365}.category-angels{background:#e4efff;color:#244f85}
.category-models{background:#e4f2e5;color:#285b31}.category-prospects{background:#fff0d9;color:#704a12}.category-potentials{background:#eee;color:#555}
.score-green{background:#d9efdc;color:#205b2a}.score-yellow{background:#fff1bd;color:#6b5200}
.score-orange{background:#ffe0c2;color:#7a3f00}.score-red{background:#f5d6d6;color:#7b2222}
.review-count{background:#fff0d9;color:#704a12}.card-use-guidance{font-size:.86em;color:var(--st-muted)}
.intake-detail-link{display:inline-block;font-size:.86em;font-weight:600;margin-top:8px;padding:4px 8px;border:1px solid var(--st-line);border-radius:6px;background:var(--st-accent-soft)}
a:is(.badge,.category-badge,.score-badge,.history,.photo-count){text-decoration:underline;text-underline-offset:2px}
a:is(.badge,.category-badge,.score-badge,.history,.photo-count):hover{box-shadow:0 0 0 1px currentColor}
.library-nav{position:sticky;top:0;z-index:10;display:flex;gap:6px;flex-wrap:wrap;margin:12px 0;padding:10px 0;background:var(--st-paper);border-bottom:1px solid var(--st-line)}
.site-page :target{scroll-margin-top:6rem}
.library-nav a,.library-footer a{color:var(--st-accent);text-decoration:none;padding:6px 12px;border-radius:6px;background:var(--st-accent-soft)}
.library-nav a:hover,.library-footer a:hover{text-decoration:underline;background:#dce6ed}
.library-nav a[aria-current=page]{background:var(--st-accent);color:#fff}
.library-footer{display:flex;justify-content:space-between;align-items:center;gap:18px;flex-wrap:wrap;margin:28px 0 12px;padding:24px;border-top:3px solid var(--st-gold);border-radius:0 0 var(--st-radius) var(--st-radius);background:linear-gradient(115deg,#17233b,#353052 65%,#534333);color:#eee9df;font-size:.86em;box-shadow:var(--st-shadow)}
.footer-brand strong,.footer-brand small{display:block}.footer-brand strong{font-size:1.12em;letter-spacing:.03em}.footer-brand small{color:#e5cf9e;margin-top:5px}
.footer-message{flex:1 1 260px;max-width:750px}.library-footer a{background:#e7eef4;color:#1d3e5e;white-space:nowrap}
.identity-names{font-size:.86em}.identity-names dt{font-weight:600}.identity-names dd{margin:0 0 5px;overflow-wrap:anywhere}
@media(max-width:760px){.site-masthead-inner{padding:16px 12px 14px;min-height:112px}.site-brand strong{font-size:1.15rem}.site-page{padding:12px}.page-header{display:block}.header-side{text-align:left;margin-top:12px}.score-legend{justify-content:flex-start}}
@media(max-width:600px){.site-masthead-inner>.site-sections{display:none}.site-menu{display:block}.library-footer{padding:18px}}
@media(max-width:760px),(max-height:500px){.library-nav{position:static}.site-page :target{scroll-margin-top:12px}}
@media print{.library-nav{position:static}}
"""


def reports_prefix(page_dir, reports_dir):
    """Relative URL prefix from a page folder to the _reports folder, or None (other drive)."""
    try:
        relative = os.path.relpath(pathlib.Path(reports_dir), pathlib.Path(page_dir))
    except ValueError:
        return None
    relative = pathlib.Path(relative).as_posix()
    return "" if relative == "." else relative.rstrip("/") + "/"


def masthead(section=None, prefix="../", tagline="Local photo library", links=True):
    """Banner header. ``prefix`` leads from the page to _reports; None drops banner and links."""
    style = ""
    if prefix is not None:
        banner = html.escape(f"{prefix}{ASSETS_DIR}/{BANNER_NAME}", quote=True)
        style = f' style="--st-banner:url(&quot;{banner}&quot;)"'
    brand = (
        '<span class="site-mark" aria-hidden="true">ST</span>'
        f'<span><strong>Sovereign Territories</strong><small>{html.escape(tagline)}</small></span>'
    )
    show_links = links and prefix is not None
    if show_links:
        home = html.escape(prefix + SECTIONS[0][1], quote=True)
        brand = f'<a class="site-brand" href="{home}">{brand}</a>'
        sections = '<nav class="site-sections" aria-label="Libraries">' + "".join(
            f'<a href="{html.escape(prefix + href, quote=True)}"'
            + (' aria-current="page"' if label == section else "")
            + f'>{html.escape(label)}</a>'
            for label, href in SECTIONS
        ) + "</nav>"
        sections += (
            '<details class="site-menu"><summary>Menu</summary>'
            + sections.replace('aria-label="Libraries"', 'aria-label="Libraries menu"')
            + "</details>"
        )
    else:
        brand = f'<div class="site-brand">{brand}</div>'
        sections = ""
    return f'<div class="site-masthead" role="banner"{style}><div class="site-masthead-inner">{brand}{sections}</div></div>'


def navigation(links, current):
    return '<nav class="library-nav" aria-label="Gallery pages">' + "".join(
        f'<a href="{html.escape(href, quote=True)}"'
        + (' aria-current="page"' if label == current else "")
        + f'>{html.escape(label)}</a>'
        for label, href in links
    ) + "</nav>"


def footer(message):
    return (
        '<footer class="library-footer"><span class="footer-brand"><strong>Sovereign Territories</strong>'
        f'<small>Local photo library · Gallery UI v{GALLERY_VERSION}</small></span>'
        f'<span class="footer-message">{html.escape(message)}</span><a href="#top">Back to top</a></footer>'
    )


def publish_banner(reports_dir):
    """Copy the packaged banner to <_reports>/_assets once; keep any existing (user-chosen) file."""
    target = pathlib.Path(reports_dir) / ASSETS_DIR / BANNER_NAME
    if target.is_symlink():
        raise ValueError(f"linked gallery banner refused: {target}")
    if target.is_file():
        if target.read_bytes() != BANNER_SOURCE.read_bytes():
            print(f"Gallery banner: keeping the existing custom banner {target}")
        return target
    if not BANNER_SOURCE.is_file():
        print(f"DIAGNOSTIC: packaged gallery banner missing ({BANNER_SOURCE}); pages use the gradient fallback")
        return None
    target.parent.mkdir(parents=True, exist_ok=True)
    stage = None
    try:
        with tempfile.NamedTemporaryFile(dir=target.parent, prefix=".banner-", suffix=".tmp", delete=False) as output:
            stage = pathlib.Path(output.name)
            output.write(BANNER_SOURCE.read_bytes())
        os.replace(stage, target)
    finally:
        if stage is not None and stage.exists():
            stage.unlink()
    print(f"Gallery banner: published {target} ({target.stat().st_size} bytes, shared by every report page)")
    return target
