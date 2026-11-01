"""Tests for the PostgreSQL connection."""

from app.db import get_connection


def test_database_connection():
    """Verify that the application can connect to PostgreSQL."""

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute("SELECT current_database(), current_user")
            row = cur.fetchone()

    assert row is not None, "Database query returned no results"

    database, user = row

    assert database == "the_choice"
    assert user == "the_choice_app"