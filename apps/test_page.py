from __future__ import annotations

import re
from pathlib import Path

_PROFILE_PATH = Path(__file__).resolve().parent.parent / "data" / "github_profile.html"

# Canonical URL -> local path
_REWRITES = {
    "https://github.projectnova.download/name.svg": "/name.svg",
    "https://github.projectnova.download/typing.svg": "/typing.svg",
}


def _rewrite_img(html: str) -> str:
    """Rewrite <img> tags that reference the profile's animated SVGs.

    GitHub serves these through Camo: the visible `src` is a camo URL and the
    real URL is in `data-canonical-src`. Replace the camo `src` with the local
    path so they render offline, and remove the stats image.
    """

    def _fix(match: re.Match) -> str:
        tag = match.group(0)
        # determine which file this is from data-canonical-src
        canonical = re.search(r'data-canonical-src="([^"]+)"', tag)
        if not canonical:
            return tag
        url = canonical.group(1)
        if "stats.svg" in url:
            return ""  # drop stats image entirely
        local = _REWRITES.get(url)
        if local:
            tag = re.sub(r'src="[^"]*"', f'src="{local}"', tag, count=1)
            tag = re.sub(r'data-canonical-src="[^"]*"', f'data-canonical-src="{local}"', tag)
        return tag

    return re.sub(r'<img[^>]*>', _fix, html)


def render_test_page() -> str:
    if not _PROFILE_PATH.exists():
        return "<h1>Missing data/github_profile.html</h1>"
    html = _PROFILE_PATH.read_text(encoding="utf-8")
    html = _rewrite_img(html)

    # clean up any orphaned anchor around the removed stats image
    html = re.sub(r'<a href="[^"]*stats\.svg"[^>]*>\s*</a>', '', html)
    return html
