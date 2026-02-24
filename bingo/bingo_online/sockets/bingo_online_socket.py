import random

from flask import request, session
from flask_socketio import join_room, emit, leave_room

from bingo.bingo_online.state import salas_bingo_online, online_lobbies
from bingo.bingo_online.logic.cartones import generar_carton
from bingo.bingo_online.logic.bolas import BomboBingo
from bingo.bingo_online.logic.validaciones import (
    comprobar_linea,
    comprobar_bingo,
    comprobar_cruz,
    comprobar_x
)

from bingo.bingo_online.data.bot_names import BOT_NAMES

from config import (
    ONLINE_COUNTDOWN_SECONDS,
    BOLA_INTERVAL_SECONDS,
)

from bingo.logic.bingo_online_stats import (
    ensure_bingo_online_stats,
    crear_partida_online,
    registrar_linea_online,
    registrar_cruz_online,
    registrar_x_online,
    registrar_bingo_online,
    registrar_partida_online,
    sumar_puntos_online
)

from config import BOT_MIN_DELAY, BOT_MAX_DELAY


# 💬 Historial de chat en memoria
chat_historial = {}


#Penalizar jugador
def validar_en_cartones(cartones, bolas, funcion_comprobar):
    """
    Devuelve True si AL MENOS UN cartón cumple la condición
    """
    return any(
        funcion_comprobar(carton, bolas)
        for carton in cartones
    )


#Para que se unan a sal de mismos jugadores

def get_lobby(max_players):
    if max_players not in online_lobbies:
        online_lobbies[max_players] = {
            "players": [],
            "max_players": max_players,  # 0 = libre
            "countdown": ONLINE_COUNTDOWN_SECONDS,
            "timer_running": False,
            "started": False
        }
    return online_lobbies[max_players]




# Puntos por cantar:
def sumar_puntos(jugador, puntos):
    jugador["puntos"] += puntos



#Ranqking
def emitir_ranking(socketio, codigo, sala):
    ranking = sorted(
        sala["jugadores"].values(),
        key=lambda j: j["puntos"],
        reverse=True
    )

    socketio.emit(
        "ranking_update",
        {
            "ranking": [
                {"nombre": j["nombre"], "puntos": j["puntos"]}
                for j in ranking
            ]
        },
        room=codigo
    )


# =====================================================
# UTILIDADES
# =====================================================

def emitir_estado_a_todos(socketio, codigo, sala):
    socketio.emit(
        "lista_jugadores",
        {
            "jugadores": [
                {
                    "nombre": j["nombre"],
                    "cartones": j.get("cartones", 1)
                }
                for j in sala["jugadores"].values()
            ],
            "en_partida": sala["en_partida"],
        },
        room=codigo,
    )



# =====================================================
# 🤖 BOTS
# =====================================================

def fill_with_bots(lobby):
    if lobby["max_players"] <= 0:
        return

    faltan = lobby["max_players"] - len(lobby["players"])
    if faltan <= 0:
        return

    nombres = random.sample(BOT_NAMES, min(faltan, len(BOT_NAMES)))

    for nombre in nombres:
        lobby["players"].append({
            "sid": None,
            "nombre": nombre,
            "bot": True,
            "cartones": 1
        })



# =====================================================
# ⏳ COUNTDOWN ONLINE
# =====================================================

