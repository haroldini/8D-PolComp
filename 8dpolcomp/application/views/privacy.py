
import logging

from flask import Blueprint, render_template


logger = logging.getLogger(__name__)


v = Blueprint("privacy", __name__)


@v.route("/privacy", methods=["GET"])
def privacy():
    """
    Render the privacy page.

    Args:
        None

    Returns:
        Response: HTML privacy template.

    Raises:
        None
    """

    return render_template("pages/privacy.html")
