import os
import sqlite3


import hashlib

def hash_password(password: str) -> str:
    return hashlib.sha256(password.encode("utf-8")).hexdigest()


BASE_DIR = os.path.dirname(os.path.abspath(__file__))

DB_FOLDER = os.path.join(BASE_DIR, "database")
os.makedirs(DB_FOLDER, exist_ok=True)

DB_NAME = os.path.join(DB_FOLDER, "play.db")


def get_connection():
    conn = sqlite3.connect(DB_NAME)
    conn.row_factory = sqlite3.Row
    return conn



def init_db():
    conn = get_connection()
    cur = conn.cursor()

    # Tabla de usuarios
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS users (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            email TEXT NOT NULL UNIQUE,
            username TEXT NOT NULL UNIQUE,
            password_hash TEXT NOT NULL,
            best_score INTEGER DEFAULT 0,
            total_score INTEGER DEFAULT 0,
            level_unlocked INTEGER DEFAULT 1,
            role TEXT DEFAULT 'user',
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            reset_token TEXT,
            reset_expires TEXT
        );

        """
    )

    # Tabla de puntuaciones por partida/nivel
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level INTEGER NOT NULL,
            score INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    # 🔹 NUEVA TABLA: partidas del Puzzle Matemático
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS puzzle_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            difficulty TEXT NOT NULL,      -- easy / medium / pro / infernal
            solved INTEGER NOT NULL,       -- operaciones correctas
            total_eq INTEGER NOT NULL,     -- total de operaciones del puzzle
            mistakes INTEGER NOT NULL,     -- fallos cometidos
            lives_left INTEGER NOT NULL,   -- vidas restantes al final
            duration_sec INTEGER NOT NULL, -- duración de la partida en segundos
            score INTEGER NOT NULL,        -- puntuación calculada
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

        # 🔹 NUEVA TABLA: puntuaciones del juego de colores en inglés
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS english_color_scores (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            user_id INTEGER NOT NULL,
            level INTEGER NOT NULL,
            score INTEGER NOT NULL,
            duration_sec INTEGER NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

   
    # 🔹 NUEVA TABLA: visitas a la web
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS visitas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            fecha TEXT DEFAULT CURRENT_TIMESTAMP,
            ip TEXT,
            user_agent TEXT,
            ruta TEXT,
            user_id INTEGER,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )

        """
    )

    # =====================================================
    # 🔹 TABLAS PARA EL BINGO
    # =====================================================

    # Estadísticas acumuladas por usuario
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bingo_stats (
            user_id INTEGER PRIMARY KEY,
            partidas_jugadas INTEGER DEFAULT 0,
            lineas INTEGER DEFAULT 0,
            cruces INTEGER DEFAULT 0,
            x INTEGER DEFAULT 0,
            bingos INTEGER DEFAULT 0,
            bingos_fallidos INTEGER DEFAULT 0,
            puntos_totales INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )

        """
    )

    # Historial de partidas de bingo
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bingo_partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ganador_id INTEGER,
            duracion_sec INTEGER,
            jugadores INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(ganador_id) REFERENCES users(id)
        )
        """
    )

    # Eventos dentro de una partida (línea, cruce, bingo…)
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bingo_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL, -- linea | cruce | bingo | bingo_fallido
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(partida_id) REFERENCES bingo_partidas(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    # =====================================================
    # 🔹 TABLAS PARA EL BINGO ONLINE
    # =====================================================

    # Estadísticas acumuladas online por usuario
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bingo_online_stats (
            user_id INTEGER PRIMARY KEY,
            partidas_jugadas INTEGER DEFAULT 0,
            lineas INTEGER DEFAULT 0,
            cruces INTEGER DEFAULT 0,
            x INTEGER DEFAULT 0,
            bingos INTEGER DEFAULT 0,
            bingos_fallidos INTEGER DEFAULT 0,
            puntos_totales INTEGER DEFAULT 0,
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    # Historial de partidas online
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bingo_online_partidas (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            ganador_id INTEGER,
            duracion_sec INTEGER,
            jugadores INTEGER,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(ganador_id) REFERENCES users(id)
        )
        """
    )

    # Eventos online
    cur.execute(
        """
        CREATE TABLE IF NOT EXISTS bingo_online_eventos (
            id INTEGER PRIMARY KEY AUTOINCREMENT,
            partida_id INTEGER NOT NULL,
            user_id INTEGER NOT NULL,
            tipo TEXT NOT NULL,
            created_at TEXT DEFAULT CURRENT_TIMESTAMP,
            FOREIGN KEY(partida_id) REFERENCES bingo_online_partidas(id),
            FOREIGN KEY(user_id) REFERENCES users(id)
        )
        """
    )

    # ===============================
    # 👤 USUARIOS POR DEFECTO
    # ===============================

    # ---- ADMIN ----
    cur.execute("SELECT id FROM users WHERE email = ?", ("jcm201080@gmail.com",))
    admin_exists = cur.fetchone()

    if not admin_exists:
        cur.execute("""
            INSERT INTO users 
            (email, username, password_hash, role, best_score, total_score, level_unlocked)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "jcm201080@gmail.com",
            "jcm",
            hash_password("1234"),
            "admin",
            0,
            0,
            1
        ))

    # ---- USER NORMAL ----
    cur.execute("SELECT id FROM users WHERE email = ?", ("jcm201080@hotmail.com",))
    user_exists = cur.fetchone()

    if not user_exists:
        cur.execute("""
            INSERT INTO users 
            (email, username, password_hash, role, best_score, total_score, level_unlocked)
            VALUES (?, ?, ?, ?, ?, ?, ?)
        """, (
            "jcm201080@hotmail.com",
            "jesus",
            hash_password("1234"),
            "user",
            0,
            0,
            1
        ))

    # ---- BOTS ONLINE ----
    bots = [
        ("ismael@play.com", "Ismael RM"),
        ("juan_bot@play.com", "Juan"),
        ("irene@play.com", "Irene G"),
    ]

    for email, username in bots:
        cur.execute("SELECT id FROM users WHERE email = ?", (email,))
        if not cur.fetchone():
            cur.execute("""
                INSERT INTO users
                (email, username, password_hash, role)
                VALUES (?, ?, ?, ?)
            """, (
                email,
                username,
                hash_password("bot123"),
                "bot"
            ))


    for username, stats in [
        ("Ismael RM", (25, 12, 8, 6, 4, 120)),
        ("Juan", (40, 18, 11, 9, 7, 210)),
        ("Irene G", (15, 5, 3, 2, 1, 55)),
    ]:
        cur.execute("""
            INSERT OR IGNORE INTO bingo_online_stats
            (user_id, partidas_jugadas, lineas, cruces, x, bingos, puntos_totales)
            SELECT id, ?, ?, ?, ?, ?, ?
            FROM users WHERE username = ?
        """, (*stats, username))


            


    conn.commit()
    conn.close()




    
