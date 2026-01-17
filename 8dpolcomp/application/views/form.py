
import json
import logging
import os

from flask import Blueprint, render_template, session, request, redirect, url_for, current_app


logger = logging.getLogger(__name__)


v = Blueprint("form", __name__)


@v.route("/form", methods=["GET"])
def form():
    """
    Render the demographics form page.

    Args:
        None

    Returns:
        Response: HTML form template.

    Raises:
        302: Redirects if session template state is inconsistent.
        500: Logs file read errors and redirects to instructions.
    """

    # Redirect to correct template. Prevents user accessing incorrect test page.
    if not "template" in session:
        session["template"] = "instructions"
    if session["template"] != "form":
        return redirect(url_for(f"{session['template']}.{session['template']}"))

    try:
        demo_path = os.path.join(current_app.config["REL_DIR"], "application/data/demographics/demographics.json")
        with open(demo_path, "r", encoding="utf-8") as f:
            demo = json.load(f)
            f.close()
    except Exception:
        logger.exception("[/form] Failed to load demographics.json")
        session["template"] = "form"
        return render_template(f"pages/{session['template']}.html", site_key=current_app.config["HCAPTCHA_SITE_KEY"], demo={})

    session["template"] = "form"
    return render_template(f"pages/{session['template']}.html", site_key=current_app.config["HCAPTCHA_SITE_KEY"], demo=demo)
