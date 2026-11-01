
"""Database operations for visitor journeys."""

from uuid import UUID, uuid4

from psycopg.rows import dict_row

from app.db import get_connection


class JourneyError(Exception):
    """Base exception for journey-related errors."""


class JourneyNotFoundError(JourneyError):
    """Raised when a journey does not exist."""


class InvalidAnswerError(JourneyError):
    """Raised when an answer is invalid for the current question."""


class JourneyCompletedError(JourneyError):
    """Raised when an answer is submitted to an already completed journey."""


def create_journey() -> UUID:
    """Create a new anonymous journey and return its UUID."""

    journey_id = uuid4()

    with get_connection() as conn:
        with conn.cursor() as cur:
            cur.execute(
                """
                INSERT INTO journeys (id, status)
                VALUES (%s, 'in_progress');
                """,
                (journey_id,),
            )

    return journey_id


def submit_answer(
    journey_id: UUID,
    question_id: int,
    option_id: int,
) -> dict:
    """Record an answer and determine the next step in the journey."""

    with get_connection() as conn:
        with conn.cursor(row_factory=dict_row) as cur:

            # Lock the journey to prevent simultaneous submissions.
            cur.execute(
                """
                SELECT id, status, path_signature
                FROM journeys
                WHERE id = %s
                FOR UPDATE;
                """,
                (journey_id,),
            )

            journey = cur.fetchone()

            if journey is None:
                raise JourneyNotFoundError("Journey does not exist.")

            if journey["status"] != "in_progress":
                raise JourneyCompletedError("Journey is already completed.")

            # Count how many answers have already been recorded.
            cur.execute(
                """
                SELECT COUNT(*) AS response_count
                FROM responses
                WHERE journey_id = %s;
                """,
                (journey_id,),
            )

            response_count_row = cur.fetchone()

            if response_count_row is None:
                raise RuntimeError("Could not count journey responses.")

            response_count = response_count_row["response_count"]

            if response_count >= 3:
                raise JourneyCompletedError("All questions have been answered.")

            # Determine which question the visitor should currently answer.
            if response_count == 0:
                cur.execute(
                    """
                    SELECT id
                    FROM questions
                    WHERE is_start = TRUE;
                    """
                )

                current_question = cur.fetchone()

                if current_question is None:
                    raise RuntimeError("Starting question is not configured.")

                expected_question_id = current_question["id"]

            else:
                cur.execute(
                    """
                    SELECT o.next_question_id
                    FROM responses AS r
                    JOIN options AS o
                        ON r.option_id = o.id
                    WHERE r.journey_id = %s
                    ORDER BY r.response_order DESC
                    LIMIT 1;
                    """,
                    (journey_id,),
                )

                last_answer = cur.fetchone()

                if last_answer is None:
                    raise RuntimeError("Journey has responses but no previous answer was found.")

                expected_question_id = last_answer["next_question_id"]

                if expected_question_id is None:
                    raise JourneyCompletedError("The previous answer has no next question.")

            if expected_question_id is None:
                raise JourneyCompletedError("No further question is available.")

            if question_id != expected_question_id:
                raise InvalidAnswerError("This is not the current question.")

            # Make sure the selected option belongs to this question.
            cur.execute(
                """
                SELECT id, code, next_question_id
                FROM options
                WHERE id = %s
                  AND question_id = %s;
                """,
                (option_id, question_id),
            )

            selected_option = cur.fetchone()

            if selected_option is None:
                raise InvalidAnswerError("Invalid option for this question.")

            # Record the answer.
            response_order = response_count + 1

            cur.execute(
                """
                INSERT INTO responses (
                    journey_id,
                    question_id,
                    option_id,
                    response_order
                )
                VALUES (%s, %s, %s, %s);
                """,
                (
                    journey_id,
                    question_id,
                    option_id,
                    response_order,
                ),
            )

            # Build the complete answer-path signature.
            path_signature = (
                journey["path_signature"] or ""
            ) + selected_option["code"]

            next_question_id = selected_option["next_question_id"]

            # A terminal option means the journey should now be complete.
            if next_question_id is None:

                if response_order != 3:
                    raise InvalidAnswerError(
                        "The journey ended before all three questions."
                    )

                # Find the prophecy assigned to this exact path.
                cur.execute(
                    """
                    SELECT
                        p.id,
                        p.code,
                        p.title,
                        p.message
                    FROM prophecy_routes AS pr
                    JOIN prophecies AS p
                        ON pr.prophecy_id = p.id
                    WHERE pr.path_signature = %s;
                    """,
                    (path_signature,),
                )

                prophecy = cur.fetchone()

                if prophecy is None:
                    raise RuntimeError(
                        f"No prophecy configured for path {path_signature}."
                    )

                # Mark the journey as completed.
                cur.execute(
                    """
                    UPDATE journeys
                    SET
                        status = 'completed',
                        path_signature = %s,
                        prophecy_id = %s,
                        completed_at = CURRENT_TIMESTAMP
                    WHERE id = %s;
                    """,
                    (
                        path_signature,
                        prophecy["id"],
                        journey_id,
                    ),
                )

                return {
                    "status": "completed",
                    "path_signature": path_signature,
                    "prophecy": prophecy,
                }

            # A non-terminal option must lead to the next question.
            if response_order == 3:
                raise InvalidAnswerError(
                    "The third question must lead to a prophecy."
                )

            # Save the path so far.
            cur.execute(
                """
                UPDATE journeys
                SET path_signature = %s
                WHERE id = %s;
                """,
                (path_signature, journey_id),
            )

            return {
                "status": "in_progress",
                "path_signature": path_signature,
                "next_question_id": next_question_id,
            }
