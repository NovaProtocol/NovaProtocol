from __future__ import annotations

from apps.console_svg import render_console_svg


def test_console_svg_has_chrome():
    out = render_console_svg()
    assert "nova@ProjectNova" in out  # title bar
    assert "#0D1117" in out  # background


def test_console_svg_is_svg():
    out = render_console_svg()
    assert out.startswith("<svg")
    assert out.endswith("</svg>")
