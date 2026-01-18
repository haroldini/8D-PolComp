

import logging

from flask import Blueprint, send_from_directory


logger = logging.getLogger(__name__)


v = Blueprint("ads", __name__)


@v.route("/ads.txt")
def ads_txt():
    return send_from_directory("static", "ads.txt")




