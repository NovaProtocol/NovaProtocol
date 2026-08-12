from __future__ import annotations

from pathlib import Path

_PROFILE_PATH = Path(__file__).resolve().parent.parent / "data" / "github_profile.html"


def _render_svg_gallery() -> str:
    """Self-contained live view: embed the profile SVGs directly.

    Uses <object> so SMIL animations actually run. No dependency on the
    scraped profile snapshot, so this works in any deployment.
    """
    cards = "".join(
        f'<div style="background:#0a0a0f;border-radius:12px;padding:16px;'
        f'margin:0 auto 24px;max-width:900px;display:flex;justify-content:center;">'
        f'<object type="image/svg+xml" data="{path}" '
        f'style="max-width:100%;"></object></div>'
        for path in ("/name.svg", "/skills.svg", "/console.svg")
    )
    return f"""<!doctype html>
<html lang="en">
<head>
<meta charset="utf-8">
<title>GitHub Profile Assets</title>
<style>
  body {{ margin:0; padding:32px 16px; background:#0d1117; font-family:system-ui,sans-serif; }}
  h1 {{ color:#e6edf3; text-align:center; font-size:20px; margin:0 0 32px; }}
</style>
</head>
<body>
<h1>Live profile assets</h1>
{cards}
</body>
</html>
"""


def render_test_page() -> str:
    return _render_svg_gallery()
