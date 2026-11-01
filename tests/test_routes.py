
"""Tests for The Choice homepage."""

from app import create_app
from app.routes import main


def test_homepage_displays_starting_question(monkeypatch):
    """The homepage should display the question from the service."""

    starting_question = {
        "id": 1,
        "code": "START",
        "text": "Which pill will you choose?",
        "options": [
            {
                "id": 1,
                "code": "R",
                "text": "Look beyond the reality you know.",
                "next_question_id": 2,
                "display_order": 1,
            },
            {
                "id": 2,
                "code": "B",
                "text": "Preserve the reality you understand.",
                "next_question_id": 3,
                "display_order": 2,
            },
        ],
    }

    monkeypatch.setattr(
        main,
        "get_starting_question",
        lambda: starting_question,
    )

    app = create_app()
    app.config["TESTING"] = True

    response = app.test_client().get("/")

    assert response.status_code == 200
    assert b"Which pill will you choose?" in response.data
    assert b"Look beyond the reality you know." in response.data
    assert b"Preserve the reality you understand." in response.data


def test_homepage_handles_missing_question(monkeypatch):
    """The homepage should handle a missing starting question."""

    monkeypatch.setattr(
        main,
        "get_starting_question",
        lambda: None,
    )

    app = create_app()
    app.config["TESTING"] = True

    response = app.test_client().get("/")

    assert response.status_code == 503
    assert b"not configured" in response.data
