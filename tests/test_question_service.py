
"""Tests for the question database service."""

from app.services.question_service import (
    get_question_by_code,
    get_starting_question,
)


def test_get_starting_question():
    """The starting question should contain RED and BLUE options."""

    question = get_starting_question()

    assert question is not None
    assert question["code"] == "START"
    assert len(question["options"]) == 2

    option_codes = [option["code"] for option in question["options"]]

    assert option_codes == ["R", "B"]


def test_get_question_by_code():
    """A question should be retrievable by its unique code."""

    question = get_question_by_code("RED_1")

    assert question is not None
    assert question["code"] == "RED_1"
    assert len(question["options"]) == 2


def test_get_nonexistent_question():
    """An unknown question code should return None."""

    question = get_question_by_code("DOES_NOT_EXIST")

    assert question is None
