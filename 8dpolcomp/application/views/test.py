
import json
import logging

from flask import Blueprint, render_template, session, request, redirect, url_for

from application.controllers.questions import QuestionsController as Questions


logger = logging.getLogger(__name__)


v = Blueprint("test", __name__)


@v.route("/test", methods=["GET"])
def test():
    """
    Render the main test page (questions).

    Args:
        None

    Returns:
        Response: HTML template response for the test page.

    Raises:
        302: Redirects to the correct template if session state is invalid.
        500: If question loading fails.
    """

    # Redirect to correct template. Prevents user accessing incorrect test page.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "test":
        return redirect(url_for(f"{session['template']}.{session['template']}"))

    # Get question texts, pass to front.
    try:
        texts = json.dumps(Questions.get_texts(test=False))
    except Exception:
        logger.exception("[/test] Failed to load question texts")
        session["template"] = "instructions"
        return redirect(url_for("instructions.instructions"))

    session["template"] = "test"
    return render_template(f"pages/{session['template']}.html", texts=texts)
