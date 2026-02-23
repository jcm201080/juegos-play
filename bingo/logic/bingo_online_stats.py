# bingo/bingo_online/logic/bingo_online_stats.py

from db import get_connection


# =========================
# ASEGURAR FILA DE STATS
# =========================
def ensure_bingo_online_stats(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT OR IGNORE INTO bingo_online_stats (user_id)
        VALUES (?)
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()


# =========================
# CREAR PARTIDA ONLINE
# =========================
def crear_partida_online(jugadores):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO bingo_online_partidas (jugadores)
        VALUES (?)
        """,
        (jugadores,)
    )

    partida_id = cur.lastrowid
    conn.commit()
    conn.close()

    return partida_id


# =========================
# REGISTRAR LÍNEA
# =========================
def registrar_linea_online(user_id, partida_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO bingo_online_stats (user_id) VALUES (?)",
        (user_id,)
    )

    cur.execute(
        """
        UPDATE bingo_online_stats
        SET lineas = lineas + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    cur.execute(
        """
        INSERT INTO bingo_online_eventos (partida_id, user_id, tipo)
        VALUES (?, ?, 'linea')
        """,
        (partida_id, user_id)
    )

    conn.commit()
    conn.close()


# =========================
# REGISTRAR CRUZ
# =========================
def registrar_cruz_online(user_id, partida_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO bingo_online_stats (user_id) VALUES (?)",
        (user_id,)
    )

    cur.execute(
        """
        UPDATE bingo_online_stats
        SET cruces = cruces + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    cur.execute(
        """
        INSERT INTO bingo_online_eventos (partida_id, user_id, tipo)
        VALUES (?, ?, 'cruz')
        """,
        (partida_id, user_id)
    )

    conn.commit()
    conn.close()


# =========================
# REGISTRAR X
# =========================
def registrar_x_online(user_id, partida_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO bingo_online_stats (user_id) VALUES (?)",
        (user_id,)
    )

    cur.execute(
        """
        UPDATE bingo_online_stats
        SET x = x + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    cur.execute(
        """
        INSERT INTO bingo_online_eventos (partida_id, user_id, tipo)
        VALUES (?, ?, 'x')
        """,
        (partida_id, user_id)
    )

    conn.commit()
    conn.close()


# =========================
# REGISTRAR BINGO
# =========================
def registrar_bingo_online(user_id, partida_id, duracion_sec):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO bingo_online_stats (user_id) VALUES (?)",
        (user_id,)
    )

    cur.execute(
        """
        UPDATE bingo_online_stats
        SET bingos = bingos + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    cur.execute(
        """
        UPDATE bingo_online_partidas
        SET ganador_id = ?, duracion_sec = ?
        WHERE id = ?
        """,
        (user_id, duracion_sec, partida_id)
    )

    cur.execute(
        """
        INSERT INTO bingo_online_eventos (partida_id, user_id, tipo)
        VALUES (?, ?, 'bingo')
        """,
        (partida_id, user_id)
    )

    conn.commit()
    conn.close()


# =========================
# PARTIDA JUGADA
# =========================
def registrar_partida_online(user_id):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO bingo_online_stats (user_id) VALUES (?)",
        (user_id,)
    )

    cur.execute(
        """
        UPDATE bingo_online_stats
        SET partidas_jugadas = partidas_jugadas + 1
        WHERE user_id = ?
        """,
        (user_id,)
    )

    conn.commit()
    conn.close()


# =========================
# SUMAR PUNTOS
# =========================
def sumar_puntos_online(user_id, puntos):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        "INSERT OR IGNORE INTO bingo_online_stats (user_id) VALUES (?)",
        (user_id,)
    )

    cur.execute(
        """
        UPDATE bingo_online_stats
        SET puntos_totales = puntos_totales + ?
        WHERE user_id = ?
        """,
        (puntos, user_id)
    )

    conn.commit()
    conn.close()


# =========================
# RANKING ONLINE
# =========================
def obtener_ranking_online(limit=20):
    conn = get_connection()
    cur = conn.cursor()

    cur.execute("""
        SELECT 
            u.username,
            bos.partidas_jugadas,
            bos.bingos,
            bos.lineas,
            bos.cruces,
            bos.x,
            bos.puntos_totales
        FROM bingo_online_stats bos
        JOIN users u ON u.id = bos.user_id
        ORDER BY bos.puntos_totales DESC
        LIMIT ?
    """, (limit,))

    rows = cur.fetchall()
    conn.close()

    return [dict(row) for row in rows]