def start_online_countdown(socketio, lobby):

    def run():
        while lobby["countdown"] > 0 and not lobby.get("started"):
            socketio.sleep(1)
            lobby["countdown"] -= 1

            socketio.emit(
                "online_lobby_update",
                {
                    "players": [
                        {
                            "nombre": p["nombre"],
                            "cartones": p.get("cartones", 1)
                        }
                        for p in lobby["players"]
                    ],
                    "countdown": lobby["countdown"],
                    "max_players": lobby["max_players"]
                },
                room=[p["sid"] for p in lobby["players"] if p["sid"]]
            )

        # 🔒 Marcar como iniciada (anti doble inicio)
        if lobby.get("started"):
            return

        lobby["started"] = True

        fill_with_bots(lobby)

        codigo = "".join(random.choices("ABCDEFGH123456789", k=4))
        
        # 🔄 Transferir chat del lobby a la nueva sala
        lobby_key = f"lobby_{lobby['max_players']}"
        if lobby_key in chat_historial:
            chat_historial[codigo] = chat_historial[lobby_key]
            chat_historial.pop(lobby_key, None)

        salas_bingo_online[codigo] = {
            "jugadores": {},
            "cartones": {},
            "en_partida": True,
            "bombo": BomboBingo(),
            "online": True,
            "premios": {
                "linea": None,
                "cruz": None,
                "x": None,
                "bingo": None
            }
        }

        # ✅ Crear partida en BD
        partida_id = crear_partida_online(len(lobby["players"]))
        salas_bingo_online[codigo]["partida_id"] = partida_id

        for p in lobby["players"]:
            
            salas_bingo_online[codigo]["jugadores"][p["nombre"]] = {
                "nombre": p["nombre"],
                "vidas": 3,
                "puntos": 0,
                "cartones": p.get("cartones", 1),
                "sid": p["sid"],
                "bot": p.get("bot", False),
                "user_id": None,
                "cantado": {
                    "linea": False,
                    "cruz": False,
                    "x": False,
                    "bingo": False
                }
            }


        # 🎟️ CARTONES PARA BOTS
        for nombre, jugador in salas_bingo_online[codigo]["jugadores"].items():
            if jugador.get("bot"):
                sala = salas_bingo_online[codigo]
                sala["cartones"][nombre] = [
                    generar_carton() for _ in range(jugador["cartones"])
        ]


        # Redirigir humanos
        for p in lobby["players"]:
            if p["sid"]:
                socketio.emit(
                    "redirect_to_game",
                    {"url": f"/bingo/online/{codigo}"},
                    room=p["sid"]
                )

        # 🧹 Limpiar lobby
        lobby["players"].clear()
        lobby["timer_running"] = False
        lobby["countdown"] = ONLINE_COUNTDOWN_SECONDS
        lobby["started"] = False

    
    socketio.start_background_task(run)





# =====================================================
# AUTOPLAY
# =====================================================
def start_online_autoplay(socketio, codigo):
    def run():
        print("🎱 AUTOPLAY ACTIVO EN SALA", codigo)

        sala = salas_bingo_online.get(codigo)
        if not sala:
            print("❌ Sala no encontrada en autoplay")
            return

        while sala["en_partida"]:
            socketio.sleep(BOLA_INTERVAL_SECONDS)

            bola = sala["bombo"].sacar_bola()
            print("🎱 Bola:", bola)

            if bola is None:
                sala["en_partida"] = False
                print("🏁 Fin de partida")
                return

            # 🔔 Emitir bola a todos
            socketio.emit(
                "bola_cantada",
                {
                    "bola": bola,
                    "historial": sala["bombo"].historial
                },
                room=codigo
            )

            bolas = sala["bombo"].historial

            # 🤖 LÓGICA DE BOTS
            for nombre, jugador in sala["jugadores"].items():
                if not jugador.get("bot"):
                    continue

                cartones = sala["cartones"].get(nombre)
                if not cartones:
                    continue

                carton = cartones[0]

                # ⏱️ pequeño retraso humano
                socketio.sleep(random.uniform(BOT_MIN_DELAY, BOT_MAX_DELAY))


                # LINEA
                if (
                    sala["premios"]["linea"] is None
                    and not jugador["cantado"]["linea"]
                    and comprobar_linea(carton, bolas)
                ):
                    jugador["cantado"]["linea"] = True
                    sala["premios"]["linea"] = nombre
                    sumar_puntos(jugador, 1)

                    emitir_ranking(socketio, codigo, sala)

                    socketio.emit(
                        "resultado_cantar",
                        {
                            "tipo": "linea",
                            "valida": True,
                            "jugador": nombre,
                            "puntos": jugador["puntos"]
                        },
                        room=codigo
                    )
                    continue




                # CRUZ
                if (
                    sala["premios"]["cruz"] is None
                    and not jugador["cantado"]["cruz"]
                    and comprobar_cruz(carton, bolas)
                ):
                    jugador["cantado"]["cruz"] = True
                    sala["premios"]["cruz"] = nombre
                    sumar_puntos(jugador, 2)

                    emitir_ranking(socketio, codigo, sala)

                    socketio.emit(
                        "resultado_cantar",
                        {
                            "tipo": "cruz",
                            "valida": True,
                            "jugador": nombre,
                            "puntos": jugador["puntos"]
                        },
                        room=codigo
                    )
                    continue



                # X
                if (
                    sala["premios"]["x"] is None
                    and not jugador["cantado"]["x"]
                    and comprobar_x(carton, bolas)
                ):
                    jugador["cantado"]["x"] = True
                    sala["premios"]["x"] = nombre
                    sumar_puntos(jugador, 2)

                    emitir_ranking(socketio, codigo, sala)

                    socketio.emit(
                        "resultado_cantar",
                        {
                            "tipo": "x",
                            "valida": True,
                            "jugador": nombre,
                            "puntos": jugador["puntos"]
                        },
                        room=codigo
                    )
                    continue



                # BINGO (cierra partida)
                if comprobar_bingo(carton, bolas):
                    sala["en_partida"] = False
                    sumar_puntos(jugador, 5)

                    emitir_ranking(socketio, codigo, sala)

                    socketio.emit(
                        "resultado_cantar",
                        {
                            "tipo": "bingo",
                            "valida": True,
                            "jugador": nombre,
                            "puntos": jugador["puntos"]
                        },
                        room=codigo
                    )
                    return


    socketio.start_background_task(run)


