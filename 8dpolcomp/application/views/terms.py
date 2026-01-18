
import logging

from flask import Blueprint, render_template


logger = logging.getLogger(__name__)


v = Blueprint("terms", __name__)


@v.route("/terms", methods=["GET"])
def terms():
    """
    Render the terms page.

    Args:
        None

    Returns:
        Response: HTML terms template.

    Raises:
        None
    """

    return render_template("pages/terms.html")
