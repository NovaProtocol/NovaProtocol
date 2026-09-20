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
        r = client.get("/public/projects/gatekeeper.svg")
        assert r.status_code == 200
        assert r.headers["content-type"].startswith("image/svg+xml")
        assert r.headers["cache-control"] == "no-store, max-age=0"
        assert b"<svg" in r.content


def test_project_badge_unknown_slug_is_404():
    with TestClient(create_app()) as client:
        r = client.get("/public/projects/not-a-project.svg")
        assert r.status_code == 404


def test_every_project_slug_serves_a_badge():
    from apps import project_svg

    with TestClient(create_app()) as client:
        for slug in project_svg.slugs():
            r = client.get(f"/public/projects/{slug}.svg")
            assert r.status_code == 200, slug
            assert b"<svg" in r.content, slug


def test_legacy_project_badge_redirects():
    with TestClient(create_app()) as client:
        r = client.get("/projects/gatekeeper.svg", follow_redirects=False)
        assert r.status_code == 301
        assert r.headers["location"] == "/public/projects/gatekeeper.svg"


def test_public_index_lists_project_badges():
    from apps import project_svg

    with TestClient(create_app()) as client:
        r = client.get("/public")
        assert r.status_code == 200
        for slug in project_svg.slugs():
            assert f"/public/projects/{slug}.svg" in r.text, slug
