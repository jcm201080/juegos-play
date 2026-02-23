# routes/auth_routes.py

from flask import Blueprint, request, jsonify, session, redirect, url_for
from db import get_connection   # 👈 CAMBIADO SI db.py ESTÁ EN database
import hashlib
import sqlite3
from functools import wraps
import secrets
from datetime import datetime, timedelta
from flask import jsonify, render_template
import smtplib
from email.mime.text import MIMEText
from email.mime.multipart import MIMEMultipart
import os



auth_bp = Blueprint("auth", __name__)


# =========================
# 🔐 HASH PASSWORD
# =========================
def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


# =========================
# 📧 ENVIAR EMAIL
# =========================
def send_reset_email(to_email, reset_link):
    smtp_server = "smtp.gmail.com"
    smtp_port = 587

    sender_email = os.getenv("MAIL_USER")
    sender_password = os.getenv("MAIL_PASSWORD")

    message = MIMEMultipart("alternative")
    message["Subject"] = "Recuperación de contraseña - Juegos JCM"
    message["From"] = sender_email
    message["To"] = to_email

    html = f"""
    <html>
    <body style="font-family: Arial;">
        <h2>🔐 Recuperación de contraseña</h2>
        <p>Haz clic en el botón:</p>
        <a href="{reset_link}">Restablecer contraseña</a>
        <p>Expira en 30 minutos.</p>
    </body>
    </html>
    """

    part = MIMEText(html, "html")
    message.attach(part)

    with smtplib.SMTP(smtp_server, smtp_port) as server:
        server.starttls()
        server.login(sender_email, sender_password)
        server.sendmail(sender_email, to_email, message.as_string())


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


@auth_bp.route("/recover", methods=["POST"])
def recover_password():
    data = request.get_json() or {}
    email = data.get("email", "").strip()

    if not email:
        return jsonify({"success": False, "message": "Email requerido."}), 400

    conn = get_connection()
    cur = conn.cursor()

    cur.execute("SELECT id FROM users WHERE email = ?", (email,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return jsonify({"success": False, "message": "Email no encontrado."})

    # 🔐 Generar token seguro
    token = secrets.token_urlsafe(32)

    # ⏳ Expira en 30 minutos
    expires = (datetime.utcnow() + timedelta(minutes=30)).isoformat()

    # 💾 Guardar en BD
    cur.execute("""
        UPDATE users
        SET reset_token = ?, reset_expires = ?
        WHERE id = ?
    """, (token, expires, user["id"]))

    conn.commit()
    conn.close()

    # 🖥 Enlace (modo desarrollo)
    reset_link = url_for("auth.reset_password", token=token, _external=True)
    send_reset_email(email, reset_link)
    print("🔐 ENLACE DE RECUPERACIÓN:", reset_link)

    return jsonify({
        "success": True,
        "message": "Te hemos enviado un enlace de recuperación a tu correo."
    })



@auth_bp.route("/reset/<token>", methods=["GET", "POST"])
def reset_password(token):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT id, reset_expires
        FROM users
        WHERE reset_token = ?
    """, (token,))
    user = cur.fetchone()

    if not user:
        conn.close()
        return "Token inválido", 400

    expires = datetime.fromisoformat(user["reset_expires"])

    if datetime.utcnow() > expires:
        conn.close()
        return "Token expirado", 400

    if request.method == "POST":
        new_password = request.form.get("password")
        hashed = hash_password(new_password)

        cur.execute("""
            UPDATE users
            SET password_hash = ?, reset_token = NULL, reset_expires = NULL
            WHERE id = ?
        """, (hashed, user["id"]))

        conn.commit()
        conn.close()

        return redirect(url_for("main.home", reset=1))

    conn.close()
    return render_template("reset_password.html", token=token)


   