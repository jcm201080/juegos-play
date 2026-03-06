# ai/agente_router.py
from litellm import completion

from ai.agentes.agente_bingo import preguntar_agente_bingo
from ai.agentes.agente_tetris import preguntar_agente_tetris
from ai.agentes.agente_english import preguntar_agente_english
from ai.contexto_general import contexto_general


def clasificar_pregunta(pregunta):
    """
    Decide qué agente debe responder.
    """

    system_prompt = """
Clasifica la pregunta del usuario según el juego al que pertenece.

Opciones posibles:
- bingo
- tetris
- chess
- puzzle
- math
- english
- general

Responde SOLO con una palabra, sin puntos ni nada más.
"""

    try:
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": pregunta}
            ],
            max_tokens=10,
            temperature=0.3
        )

        decision = response["choices"][0]["message"]["content"].strip().lower()
        return decision
    except Exception as e:
        print(f"Error clasificando pregunta: {e}")
        return "general"


def preguntar_agente_general(pregunta, pagina="", contexto_adicional=None):
    """
    Router principal que decide qué agente usar.
    
    Args:
        pregunta (str): Pregunta del usuario
        pagina (str): Página actual (home, bingo, tetris, etc.)
        contexto_adicional (dict): Contexto específico del juego
    """
    
    # 🧭 Pista rápida según la página actual
    if pagina:
        pagina_lower = pagina.lower()

        if "bingo" in pagina_lower:
            print("🧠 Router IA: bingo (por página)")
            return preguntar_agente_bingo(pregunta, contexto_adicional)

        if "tetris" in pagina_lower:
            print("🧠 Router IA: tetris (por página)")
            return preguntar_agente_tetris(pregunta, contexto_adicional)

        if "english" in pagina_lower:
            print("🧠 Router IA: english (por página)")
            return preguntar_agente_english(pregunta, contexto_adicional)

        if "chess" in pagina_lower:
            print("🧠 Router IA: chess (por página)")
            # return preguntar_agente_chess(pregunta, contexto_adicional)

        if "puzzle" in pagina_lower:
            print("🧠 Router IA: puzzle (por página)")
            # return preguntar_agente_puzzle(pregunta, contexto_adicional)

    # 🧠 Si no se puede deducir por página → usar IA
    decision = clasificar_pregunta(pregunta)

    print(f"🧠 Router IA: {decision} (por clasificación)")

    # 🎱 Bingo
    if decision == "bingo":
        return preguntar_agente_bingo(pregunta, contexto_adicional)

    # 🧩 Tetris
    if decision == "tetris":
        return preguntar_agente_tetris(pregunta, contexto_adicional)

    # 📘 English
    if decision == "english":
        return preguntar_agente_english(pregunta, contexto_adicional)

    # 🧠 General
    return responder_general(pregunta)


def responder_general(pregunta):
    """Respuestas para preguntas generales sobre la plataforma"""
    
    try:
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": contexto_general},
                {"role": "user", "content": pregunta}
            ],
            max_tokens=300,
            temperature=0.7
        )

        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        print(f"Error en responder_general: {e}")
        return "Lo siento, tengo problemas técnicos. Por favor, intenta más tarde."