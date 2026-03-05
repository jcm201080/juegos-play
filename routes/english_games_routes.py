# routes/english_games_routes.py

from flask import Blueprint, render_template, request, jsonify, session
from db import get_connection
from routes.auth_routes import login_required
from ai.agentes.agente_english import generar_nivel_english

english_games_bp = Blueprint("english_games", __name__)


# 🔹 Página del juego
@english_games_bp.route("/english-games")
@login_required
def english_games():
    return render_template("english_games.html")


# 🔹 Guardar puntuación del juego de colores en inglés
@english_games_bp.route("/api/english-colors/save-score", methods=["POST"])
def save_english_colors_score():
    # Comprobar que hay usuario logueado
    user_id = session.get("user_id")
    if not user_id:
        return jsonify({"ok": False, "error": "not_logged_in"}), 401

    data = request.get_json(silent=True) or {}

    level = int(data.get("level", 1))
    score = int(data.get("score", 0))
    duration_sec = int(data.get("duration_sec", 0))

    conn = get_connection()
    cur = conn.cursor()

    # Insertar partida
    cur.execute(
        """
        INSERT INTO english_color_scores (user_id, level, score, duration_sec)
        VALUES (?, ?, ?, ?)
        """,
        (user_id, level, score, duration_sec),
    )
    conn.commit()

    # Mejor puntuación global de este juego
    cur.execute(
        "SELECT COALESCE(MAX(score), 0) FROM english_color_scores WHERE user_id = ?",
        (user_id,),
    )
    best_global = cur.fetchone()[0] or 0

    # Puntuación acumulada en este juego
    cur.execute(
        "SELECT COALESCE(SUM(score), 0) FROM english_color_scores WHERE user_id = ?",
        (user_id,),
    )
    total_score = cur.fetchone()[0] or 0

    # Mejor puntuación en este nivel concreto
    cur.execute(
        """
        SELECT COALESCE(MAX(score), 0)
        FROM english_color_scores
        WHERE user_id = ? AND level = ?
        """,
        (user_id, level),
    )
    best_level = cur.fetchone()[0] or 0

    conn.close()

    return jsonify(
        {
            "ok": True,
            "best_global": best_global,
            "total_score": total_score,
            "best_level": best_level,
        }
    )
@english_games_bp.route("/api/english-colors/ranking")
def english_colors_ranking():
    conn = get_connection()
    cur = conn.cursor()

    # Top 10 por mejor puntuación global en este juego
    cur.execute(
        """
        SELECT u.username,
               MAX(s.score) AS best_score,
               COUNT(*)     AS games_played
        FROM english_color_scores s
        JOIN users u ON u.id = s.user_id
        GROUP BY s.user_id
        ORDER BY best_score DESC
        LIMIT 10
        """
    )
    rows = cur.fetchall()
    conn.close()

    ranking = []
    for idx, row in enumerate(rows, start=1):
        ranking.append(
            {
                "position": idx,
                "username": row["username"],
                "best_score": row["best_score"],
                "games_played": row["games_played"],
            }
        )

    return jsonify({"ok": True, "ranking": ranking})


# 🔹 Generar nivel con IA
@english_games_bp.route("/api/english/generate-level")
def generate_english_level():

    level = request.args.get("level", 6)

    try:
        level = int(level)
    except:
        level = 6

    data = generar_nivel_english(level)

    if not data:
        return jsonify({
            "ok": False,
            "error": "ai_generation_failed"
        })

    return jsonify({
        "ok": True,
        "level": level,
        "data": data
    })


@english_games_bp.route("/api/english/next-level")
@login_required
def next_level():

    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "SELECT current_level FROM english_user_progress WHERE user_id = ?",
        (user_id,)
    )

    row = cur.fetchone()

    if row:
        level = row["current_level"]
    else:
        level = 1
        cur.execute(
            "INSERT INTO english_user_progress (user_id, current_level) VALUES (?,1)",
            (user_id,)
        )
        conn.commit()

    conn.close()

    data = generar_nivel_english(level)

    return jsonify({
        "ok": True,
        "level": level,
        "data": data
    })

@english_games_bp.route("/api/english/complete-level", methods=["POST"])
@login_required
def complete_level():

    user_id = session["user_id"]

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "UPDATE english_user_progress SET current_level = current_level + 1 WHERE user_id = ?",
        (user_id,)
    )

    conn.commit()
    conn.close()

    return jsonify({"ok": True})


# routes/english_games_routes.py

@english_games_bp.route("/api/english/generate-image", methods=["POST"])
@login_required
def generate_image():
    """
    Endpoint para generar imágenes bajo demanda
    """
    data = request.get_json(silent=True) or {}
    prompt = data.get("prompt")
    estilo = data.get("estilo", "cartoon")
    
    if not prompt:
        return jsonify({"ok": False, "error": "prompt_required"}), 400
    
    # Importar la función del agente
    from ai.agentes.agente_english import generar_o_obtener_imagen
    
    image_url = generar_o_obtener_imagen(prompt, estilo)
    
    if image_url:
        return jsonify({
            "ok": True,
            "image_url": image_url
        })
    else:
        return jsonify({
            "ok": False,
            "error": "image_generation_failed"
        }), 500


@english_games_bp.route("/api/english/user-stats")
@login_required
def user_stats():
    """
    Obtener estadísticas del usuario para personalizar dificultad
    """
    user_id = session["user_id"]
    
    conn = get_connection()
    cur = conn.cursor()
    
    # Tiempo medio por nivel
    cur.execute("""
        SELECT AVG(duration_sec) as avg_time, 
               AVG(score) as avg_score,
               COUNT(*) as games_played
        FROM english_color_scores 
        WHERE user_id = ?
    """, (user_id,))
    
    stats = dict(cur.fetchone() or {})
    conn.close()
    
    return jsonify({
        "ok": True,
        "stats": stats
    })