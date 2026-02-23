from flask import Blueprint, render_template
from bingo.logic.bingo_stats import obtener_ranking_classic
from bingo.logic.bingo_online_stats import obtener_ranking_online
from db import get_connection

ranking_bp = Blueprint("ranking", __name__, url_prefix="/bingo")


@ranking_bp.route("/ranking")
def ranking():
    ranking_classic = obtener_ranking_classic()
    ranking_online = obtener_ranking_online()

    # 🔥 Ranking combinado
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            u.username,
            COALESCE(c.puntos_totales,0) AS puntos_classic,
            COALESCE(o.puntos_totales,0) AS puntos_online,
            COALESCE(c.puntos_totales,0) + COALESCE(o.puntos_totales,0) AS puntos_totales
        FROM users u
        LEFT JOIN bingo_stats c ON c.user_id = u.id
        LEFT JOIN bingo_online_stats o ON o.user_id = u.id
        ORDER BY puntos_totales DESC
    """)

    ranking_global = [dict(row) for row in cur.fetchall()]
    conn.close()

    return render_template(
        "bingo/ranking.html",
        ranking_classic=ranking_classic,
        ranking_online=ranking_online,
        ranking_global=ranking_global
    )
