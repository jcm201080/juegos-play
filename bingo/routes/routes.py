from flask import Blueprint, render_template
from routes.auth_routes import login_required

bingo_bp = Blueprint(
    "bingo",
    __name__,
    url_prefix="/bingo"
)

@bingo_bp.route("/")
@login_required
def bingo_home():
    return render_template("bingo/home_bingo.html")


