# =========================
# ⚙️ Detectar entorno
# =========================
import os
import json
from dotenv import load_dotenv
import logging  # Importar logging para manejar errores

# Cargar las variables de entorno desde un archivo .env
load_dotenv()

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
IS_PROD = os.environ.get("FLASK_ENV") == "production"

# =================
# Version
# =================
def get_app_version():
    """Obtiene la versión de la aplicación desde package.json."""
    try:
        with open(os.path.join(BASE_DIR, "package.json"), "r", encoding="utf-8") as f:
            return json.load(f).get("version", "unknown")
    except FileNotFoundError:  # Manejar solo el error de archivo no encontrado
        logging.error("El archivo package.json no se encontró.")
        return "unknown"
    except json.JSONDecodeError:  # Manejar errores de decodificación JSON
        logging.error("Error al decodificar JSON en package.json.")
        return "unknown"

APP_VERSION = get_app_version()

import eventlet
eventlet.monkey_patch()  # Habilitar monkey patch para compatibilidad con Socket.IO

# =========================
# 📦 Imports Flask
# =========================
from flask import Flask, request, session, jsonify
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix
from db import init_db, get_connection

# =========================
# 📦 Blueprints
# =========================
from routes.main_routes import main_bp
from routes.auth_routes import auth_bp
from routes.juego_mate_routes import game_bp
from routes.puzzle_routes import puzzle_bp
from routes.english_games_routes import english_games_bp
from routes.oca_online_apy import oca_api
from routes.chess import chess_routes
from routes.admin_routes import admin_bp

# ♟️ Chess sockets
from routes.chess_socket import register_chess_sockets
from routes.chess_rooms import register_chess_rooms

# 🎱 Bingo CLASSIC
from bingo.classic.routes.bingo_routes import bingo_routes
from bingo.classic.sockets.bingo_socket import register_bingo_sockets
from bingo.routes.routes import bingo_bp  # 🏆 Bingo Ranking
from bingo.routes.ranking_routes import ranking_bp

# 🎱 Bingo ONLINE
from bingo.bingo_online.routes.bingo_online_routes import bingo_online_routes
from bingo.bingo_online.sockets.bingo_online_socket import register_bingo_online_sockets
from bingo.classic.sockets.bingo_socket import salas_bingo
# En app.py, añadir:

# puzzle
from math_puzzle.routes.math_puzzle_routes import math_puzzle_bp



from routes.perfil_routes import perfil_bp


# 🧠 Agente de Bingo
import os
from litellm import completion

from ai.agentes.agente_bingo import preguntar_agente_bingo

from utils.visitas import registrar_visita

import config
from config_validator import validate_config

# Validar la configuración de la aplicación
try:
    validate_config(config)
except ValueError as e:
    logging.error(f"Configuration validation failed: {e}")
    exit(1)

# =========================
# 🚀 Crear app
# =========================
app = Flask(__name__)

# Configuración de ProxyFix SOLO en producción (cuando hay Nginx)
if IS_PROD:
    app.wsgi_app = ProxyFix(app.wsgi_app, x_proto=1, x_host=1)

# =========================
# 🔑 Configuración básica
# =========================
app.config["SECRET_KEY"] = os.getenv("SECRET_KEY", "dev-key")  # Clave secreta para sesiones
app.config["TEMPLATES_AUTO_RELOAD"] = not IS_PROD  # Recargar plantillas en desarrollo
app.config["SEND_FILE_MAX_AGE_DEFAULT"] = 0  # Desactivar caché de archivos

# =========================
# 🍪 Cookies seguras
# =========================
app.config.update(
    SESSION_COOKIE_SAMESITE="Lax",  # Configuración de seguridad para cookies
    SESSION_COOKIE_SECURE=IS_PROD,  # Cookies seguras solo en producción
)

# =========================
# 🔑 Base de datos
# =========================
init_db()  # Inicializar la base de datos

