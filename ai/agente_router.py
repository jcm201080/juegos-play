from litellm import completion

from ai.agentes.agente_bingo import preguntar_agente_bingo
from ai.contexto_general import contexto_general
from ai.agentes.agente_english import preguntar_agente_english


def clasificar_pregunta(pregunta):
    """
    Decide qué agente debe responder.
    """

    system_prompt = """
Clasifica la pregunta del usuario según el juego al que pertenece.

Opciones posibles:

bingo
chess
puzzle
math
english
general

Responde SOLO con una palabra.
"""

    response = completion(
        model="groq/llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": pregunta}
        ],
        max_tokens=10
    )

    decision = response["choices"][0]["message"]["content"].strip().lower()

    return decision


def preguntar_agente_general(pregunta, pagina=""):

    # 🧭 Pista rápida según la página actual
    if pagina:
        pagina_lower = pagina.lower()

        if "bingo" in pagina_lower:
            print("🧠 Router IA: bingo (por página)")
            return preguntar_agente_bingo(pregunta)

        if "english" in pagina_lower:
            print("🧠 Router IA: english (por página)")
            return preguntar_agente_english(pregunta)

        if "chess" in pagina_lower:
            print("🧠 Router IA: chess (por página)")
            # return preguntar_agente_chess(pregunta)

        if "puzzle" in pagina_lower:
            print("🧠 Router IA: puzzle (por página)")
            # return preguntar_agente_puzzle(pregunta)

    # 🧠 Si no se puede deducir por página → usar IA
    decision = clasificar_pregunta(pregunta)

    print("🧠 Router IA:", decision)

    # 🎱 Bingo
    if decision == "bingo":
        return preguntar_agente_bingo(pregunta)

    if decision == "english":
        return preguntar_agente_english(pregunta)

    # 🧠 General
    return responder_general(pregunta)


def responder_general(pregunta):

    response = completion(
        model="groq/llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": contexto_general},
            {"role": "user", "content": pregunta}
        ],
        max_tokens=300
    )

    return response["choices"][0]["message"]["content"]