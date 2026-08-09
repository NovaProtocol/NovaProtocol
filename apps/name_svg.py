from __future__ import annotations

W, H = 980, 160
ACCENT = "#50c878"
GRAY = "#828c9b"


def esc(s: str) -> str:
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def render_name_svg() -> str:
    """Centered, polished typing name — like readme-typing-svg.

    Types 'Nova' (large), then 'Khyles Gibrian Ramos' (smaller), holding
    the final state (non-looping).
    """
    total = 10.0

    def _clip(name: str, text: str, y: int, size: int, color: str,
              start: float, dur: float) -> tuple[str, str]:
        s, e = start / total, (start + dur) / total
        clip = (
            f'<clipPath id="nc_{name}">'
            f'<rect x="0" y="{y - size}" width="0" height="{size * 1.6}">'
            f'<animate attributeName="width" dur="{total:.2f}s" '
            f'values="0;0;{W};{W}" fill="freeze" '
            f'keyTimes="0;{s:.4f};{min(e, 0.999):.4f};1"/>'
            f'</rect></clipPath>'
        )
        elem = (
            f'<text x="{W / 2:.0f}" y="{y}" font-size="{size}" fill="{color}" '
            f'font-weight="bold" text-anchor="middle" '
            f'font-family="DejaVu Sans Mono, Menlo, Consolas, monospace" '
            f'clip-path="url(#nc_{name})">{esc(text)}</text>'
        )
        return clip, elem

    c1, e1 = _clip("nova", "Nova", 90, 64, ACCENT, 0.5, 2.5)
    c2, e2 = _clip("name", "Khyles Gibrian Ramos", 130, 24, GRAY, 3.5, 3.0)

    return (
        f'<svg viewBox="0 0 {W} {H}" xmlns="http://www.w3.org/2000/svg">'
        f'<defs>{c1}{c2}</defs>'
        f'<rect width="{W}" height="{H}" fill="#0D1117"/>'
        f'{e1}{e2}'
        f'</svg>'
    )
