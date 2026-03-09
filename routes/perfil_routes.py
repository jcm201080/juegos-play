from flask import Blueprint, render_template, session, redirect, url_for, request, jsonify
from db import get_connection

perfil_bp = Blueprint("perfil", __name__, url_prefix="/perfil")


@perfil_bp.route("/")
def perfil():

    if "user_id" not in session:
        return redirect(url_for("main.home"))

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, username, email, best_score, total_score,
               level_unlocked, created_at, avatar, photo
        FROM users
        WHERE id = ?
    """, (session["user_id"],))

    usuario = cur.fetchone()

    conn.close()

    return render_template("perfil/perfil.html", usuario=usuario)


@perfil_bp.route("/api/cambiar-username", methods=["POST"])
def cambiar_username():

    if "user_id" not in session:
        return jsonify({"error": "no autorizado"}), 401

    data = request.get_json()
    nuevo = data.get("username")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET username = ?
        WHERE id = ?
    """, (nuevo, session["user_id"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True})

@perfil_bp.route("/api/cambiar-avatar", methods=["POST"])
def cambiar_avatar():

    if "user_id" not in session:
        return jsonify({"error": "no autorizado"}), 401

    data = request.get_json()
    avatar = data.get("avatar")

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        UPDATE users
        SET avatar = ?
        WHERE id = ?
    """, (avatar, session["user_id"]))

    conn.commit()
    conn.close()

    return jsonify({"success": True})