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
from flask import Flask, request, session
from flask_cors import CORS
from flask_socketio import SocketIO
from werkzeug.middleware.proxy_fix import ProxyFix
from db import init_db

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

# 🧠 Agente de Bingo
import os
from litellm import completion

from ai.agente_bingo import preguntar_agente_bingo

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
# ▶️ Arranque local
# =========================
if __name__ == "__main__":
    socketio.run(
        app,
        host="0.0.0.0",
        port=5000,
        debug=not IS_PROD,
        allow_unsafe_werkzeug=True  # Considera eliminar esto en producción
    )