from flask import Blueprint, render_template, redirect, url_for
from routes.auth_routes import login_required
from config import BOLA_INTERVAL_SECONDS


from os import path

BASE_DIR = path.dirname(__file__)

# 🔵 Blueprint exclusivo del bingo ONLINE
bingo_online_routes = Blueprint(
    "bingo_online",
    __name__,
    template_folder=path.join(BASE_DIR, "..", "templates")
)



# =========================
# 🏠 HOME BINGO ONLINE
# =========================
@bingo_online_routes.route("/bingo/online")
@login_required
def bingo_online_home():
    return render_template(
        "bingo_online.html",
        BOLA_INTERVAL_SECONDS=BOLA_INTERVAL_SECONDS
    )



# =========================
# 🎯 SALA ONLINE
# =========================
@bingo_online_routes.route("/bingo/online/<codigo>")
@login_required
def bingo_online_sala(codigo):
    return render_template(
        "sala/bingo_sala_online.html",
        codigo=codigo,
        IS_ONLINE=True,
        BOLA_INTERVAL_SECONDS=BOLA_INTERVAL_SECONDS
    )


