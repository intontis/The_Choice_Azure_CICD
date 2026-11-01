
"""Database queries for questions and their available options."""

from psycopg.rows import dict_row

from app.db import get_connection


def _get_question(
    *,
    is_start: bool = False,
    question_code: str | None = None,
    question_id: int | None = None,
) -> dict | None:
    """Retrieve one question and all its associated options."""

    selectors = [
        is_start,
        question_code is not None,
        question_id is not None,
    ]

    if sum(selectors) != 1:
        raise ValueError(
            "Specify exactly one of is_start, question_code or question_id."
        )

    query = """
        SELECT
            q.id AS question_id,
            q.code AS question_code,
            q.question_text,
            o.id AS option_id,
            o.code AS option_code,
            o.option_text,
            o.next_question_id,
            o.display_order

        FROM questions AS q

        LEFT JOIN options AS o
            ON q.id = o.question_id

        WHERE
            (%s::boolean AND q.is_start = TRUE)
            OR
            (%s::boolean AND q.code = %s)
            OR
            (%s::boolean AND q.id = %s)

        ORDER BY o.display_order;
    """

    parameters = (
        is_start,
        question_code is not None,
        question_code,
        question_id is not None,
        question_id,
    )

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:
            cur.execute(query, parameters)
            rows = cur.fetchall()

    if not rows:
        return None

    first_row = rows[0]

    options = [
        {
            "id": row["option_id"],
            "code": row["option_code"],
            "text": row["option_text"],
            "next_question_id": row["next_question_id"],
            "display_order": row["display_order"],
        }
        for row in rows
        if row["option_id"] is not None
    ]

    return {
        "id": first_row["question_id"],
        "code": first_row["question_code"],
        "text": first_row["question_text"],
        "options": options,
    }


def get_starting_question() -> dict | None:
    """Retrieve the initial RED/BLUE question."""

    return _get_question(is_start=True)


def get_question_by_code(question_code: str) -> dict | None:
    """Retrieve a question using its unique code."""

    return _get_question(question_code=question_code)


def get_question_by_id(question_id: int) -> dict | None:
    """Retrieve a question using its database ID."""

    return _get_question(question_id=question_id)
