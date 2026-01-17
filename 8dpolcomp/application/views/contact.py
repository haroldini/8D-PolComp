
import logging

from flask import Blueprint, render_template


logger = logging.getLogger(__name__)


v = Blueprint("contact", __name__)


@v.route("/contact", methods=["GET"])
def contact():
    """
    Render the contact page.

    Args:
        None

    Returns:
        Response: HTML contact template.

    Raises:
        None
    """

    return render_template("pages/contact.html")
