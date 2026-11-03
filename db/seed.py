
"""Populate The Choice database with its initial question tree and prophecies."""

import sys

import psycopg


QUESTIONS = [
    (
        "START",
        "A choice stands before you. One path reveals what is hidden, while "
        "the other preserves the world you know. Which one will you choose?",
        True,
    ),
    (
        "RED_1",
        "You have chosen to look closer. The first truth you uncover is "
        "incomplete. What do you do next?",
        False,
    ),
    (
        "BLUE_1",
        "Your familiar world offers certainty, but you notice something "
        "doesn't add up. How do you respond?",
        False,
    ),
    (
        "RED_1_1",
        "The evidence leads to a door no one else can see. "
        "What do you carry through it?",
        False,
    ),
    (
        "RED_1_2",
        "Someone offers a convincing explanation, but it conflicts "
        "with what you witnessed.",
        False,
    ),
    (
        "BLUE_1_1",
        "Your investigation reveals that one familiar rule was "
        "never inevitable.",
        False,
    ),
    (
        "BLUE_1_2",
        "The contradiction fades, but the question remains.",
        False,
    ),
]


OPTIONS = [
    # Starting question
    ("START", "R", "Look beyond the reality you know", "RED_1", 1),
    ("START", "B", "Preserve the reality you understand", "BLUE_1", 2),

    # Second question: RED
    (
        "RED_1",
        "1",
        "Follow the evidence, even if it unsettles you.",
        "RED_1_1",
        1,
    ),
    (
        "RED_1",
        "2",
        "Seek another perspective before deciding what it means.",
        "RED_1_2",
        2,
    ),

    # Second question: BLUE
    (
        "BLUE_1",
        "1",
        "Investigate the contradiction quietly.",
        "BLUE_1_1",
        1,
    ),
    (
        "BLUE_1",
        "2",
        "Set it aside and protect the life you have built.",
        "BLUE_1_2",
        2,
    ),

    # Third question: RED -> 1
    (
        "RED_1_1",
        "1",
        "Reveal everything, even if it creates chaos.",
        None,
        1,
    ),
    (
        "RED_1_1",
        "2",
        "Protect those who aren't ready to know.",
        None,
        2,
    ),

    # Third question: RED -> 2
    (
        "RED_1_2",
        "1",
        "Challenge the explanation.",
        None,
        1,
    ),
    (
        "RED_1_2",
        "2",
        "Keep listening until the pattern becomes clear.",
        None,
        2,
    ),

    # Third question: BLUE -> 1
    (
        "BLUE_1_1",
        "1",
        "Test a different way.",
        None,
        1,
    ),
    (
        "BLUE_1_1",
        "2",
        "Wait until you understand the consequences.",
        None,
        2,
    ),

    # Third question: BLUE -> 2
    (
        "BLUE_1_2",
        "1",
        "Return to it when the moment is right.",
        None,
        1,
    ),
    (
        "BLUE_1_2",
        "2",
        "Let it go and choose peace.",
        None,
        2,
    ),
]


PROPHECIES = [
    (
        "R11",
        "The Cartographer",
        "You move towards the unknown, relying on evidence rather "
        "than promises. You are willing to enter unfamiliar territory, "
        "but remember that even the best map cannot predict every turn.",
    ),
    (
        "R12",
        "The Keeper of Names",
        "You crossed the threshold, but you did not leave everyone "
        "behind. You carry the people and experiences that shaped "
        "your journey. Remember that responsibility can be both "
        "an anchor and a compass.",
    ),
    (
        "R21",
        "The Skeptic's Flame",
        "You question explanations that others accept without "
        "hesitation. Your curiosity keeps you moving, but remember "
        "that doubt is a tool for discovery, not a destination.",
    ),
    (
        "R22",
        "The Listener at the Gate",
        "You seek understanding before making your final decision. "
        "You know that patience can reveal patterns that haste "
        "would destroy. Just make sure you recognize when the "
        "moment to act has arrived.",
    ),
    (
        "B11",
        "The Quiet Disruptor",
        "You appear to preserve the familiar, yet quietly investigate "
        "what others overlook. You may discover that the greatest "
        "changes do not always begin with rebellion. Sometimes "
        "they begin with one unanswered question.",
    ),
    (
        "B12",
        "The Steward of Consequences",
        "You recognize that truth and responsibility must coexist. "
        "You are willing to question what you know, but you "
        "understand that every decision has consequences beyond yourself.",
    ),
    (
        "B21",
        "The Returner",
        "You chose stability, but something kept calling you back. "
        "Not every question must be answered immediately. "
        "Some truths wait until you are ready to confront them.",
    ),
    (
        "B22",
        "The Keeper of Still Waters",
        "You value peace and the world you have built. There is "
        "strength in knowing what you wish to preserve. But remember: "
        "comfort and certainty are not always the same thing.",
    ),
]


