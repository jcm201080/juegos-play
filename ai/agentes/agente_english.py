from litellm import completion
from ai.agentes.contexto_english import contexto_english
import json


# ===============================
# 🤖 Asistente del juego
# ===============================
def preguntar_agente_english(pregunta):

    response = completion(
        model="groq/llama-3.3-70b-versatile",
        messages=[
            {"role": "system", "content": contexto_english},
            {"role": "user", "content": pregunta}
        ],
        max_tokens=200
    )

    return response["choices"][0]["message"]["content"]


# ===============================
# 🎮 Generador de niveles
# ===============================
def generar_nivel_english(level):

    prompt = f"""
Generate a level for an English learning drag-and-drop game.

Level difficulty: {level}

Return ONLY valid JSON with this structure:

{{
 "type": "simple",
 "description": "Match the color with the word",
 "items": [
   {{"id":"red","word":"red","color":"#e74c3c"}},
   {{"id":"blue","word":"blue","color":"#3498db"}}
 ]
}}

Rules:

- 5 to 6 items
- Beginner vocabulary if level < 5
- Sentences if level >= 5
- Colors or simple objects
- No explanations
- Only JSON
"""

    response = completion(
        model="groq/llama-3.3-70b-versatile",
        messages=[{"role": "user", "content": prompt}],
        max_tokens=400
    )

    texto = response["choices"][0]["message"]["content"]

    try:
        return json.loads(texto)
    except Exception:
        return None