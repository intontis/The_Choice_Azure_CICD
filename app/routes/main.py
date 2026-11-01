
"""Main page and journey routes for The Choice."""

from uuid import UUID

from flask import (
    Blueprint,
    abort,
    redirect,
    render_template,
    request,
    session,
    url_for,
)

from app.services.journey_service import (
    JourneyError,
    create_journey,
    submit_answer,
)
from app.services.question_service import (
    get_question_by_id,
    get_starting_question,
)

main_bp = Blueprint("main", __name__)


def _get_journey_id() -> UUID | None:
    """Retrieve and validate the journey ID stored in the session."""

    stored_id = session.get("journey_id")

    if not stored_id:
        return None

    try:
        return UUID(stored_id)
    except (TypeError, ValueError):
        session.pop("journey_id", None)
        session.pop("current_question_id", None)
        return None


def _get_step_number(question_code: str) -> int:
    """Determine the question's position in the three-step journey."""

    if question_code in {"RED_1", "BLUE_1"}:
        return 2

    if question_code == "START":
        return 1

    return 3


@main_bp.get("/")
def home():
    """Display the starting question."""

    journey_id = _get_journey_id()
    current_question_id = session.get("current_question_id")

    # Return an existing visitor to their current question.
    if journey_id is not None and current_question_id is not None:
        return redirect(
            url_for("main.question", question_id=current_question_id)
        )

    question = get_starting_question()

    if question is None:
        return "The starting question is not configured.", 503

    return render_template(
        "index.html",
        question=question,
        step_number=1,
    )


@main_bp.get("/question/<int:question_id>")
def question(question_id: int):
    """Display the next question in the visitor's journey."""

    journey_id = _get_journey_id()

    if journey_id is None:
        return redirect(url_for("main.home"))

    current_question_id = session.get("current_question_id")

    if current_question_id != question_id:
        if current_question_id is not None:
            return redirect(
                url_for("main.question", question_id=current_question_id)
            )

        return redirect(url_for("main.home"))

    question_data = get_question_by_id(question_id)

    if question_data is None:
        abort(404)

    return render_template(
        "index.html",
        question=question_data,
        step_number=_get_step_number(question_data["code"]),
    )


@main_bp.post("/answer")
def submit_choice():
    """Receive a visitor's choice and advance their journey."""

    try:
        question_id = int(request.form["question_id"])
        option_id = int(request.form["option_id"])
    except (KeyError, TypeError, ValueError):
        abort(400)

    journey_id = _get_journey_id()

    # Create the anonymous journey when the visitor makes their first choice.
    if journey_id is None:
        journey_id = create_journey()
        session["journey_id"] = str(journey_id)

    try:
        result = submit_answer(
            journey_id=journey_id,
            question_id=question_id,
            option_id=option_id,
        )
    except JourneyError as error:
        return str(error), 400

    if result["status"] == "completed":
        # Preserve the prophecy for the result page.
        session["prophecy"] = result["prophecy"]
        session["path_signature"] = result["path_signature"]

        # The journey is finished, so remove its active session data.
        session.pop("journey_id", None)
        session.pop("current_question_id", None)

        return redirect(url_for("main.prophecy"))

    next_question_id = result["next_question_id"]
    session["current_question_id"] = next_question_id

    return redirect(
        url_for("main.question", question_id=next_question_id)
    )


@main_bp.get("/prophecy")
def prophecy():
    """Display the prophecy for the completed journey."""

    prophecy_data = session.get("prophecy")

    if prophecy_data is None:
        return redirect(url_for("main.home"))

    return render_template(
        "prophecy.html",
        prophecy=prophecy_data,
        path_signature=session.get("path_signature"),
    )


@main_bp.get("/restart")
def restart():
    """Clear the previous journey and begin a new one."""

    session.pop("journey_id", None)
    session.pop("current_question_id", None)
    session.pop("prophecy", None)
    session.pop("path_signature", None)

    return redirect(url_for("main.home"))
