from __future__ import annotations

from apps.name_svg import render_name_svg


def test_name_svg_contains_names():
    out = render_name_svg()
    assert "Khyles Gibrian Ramos" in out
    assert "https://github.com/NovaProtocol" in out


def test_name_svg_has_nova_art():
    out = render_name_svg()
    assert ">i<" in out  # first char of "introduce_yourself" (typed per-char)
    assert "█" in out  # ASCII art present


def test_name_svg_green():
    out = render_name_svg()
    assert "#50c878" in out  # NOVA art is green