#penalizar jugador
def penalizar_jugador(jugador, puntos):
    jugador["vidas"] -= puntos
    if jugador["vidas"] < 0:
        jugador["vidas"] = 0


# =====================================================
# SOCKETS
# =====================================================

def register_bingo_online_sockets(socketio):

    # -------------------------
    # LOBBY ONLINE
    # -------------------------
    @socketio.on("join_online_lobby")
    def join_online_lobby(data):
        sid = request.sid
        nombre = data.get("nombre", "Invitado")
        max_players = int(data.get("max_players", 6))
        cartones = int(data.get("cartones", 1))
        countdown = data.get("countdown")  # 👈 NUEVO

        lobby = get_lobby(max_players)
        join_room(f"lobby_{max_players}")

        # 👑 Si es admin y envía countdown personalizado
        if (
            countdown
            and session.get("role") == "admin"
            and not lobby["timer_running"]
        ):
            lobby["countdown"] = int(countdown)

        if not any(p["sid"] == sid for p in lobby["players"]):
            lobby["players"].append({
                "sid": sid,
                "nombre": nombre,
                "cartones": cartones,
                "bot": False
            })

        if not lobby["timer_running"]:
            lobby["timer_running"] = True
            start_online_countdown(socketio, lobby)

        emit("online_lobby_update", {
            "players": [
                {
                    "nombre": p["nombre"],
                    "cartones": p.get("cartones", 1)
                }
                for p in lobby["players"]
            ],
            "countdown": lobby["countdown"],
            "max_players": lobby["max_players"]
        })




    # -------------------------
    # ENTRAR EN SALA ONLINE
    # -------------------------
    @socketio.on("join_online_game")
    def join_online_game(data):
        codigo = data.get("codigo")
        nombre = data.get("nombre")
        user_id = data.get("user_id")

        sid = request.sid

        print("👉 join_online_game:", codigo, nombre, sid)

        sala = salas_bingo_online.get(codigo)
        if not sala:
            print("❌ Sala no existe")
            return

        jugador = sala["jugadores"].get(nombre)
        if not jugador:
            print("❌ Jugador no existe en sala:", nombre)
            return

        # 🔗 Asociar SID real
        jugador["sid"] = sid
        jugador["user_id"] = user_id   # 👈 NUEVO

        if user_id:
            ensure_bingo_online_stats(user_id)
            print("DEBUG join:", nombre, "→ user_id:", user_id)


        join_room(codigo)
        # 📜 Enviar historial del chat si existe
        if codigo in chat_historial:
            emit("chat_history", chat_historial[codigo], room=sid)

        emitir_estado_a_todos(socketio, codigo, sala)


        # 🎟️ Generar cartón SOLO aquí
        if sid not in sala["cartones"]:
            num_cartones = jugador.get("cartones", 1)

            cartones = [generar_carton() for _ in range(num_cartones)]
            sala["cartones"][sid] = cartones

        else:
            cartones = sala["cartones"][sid]

        print("🎟️ Enviando cartón a", nombre)

        emit("send_carton", {"cartones": cartones}, room=sid)

        # 🔥 Arrancar autoplay UNA vez
        if not sala.get("autoplay"):
            sala["autoplay"] = True
            print("🎱 Arrancando autoplay")
            start_online_autoplay(socketio, codigo)

        emit("game_started", {}, room=sid)

    # -------------------------
    # CANTAR LINEA
    # -------------------------
    @socketio.on("cantar_linea")
    def cantar_linea(data):
        codigo = data.get("codigo")
        sid = request.sid

        sala = salas_bingo_online.get(codigo)
        if not sala:
            return

        cartones = sala["cartones"].get(sid)
        if not cartones:
            return

        jugador = next(
            (j for j in sala["jugadores"].values() if j["sid"] == sid),
            None
        )
        if not jugador:
            return

        # 🚫 Bloqueo global: ya se cantó la línea en la sala
        if sala["premios"]["linea"] is not None:
            return

        # 🚫 Este jugador ya cantó línea
        if jugador["cantado"]["linea"]:
            return

        # ✅ VALIDAR EN TODOS LOS CARTONES
        es_valida = validar_en_cartones(
            cartones,
            sala["bombo"].historial,
            comprobar_linea
        )

        if es_valida:
            jugador["cantado"]["linea"] = True
            sala["premios"]["linea"] = jugador["nombre"]  # 🔒 bloqueo global
            sumar_puntos(jugador, 1)

            if jugador.get("user_id"):
                registrar_linea_online(jugador["user_id"], sala["partida_id"])
                sumar_puntos_online(jugador["user_id"], 1)

            emitir_ranking(socketio, codigo, sala)

            emit(
                "resultado_cantar",
                {
                    "tipo": "linea",
                    "valida": True,
                    "jugador": jugador["nombre"],
                    "puntos": jugador["puntos"]
                },
                room=codigo
            )
        else:
            penalizar_jugador(jugador, 1)

            emit(
                "resultado_cantar",
                {
                    "tipo": "linea",
                    "valida": False,
                    "vidas": jugador["vidas"],
                    "jugador": jugador["nombre"]
                },
                room=sid
            )

    @socketio.on("start_online_now")
    def start_online_now(data):

        if session.get("role") != "admin":
            return

        lobby = None

        for l in online_lobbies.values():
            if any(p["sid"] == request.sid for p in l["players"]):
                lobby = l
                break

        if not lobby:
            return

        if lobby.get("started"):
            return

        lobby["countdown"] = 0






    # -------------------------
    # CANTAR CRUZ
    # -------------------------
    @socketio.on("cantar_cruz")
    def cantar_cruz(data):
        codigo = data.get("codigo")
        sid = request.sid

        sala = salas_bingo_online.get(codigo)
        if not sala:
            return

        cartones = sala["cartones"].get(sid)
        if not cartones:
            return

        jugador = next(
            (j for j in sala["jugadores"].values() if j["sid"] == sid),
            None
        )
        if not jugador:
            return

        # 🚫 Bloqueo global
        if sala["premios"]["cruz"] is not None:
            return

        # 🚫 Ya la cantó este jugador
        if jugador["cantado"]["cruz"]:
            return

        es_valida = validar_en_cartones(
            cartones,
            sala["bombo"].historial,
            comprobar_cruz
        )

        if es_valida:
            jugador["cantado"]["cruz"] = True
            sala["premios"]["cruz"] = jugador["nombre"]
            sumar_puntos(jugador, 2)

            if jugador.get("user_id"):
                registrar_cruz_online(jugador["user_id"], sala["partida_id"])
                sumar_puntos_online(jugador["user_id"], 2)


            emitir_ranking(socketio, codigo, sala)

            emit(
                "resultado_cantar",
                {
                    "tipo": "cruz",
                    "valida": True,
                    "jugador": jugador["nombre"],
                    "puntos": jugador["puntos"]
                },
                room=codigo
            )
        else:
            penalizar_jugador(jugador, 1)

            emit(
                "resultado_cantar",
                {
                    "tipo": "cruz",
                    "valida": False,
                    "vidas": jugador["vidas"],
                    "jugador": jugador["nombre"]
                },
                room=sid
            )



    # -------------------------
    # CANTAR X
    # -------------------------
    @socketio.on("cantar_x")
    def cantar_x(data):
        codigo = data.get("codigo")
        sid = request.sid

        sala = salas_bingo_online.get(codigo)
        if not sala:
            return

        cartones = sala["cartones"].get(sid)
        if not cartones:
            return

        jugador = next(
            (j for j in sala["jugadores"].values() if j["sid"] == sid),
            None
        )
        if not jugador:
            return

        # 🚫 Bloqueo global
        if sala["premios"]["x"] is not None:
            return

        # 🚫 Ya la cantó este jugador
        if jugador["cantado"]["x"]:
            return

        es_valida = validar_en_cartones(
            cartones,
            sala["bombo"].historial,
            comprobar_x
        )

        if es_valida:
            jugador["cantado"]["x"] = True
            sala["premios"]["x"] = jugador["nombre"]
            sumar_puntos(jugador, 2)

            if jugador.get("user_id"):
                registrar_x_online(jugador["user_id"], sala["partida_id"])
                sumar_puntos_online(jugador["user_id"], 2)


            emitir_ranking(socketio, codigo, sala)

            emit(
                "resultado_cantar",
                {
                    "tipo": "x",
                    "valida": True,
                    "jugador": jugador["nombre"],
                    "puntos": jugador["puntos"]
                },
                room=codigo
            )
        else:
            penalizar_jugador(jugador, 1)

            emit(
                "resultado_cantar",
                {
                    "tipo": "x",
                    "valida": False,
                    "vidas": jugador["vidas"],
                    "jugador": jugador["nombre"]
                },
                room=sid
            )

    # -------------------------
    # CANTAR BINGO
    # -------------------------
    @socketio.on("cantar_bingo")
    def cantar_bingo(data):
        codigo = data.get("codigo")
        sid = request.sid

        sala = salas_bingo_online.get(codigo)
        if not sala:
            return

        cartones = sala["cartones"].get(sid)
        if not cartones:
            return

        jugador = next(
            (j for j in sala["jugadores"].values() if j["sid"] == sid),
            None
        )
        if not jugador:
            return

        es_valida = validar_en_cartones(
            cartones,
            sala["bombo"].historial,
            comprobar_bingo
        )

        if es_valida:
            sala["en_partida"] = False
            sumar_puntos(jugador, 5)

            # ✅ Registrar partida jugada para todos humanos
            for j in sala["jugadores"].values():
                if j.get("user_id"):
                    registrar_partida_online(j["user_id"])

            # ✅ Registrar bingo ganador
            if jugador.get("user_id"):
                registrar_bingo_online(
                    jugador["user_id"],
                    sala["partida_id"],
                    len(sala["bombo"].historial) * 5
                )
                sumar_puntos_online(jugador["user_id"], 5)

            emitir_ranking(socketio, codigo, sala)

            emit(
                "resultado_cantar",
                {
                    "tipo": "bingo",
                    "valida": True,
                    "jugador": jugador["nombre"],
                    "puntos": jugador["puntos"]
                },
                room=codigo
            )

        else:
            penalizar_jugador(jugador, 2)

            emit(
                "resultado_cantar",
                {
                    "tipo": "bingo",
                    "valida": False,
                    "vidas": jugador["vidas"],
                    "jugador": jugador["nombre"]
                },
                room=sid
            )


    # -------------------------
    # SALIR DE LA SALA
    # -------------------------
    @socketio.on("salir_sala")
    def salir_sala(data):
        codigo = data.get("codigo")
        sid = request.sid

        sala = salas_bingo_online.get(codigo)
        if not sala:
            emit("saliste_sala", {}, room=sid)
            return

        # 🧹 Quitar cartones del jugador
        sala["cartones"].pop(sid, None)

        # 🧹 Desvincular SID del jugador
        for jugador in sala["jugadores"].values():
            if jugador.get("sid") == sid:
                jugador["sid"] = None

        # 🚪 Salir del room Socket.IO
        leave_room(codigo)

        print(f"🚪 Jugador {sid} salió de la sala {codigo}")

        # 🧨 AQUÍ VA EXACTAMENTE
        if all(j["sid"] is None for j in sala["jugadores"].values()):
            print("🧨 Sala vacía, eliminando:", codigo)
            salas_bingo_online.pop(codigo, None)

        # ✅ Confirmar al frontend
        emit("saliste_sala", {}, room=sid)


    # -------------------------
    # 💬 CHAT (Lobby + Sala)
    # -------------------------
    @socketio.on("chat_message")
    def handle_chat_message(data):
        codigo = data.get("codigo")
        mensaje = data.get("message", "")[:200].strip()

        if not mensaje or not codigo:
            return

        if codigo not in chat_historial:
            chat_historial[codigo] = []

        mensaje_data = {
            "username": session.get("username", "Invitado"),
            "message": mensaje
        }

        # Guardar máximo 30 mensajes
        chat_historial[codigo].append(mensaje_data)
        chat_historial[codigo] = chat_historial[codigo][-30:]

        emit("new_chat_message", mensaje_data, room=codigo)

