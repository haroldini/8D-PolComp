
import logging

from flask import Blueprint, render_template, session, request, redirect, url_for


logger = logging.getLogger(__name__)


v = Blueprint("instructions", __name__)


@v.route("/instructions", methods=["GET"])
def instructions():
    """
    Render the instructions page.

    Args:
        None

    Returns:
        Response: HTML instructions template.

    Raises:
        302: Redirects if session template state is inconsistent.
    """

    # Redirect to correct template. Prevents user accessing incorrect test page.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "instructions":
        return redirect(url_for(f"{session['template']}.{session['template']}"))

    # Render the appropriate template
    return render_template(f"pages/{session['template']}.html")
