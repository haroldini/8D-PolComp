
import logging
from uuid import UUID

from flask import Blueprint, render_template, session, request, redirect, url_for


logger = logging.getLogger(__name__)


v = Blueprint("instructions", __name__)


def _try_parse_uuid(s: str) -> str | None:
    try:
        return str(UUID(str(s)))
    except Exception:
        return None


@v.route("/instructions", methods=["GET"])
def instructions():
    """
    Render the instructions page.

    Args:
        None

    Returns:
        Response: HTML instructions template.

    Raises:
        302: Redirects to the correct template if session state is invalid.
    """
    # Optional group param
    g = request.args.get("g")
    if g is not None:
        g = str(g).strip()
        if g == "" or g.lower() in ("clear", "none", "null", "0"):
            session.pop("group_id", None)
        else:
            parsed = _try_parse_uuid(g)
            if parsed:
                session["group_id"] = parsed

    # Redirect to correct template. Prevents user accessing incorrect test page.
    if "template" not in session:
        session["template"] = "instructions"
    if session["template"] != "instructions":
        return redirect(url_for(f"{session['template']}.{session['template']}"))

    return render_template("pages/instructions.html", group_id=session.get("group_id"))
