from __future__ import annotations

from fastapi.testclient import TestClient

from apps import create_app


def test_health_ok():
    with TestClient(create_app()) as client:
        assert client.get("/health").json() == {"status": "ok"}


def test_name_svg_route():
    with TestClient(create_app()) as client:
        r = client.get("/public/name.svg")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert r.headers["cache-control"] == "no-store, max-age=0"
        assert b"Khyles" in r.content


def test_console_svg_route():
    with TestClient(create_app()) as client:
        r = client.get("/public/console.svg")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert r.headers["cache-control"] == "no-store, max-age=0"
        assert b"nova@ProjectNova" in r.content  # chrome title bar


def test_skills_svg_route():
    with TestClient(create_app()) as client:
        r = client.get("/public/skills.svg")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert r.headers["cache-control"] == "no-store, max-age=0"
        assert b"Python" in r.content  # tech stack
        assert b"GateKeeper" in r.content  # projects


def test_legacy_svg_redirects():
    with TestClient(create_app()) as client:
        for path, target in [
            ("/name.svg", "/public/name.svg"),
            ("/console.svg", "/public/console.svg"),
            ("/skills.svg", "/public/skills.svg"),
        ]:
            r = client.get(path, follow_redirects=False)
            assert r.status_code == 301
            assert r.headers["location"] == target


def test_old_typing_route_gone():
    with TestClient(create_app()) as client:
        assert client.get("/typing.svg").status_code == 404


def test_project_badge_route():
    with TestClient(create_app()) as client:
        r = client.get("/public/project/gatekeeper.svg")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert r.headers["cache-control"] == "no-store, max-age=0"
        assert b"<svg" in r.content


def test_project_badge_unknown_slug_is_404():
    with TestClient(create_app()) as client:
        r = client.get("/public/project/not-a-project.svg")
        assert r.status_code == 404


def test_every_project_slug_serves_a_badge():
    from apps import project_svg

    with TestClient(create_app()) as client:
        for slug in project_svg.slugs():
            r = client.get(f"/public/project/{slug}.svg")
            assert r.status_code == 200, slug
            assert b"<svg" in r.content, slug


def test_legacy_project_badge_redirects():
    with TestClient(create_app()) as client:
        r = client.get("/projects/gatekeeper.svg", follow_redirects=False)
        assert r.status_code == 301
        assert r.headers["location"] == "/public/project/gatekeeper.svg"


def test_public_index_lists_project_badges():
    from apps import project_svg

    with TestClient(create_app()) as client:
        r = client.get("/public")
        assert r.status_code == 200
        for slug in project_svg.slugs():
            assert f"/public/project/{slug}.svg" in r.text, slug


def test_plural_project_path_redirects_to_singular():
    """An embed pointing at the older plural path must keep working."""
    with TestClient(create_app()) as client:
        r = client.get("/public/projects/gatekeeper.svg", follow_redirects=False)
        assert r.status_code == 301
        assert r.headers["location"] == "/public/project/gatekeeper.svg"


def test_badge_art_comes_from_the_font_file():
    """The badge draws the project name, so the art must match the font output."""
    from apps import figlet, project_svg

    for slug in ("gatekeeper", "solvespace"):
        art = figlet.render(project_svg.PROJECTS[slug]["art"])
        assert art, slug
        # The font is 7 rows and its last row is the blank shadow baseline, so
        # the assertion is on the six carved rows above it.
        assert all(line.strip() for line in art[:-1]), slug
        assert not art[-1].strip(), slug
        # The block glyphs are box-drawing characters, not ASCII substitutes.
        assert any(any(ch in line for ch in "█╗╔╚╝═║") for line in art), slug


def test_badge_output_fills_the_terminal_exactly():
    """The badge must not overflow the terminal, or the art scrolls out of frame.

    The font draws 7 rows and the last is a blank baseline, so 6 carved rows is
    the number that lands: 6 art + url + blurb = 8 = max_line. One row more and
    the top of the art is cut off, which is exactly what happened before.
    """
    from apps import figlet, project_svg

    for slug in project_svg.slugs():
        art = [line for line in figlet.render(project_svg.PROJECTS[slug]["art"]) if line.strip()]
        output_lines = len(art) + 2  # art, url, blurb
        assert len(art) == 6, f"{slug}: {len(art)} carved rows, expected 6"
        assert output_lines == 8, f"{slug}: {output_lines} output lines, terminal holds 8"


def test_badge_matches_name_svg_shape():
    """Same chrome and preamble as the profile badge, only the script differs."""
    import re

    from apps import name_svg, project_svg

    def rows(svg):
        return [re.sub(r"<[^>]+>", "", e)
                for e in re.findall(r"<text[^>]*>.*?</text>", svg, re.S)]

    profile = rows(name_svg.render_name_svg())
    badge = rows(project_svg.render_project_badge("gatekeeper"))

    assert len(profile) == len(badge), "row count differs from name.svg"
    # Title bar and the ssh/password preamble are shared.
    assert profile[0] == badge[0], "terminal title bar differs"
    assert "ssh nova@ProjectNova.remote" in badge[1], "missing the ssh step"
    assert "password" in badge[2], "missing the password step"
    # Only the final command differs.
    assert "introduce_yourself.sh" in profile[3]
    assert "get_project_name.sh" in badge[3]


def test_requests_are_logged():
    """A served request must appear in the access log.

    The structlog branch used to return before the stdlib handler was installed,
    so the access-log middleware wrote to a logger with no handler and the
    service served silently. That made "is this being hit" unanswerable.
    """
    import io
    import logging

    from fastapi.testclient import TestClient

    from apps import create_app

    stream = io.StringIO()
    handler = logging.StreamHandler(stream)
    root = logging.getLogger()
    root.addHandler(handler)
    root.setLevel(logging.INFO)
    try:
        with TestClient(create_app()) as client:
            client.get("/public/name.svg")
    finally:
        root.removeHandler(handler)

    assert "/public/name.svg" in stream.getvalue()