# =========================
# 👀 Contar visitas
# =========================
@app.before_request
def contar_visitas():
    """Contar las visitas a la aplicación y registrar visitas únicas."""
    if request.path.startswith("/static"):
        return  # Ignorar rutas estáticas
    if request.path.startswith("/api/track"):
        return  # Ignorar seguimiento de API
    if request.path in ("/favicon.ico", "/robots.txt"):
        return  # Ignorar favicon y robots.txt

    if not session.get("visitado"):  # Si no se ha visitado la página
        session["visitado"] = True
        session["ruta_entrada"] = request.path
        registrar_visita()  # Registrar visita

# =========================
# 📌 Version global
# =========================
@app.context_processor
def inject_app_version():
    """Inyectar la versión de la aplicación en el contexto de las plantillas."""
    return dict(APP_VERSION=APP_VERSION)

# =========================
# 🔌 Socket.IO
# =========================
socketio = SocketIO(
    app,
    cors_allowed_origins="*",  # Considera restringir esto en producción
    async_mode="eventlet"
)

# =========================
# 🔗 Registrar sockets
# =========================
register_chess_sockets(socketio)
register_chess_rooms(socketio)
register_bingo_sockets(socketio)
register_bingo_online_sockets(socketio)

# =========================
# 🌍 CORS
# =========================
CORS(app, supports_credentials=True)  # Habilitar CORS con soporte para credenciales

# =========================
# 🧠 Blueprints
# =========================
app.register_blueprint(main_bp)
app.register_blueprint(auth_bp)
app.register_blueprint(game_bp)
app.register_blueprint(puzzle_bp)
app.register_blueprint(english_games_bp)
app.register_blueprint(oca_api)
app.register_blueprint(chess_routes)
app.register_blueprint(bingo_bp)
app.register_blueprint(bingo_routes)
app.register_blueprint(bingo_online_routes)
app.register_blueprint(ranking_bp)
app.register_blueprint(admin_bp)
app.register_blueprint(perfil_bp)
app.register_blueprint(math_puzzle_bp)

# =========================
# 🧠 Agente general
# =========================
from ai.agente_router import preguntar_agente_general

@app.route("/api/ai", methods=["POST"])
def ai_general():

    data = request.get_json(silent=True) or {}

    pregunta = data.get("mensaje") or data.get("pregunta") or ""

    pagina = request.path.lower()

    if not pregunta:
        return {"respuesta": "No he recibido ninguna pregunta."}

    usuario = None

    if "user_id" in session:

        conn = get_connection()
        cur = conn.cursor()

        cur.execute("""
        SELECT username, avatar, total_score, level_unlocked
        FROM users
        WHERE id = ?
        """, (session["user_id"],))

        row = cur.fetchone()
        conn.close()

        if row:
            usuario = {
                "username": row["username"],
                "avatar": row["avatar"],
                "score": row["total_score"],
                "level": row["level_unlocked"]
            }

    respuesta = preguntar_agente_general(pregunta, pagina, usuario=usuario)

    return {"respuesta": respuesta}
# =========================
# 🎱 Bingo AI
# =========================
from bingo.classic.sockets.bingo_socket import salas_bingo as salas_bingo_classic
from bingo.bingo_online.state import salas_bingo_online

@app.route("/api/bingo-ai", methods=["POST"])
def bingo_ai():

    try:

        data = request.get_json(silent=True) or {}

        pregunta = data.get("mensaje", "")
        codigo = data.get("codigo")

        if not pregunta:
            return {"respuesta": "No he recibido ninguna pregunta."}

        # 🔎 Buscar la sala en classic u online
        sala = salas_bingo_classic.get(codigo) or salas_bingo_online.get(codigo)

        contexto_partida = {}

        if sala:

            historial = sala["bombo"].historial

            contexto_partida = {
                "jugadores": [j["nombre"] for j in sala["jugadores"].values()],
                "ultima_bola": historial[-1] if historial else None,
                "bolas_recientes": historial[-10:],
                "linea_cantada": sala.get("linea_cantada") or sala.get("premios", {}).get("linea"),
                "bingo_cantado": sala.get("bingo_cantado") or sala.get("premios", {}).get("bingo")
            }

        respuesta = preguntar_agente_bingo(pregunta, contexto_partida)

        return {"respuesta": respuesta}

    except Exception as e:

        print("Error IA:", e)

        return {"respuesta": "⚠️ Error en el servidor de IA"}

