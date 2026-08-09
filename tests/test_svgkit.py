import svgwrite
from apps.svgkit import TypeWriter, FONT, GREEN


def test_typed_emits_clip_animation():
    dwg = svgwrite.Drawing(viewBox="0 0 100 100")
    g = dwg.g()
    TypeWriter(dwg).typed(g, "df -h", 10, 20, 14, GREEN, 0.0, 1.0)
    dwg.add(g)
    out = dwg.tostring()
    assert "clipPath" in out
    assert 'attributeName="width"' in out
    assert "freeze" in out
    assert "df -h" in out
    assert FONT in out


def test_plain_has_no_clip():
    dwg = svgwrite.Drawing(viewBox="0 0 100 100")
    g = dwg.g()
    TypeWriter(dwg).plain(g, "hello", 10, 20, 14, GREEN)
    dwg.add(g)
    out = dwg.tostring()
    assert "clipPath" not in out
    assert "hello" in out


def test_typed_escapes_markup():
    dwg = svgwrite.Drawing(viewBox="0 0 100 100")
    g = dwg.g()
    TypeWriter(dwg).typed(g, "a <b> & c", 0, 20, 14, GREEN, 0.0, 1.0)
    dwg.add(g)
    out = dwg.tostring()
    assert "&lt;b&gt;" in out
