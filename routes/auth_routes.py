# routes/auth_routes.py

from flask import Blueprint, request, jsonify, session, redirect, url_for
from db import get_connection   # 👈 CAMBIADO SI db.py ESTÁ EN database
import hashlib
import sqlite3
from functools import wraps

auth_bp = Blueprint("auth", __name__)


# =========================
# 🔐 HASH PASSWORD
# =========================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# =========================
# 📝 REGISTRO
# =========================
@auth_bp.route("/api/register", methods=["POST"])
def register():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip()
    username = (data.get("username") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not username or not password:
        return jsonify({
            "success": False,
            "error": "Email, usuario y contraseña requeridos"
        }), 400

    conn = get_connection()
    cur = conn.cursor()

    try:
        cur.execute(
            """
            INSERT INTO users (email, username, password_hash, role)
            VALUES (?, ?, ?, ?)
            """,
            (email, username, hash_password(password), "user"),
        )

        conn.commit()
        user_id = cur.lastrowid

        # ✅ Crear sesión
        session["user_id"] = user_id
        session["username"] = username
        session["role"] = "user"
        session.permanent = True

        cur.execute(
            """
            SELECT id, username, best_score, total_score, level_unlocked
            FROM users
            WHERE id = ?
            """,
            (user_id,),
        )

        user = dict(cur.fetchone())

        return jsonify({"success": True, "user": user})

    except sqlite3.IntegrityError:
        return jsonify({
            "success": False,
            "error": "Email o usuario ya existe"
        }), 409

    finally:
        conn.close()


# =========================
# 🔐 LOGIN (por email)
# =========================
@auth_bp.route("/api/login", methods=["POST"])
def login():
    data = request.get_json() or {}

    email = (data.get("email") or "").strip()
    password = (data.get("password") or "").strip()

    if not email or not password:
        return jsonify({
            "success": False,
            "error": "Email y contraseña requeridos"
        }), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, email, username, best_score, total_score,
               level_unlocked, password_hash, role
        FROM users
        WHERE email = ?
        """,
        (email,),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        return jsonify({
            "success": False,
            "error": "Usuario no encontrado"
        }), 404

    if hash_password(password) != row["password_hash"]:
        return jsonify({
            "success": False,
            "error": "Contraseña incorrecta"
        }), 401

    # ✅ Crear sesión
    session["user_id"] = row["id"]
    session["username"] = row["username"]
    session["role"] = row["role"]
    session.permanent = True

    user = {
        "id": row["id"],
        "username": row["username"],
        "best_score": row["best_score"],
        "total_score": row["total_score"],
        "level_unlocked": row["level_unlocked"],
    }

    return jsonify({"success": True, "user": user})


# =========================
# 🚪 LOGOUT
# =========================
@auth_bp.route("/api/logout", methods=["POST"])
def logout():
    session.clear()
    return jsonify({"success": True})


# =========================
# 👤 ME (sesión actual)
# =========================
@auth_bp.route("/api/me", methods=["GET"])
def me():
    user_id = session.get("user_id")

    if not user_id:
        return jsonify({"logged_in": False}), 200

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        SELECT id, username, best_score, total_score, level_unlocked
        FROM users
        WHERE id = ?
        """,
        (user_id,),
    )

    row = cur.fetchone()
    conn.close()

    if not row:
        session.clear()
        return jsonify({"logged_in": False}), 200

    next_url = session.pop("next_url", None)

    return jsonify({
        "logged_in": True,
        "user": dict(row),
        "next_url": next_url
    }), 200


# =========================
# 🔒 LOGIN REQUIRED
# =========================
def login_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            session["next_url"] = request.url

            if request.accept_mimetypes.accept_html:
                return redirect(url_for("main.home", login_required=1))

            return jsonify({"error": "login_required"}), 401

        return f(*args, **kwargs)

    return decorated


# =========================
# 👑 ADMIN REQUIRED
# =========================
def admin_required(f):
    @wraps(f)
    def decorated(*args, **kwargs):
        if "user_id" not in session:
            return redirect(url_for("main.home"))

        if session.get("role") != "admin":
            return jsonify({"error": "admin_required"}), 403

        return f(*args, **kwargs)

    return decorated