def seed_database(conn: psycopg.Connection) -> None:
    """Insert or update the initial application data."""

    question_ids = {}
    prophecy_ids = {}

    with conn.cursor() as cur:

        # Insert questions and retrieve their database IDs.
        for code, text, is_start in QUESTIONS:
            cur.execute(
                """
                INSERT INTO questions (code, question_text, is_start)
                VALUES (%s, %s, %s)
                ON CONFLICT (code) DO UPDATE
                SET question_text = EXCLUDED.question_text,
                    is_start = EXCLUDED.is_start
                RETURNING id;
                """,
                (code, text, is_start),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError(f"Failed to retrieve ID for question: {code}")
            question_ids[code] = row[0]

        # Insert prophecies and retrieve their database IDs.
        for code, title, message in PROPHECIES:
            cur.execute(
                """
                INSERT INTO prophecies (code, title, message)
                VALUES (%s, %s, %s)
                ON CONFLICT (code) DO UPDATE
                SET title = EXCLUDED.title,
                    message = EXCLUDED.message
                RETURNING id;
                """,
                (code, title, message),
            )
            row = cur.fetchone()
            if row is None:
                raise RuntimeError(f"Failed to retrieve ID for prophecy: {code}")
            prophecy_ids[code] = row[0]

        # Insert the answer options and their next-question relationships.
        for question_code, option_code, text, next_code, order in OPTIONS:

            next_question_id = None

            if next_code is not None:
                next_question_id = question_ids[next_code]

            cur.execute(
                """
                INSERT INTO options
                    (question_id, code, option_text,
                     next_question_id, display_order)
                VALUES (%s, %s, %s, %s, %s)
                ON CONFLICT (question_id, code) DO UPDATE
                SET option_text = EXCLUDED.option_text,
                    next_question_id = EXCLUDED.next_question_id,
                    display_order = EXCLUDED.display_order;
                """,
                (
                    question_ids[question_code],
                    option_code,
                    text,
                    next_question_id,
                    order,
                ),
            )

        # Map every complete journey to its corresponding prophecy.
        for path_code, prophecy_id_code in [
            ("R11", "R11"),
            ("R12", "R12"),
            ("R21", "R21"),
            ("R22", "R22"),
            ("B11", "B11"),
            ("B12", "B12"),
            ("B21", "B21"),
            ("B22", "B22"),
        ]:
            cur.execute(
                """
                INSERT INTO prophecy_routes (path_signature, prophecy_id)
                VALUES (%s, %s)
                ON CONFLICT (path_signature) DO UPDATE
                SET prophecy_id = EXCLUDED.prophecy_id;
                """,
                (path_code, prophecy_ids[prophecy_id_code]),
            )

    print("Database seeding completed successfully.")
    print(f"Questions:  {len(QUESTIONS)}")
    print(f"Options:    {len(OPTIONS)}")
    print(f"Prophecies: {len(PROPHECIES)}")
    print("Prophecy routes: 8")


def main() -> None:
    try:
        # Psycopg reads connection settings from PGHOST, PGUSER,
        # PGDATABASE, PGPORT and PGPASSWORD environment variables.
        with psycopg.connect() as conn:
            seed_database(conn)

    except psycopg.Error as error:
        print(f"Database error: {error}", file=sys.stderr)
        raise SystemExit(1) from error

    except (KeyError, ValueError) as error:
        print(f"Seed data error: {error}", file=sys.stderr)
        raise SystemExit(1) from error


if __name__ == "__main__":
    main()
