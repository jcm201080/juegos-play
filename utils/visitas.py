from flask import request, session
from db import get_connection

def registrar_visita(ruta=None):
    ip = request.remote_addr
    user_agent = request.headers.get("User-Agent")
    ruta_final = ruta if ruta else request.path
    user_id = session.get("user_id")  # Puede ser None si es invitado

    conn = get_connection()
    cur = conn.cursor()

    cur.execute(
        """
        INSERT INTO visitas (ip, user_agent, ruta, user_id)
        VALUES (?, ?, ?, ?)
        """,
        (ip, user_agent, ruta_final, user_id)
    )

    conn.commit()
    conn.close()