# =========================
# 🔗 Endpoint para el agente del portfolio
# =========================
@app.route("/api/agente-portfolio", methods=["POST"])
def agente_para_portfolio():
    """
    Endpoint específico para que el agente del portfolio consulte información
    sobre los juegos. Más permisivo y con contexto adaptado.
    """
    try:
        data = request.get_json(silent=True) or {}

        pregunta = data.get("mensaje") or data.get("pregunta") or ""

        # detectar página automáticamente
        pagina = request.path.lower()
        
        if not pregunta:
            return jsonify({
                "respuesta": "No he recibido ninguna pregunta.",
                "fuente": "agente_juegos"
            })
        
        # Usar el agente general de juegos (que ya tiene su propio router)
        respuesta = preguntar_agente_general(pregunta, pagina="general")
        
        # Añadir un pequeño contexto extra si la respuesta es muy corta
        if len(respuesta) < 50:
            respuesta += "\n\nPuedes ver todos los juegos en: https://juegos.jesuscmweb.com"
        
        return jsonify({
            "respuesta": respuesta,
            "fuente": "agente_juegos"
        })
        
    except Exception as e:
        print(f"Error en agente-para-portfolio: {e}")
        return jsonify({
            "respuesta": "Los juegos están disponibles en https://juegos.jesuscmweb.com. Tenemos Bingo, puzzles, juegos de matemáticas y más.",
            "fuente": "agente_juegos_fallback"
        })

# Endpoint de prueba para verificar que el agente responde
@app.route("/api/agente-portfolio/test", methods=["GET"])
def test_agente_portfolio():
    return jsonify({
        "status": "ok",
        "mensaje": "Endpoint del agente de juegos para portfolio activo",
        "juegos": ["bingo", "puzzle", "math", "english", "chess"]
    })


# app.py - Añadir al final de las importaciones (al principio del archivo)
from tetris.routes.tetris_routes import tetris_bp

# app.py - Añadir después de registrar los otros blueprints
# (busca donde registras los blueprints del bingo y añade esta línea)
app.register_blueprint(tetris_bp)

# También necesitaremos el endpoint para el agente IA del Tetris
# Esto va en ai/agente_router.py, pero por ahora podemos añadir una ruta temporal
# en app.py para probar:

@app.route('/api/tetris-ai', methods=['POST'])
def tetris_ai_temporal():
    """Endpoint temporal para el asistente IA del Tetris"""
    from flask import jsonify
    import random
    
    data = request.json
    puntuacion = data.get('puntuacion', 0)
    nivel = data.get('nivel', 1)
    
    # Consejos aleatorios por ahora (luego lo conectaremos con tu agente real)
    consejos = [
        "¡Intenta hacer Tetris (4 líneas) para más puntos!",
        "Guarda el hueco para la pieza larga (I)",
        "No dejes huecos aislados",
        "Intenta mantener el tablero plano",
        "La pieza T es útil para girar en espacios pequeños",
        f"Vas bien, ¡{puntuacion} puntos! Sigue así",
        "Si puedes, coloca las piezas en los bordes",
        "Mira la siguiente pieza y planifica"
    ]
    
    return jsonify({
        'success': True,
        'consejo': random.choice(consejos)
    })

# =========================
# ▶️ Arranque local
# =========================
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5001,
        debug=not IS_PROD,
        allow_unsafe_werkzeug=True  # Considera eliminar esto en producción
    )