# config.py
import os
from dotenv import load_dotenv

load_dotenv()

# ==========================
# 🔐 SEGURIDAD
# ==========================
SECRET_KEY = os.getenv("SECRET_KEY")

# ==========================
# 🎱 BINGO – JUGADORES
# ==========================
BINGO_MIN_PLAYERS = int(os.getenv("BINGO_MIN_PLAYERS", 1))
BINGO_MAX_PLAYERS = int(os.getenv("BINGO_MAX_PLAYERS", 10))

# ==========================
# 🎟️ CARTONES
# ==========================
BINGO_MIN_CARTONES = int(os.getenv("BINGO_MIN_CARTONES", 1))
BINGO_MAX_CARTONES = int(os.getenv("BINGO_MAX_CARTONES", 4))

# ==========================
# 🌐 ONLINE
# ==========================
ONLINE_COUNTDOWN_SECONDS = int(os.getenv("ONLINE_COUNTDOWN_SECONDS", 30))
ONLINE_MAX_PLAYERS = int(os.getenv("ONLINE_MAX_PLAYERS", 20))
BOLA_INTERVAL_SECONDS = int(os.getenv("BOLA_INTERVAL_SECONDS", 5))


# 🤖 BOTS
BOT_MIN_DELAY = float(os.getenv("BOT_MIN_DELAY", 2.5))
BOT_MAX_DELAY = float(os.getenv("BOT_MAX_DELAY", 5.0))