def ensure_bingo_stats(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT OR IGNORE INTO bingo_stats (user_id)
        VALUES (?)
    """, (user_id,))

    conn.commit()
    conn.close()


def sumar_partida(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bingo_stats (user_id, partidas_jugadas)
        VALUES (?, 1)
        ON CONFLICT(user_id) DO UPDATE SET
            partidas_jugadas = partidas_jugadas + 1
    """, (user_id,))

    conn.commit()
    conn.close()

def sumar_evento(user_id, tipo):
    campo = {
        "linea": "lineas",
        "cruce": "cruces",
        "bingo": "bingos",
        "bingo_fallido": "bingos_fallidos"
    }.get(tipo)

    if not campo:
        return

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(f"""
        INSERT INTO bingo_stats (user_id, {campo})
        VALUES (?, 1)
        ON CONFLICT(user_id) DO UPDATE SET
            {campo} = {campo} + 1
    """, (user_id,))

    conn.commit()
    conn.close()


def crear_partida_bingo(ganador_id, duracion, jugadores):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bingo_partidas (ganador_id, duracion_sec, jugadores)
        VALUES (?, ?, ?)
    """, (ganador_id, duracion, jugadores))

    partida_id = cur.lastrowid
    conn.commit()
    conn.close()

    return partida_id


def registrar_evento(partida_id, user_id, tipo):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        INSERT INTO bingo_eventos (partida_id, user_id, tipo)
        VALUES (?, ?, ?)
    """, (partida_id, user_id, tipo))

    conn.commit()
    conn.close()


#Contar usuarios:
def contar_usuarios():
    conn = get_connection()
    cur = conn.cursor()
    cur.execute("SELECT COUNT(*) FROM users")
    total = cur.fetchone()[0]
    conn.close()
    return total
