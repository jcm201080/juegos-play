from litellm import completion
from ai.agentes.contexto_english import contexto_english
import json
import re

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
# 🎮 Generador de niveles IA
# ===============================
def generar_nivel_english(level):

    # ajustar dificultad según nivel
    if level <= 3:
        dificultad = "very easy"
    elif level <= 5:
        dificultad = "easy"
    elif level <= 8:
        dificultad = "medium"
    else:
        dificultad = "hard"

    prompt = f"""
You generate levels for an English learning drag-and-drop game.

Level: {level}
Difficulty: {dificultad}

Game goal:
Players must match words or sentences with the correct color or object.

Rules:
- Generate between 5 and 6 items.
- Vocabulary must be beginner level English.
- Prefer colors, animals, vehicles, fruits or basic objects.
- Avoid repeating the same colors too often.
- Sentences must be short and simple.
- Use different structures if possible.

Game types allowed:

1) simple
Match word → color

Example:
{{"id":"red","word":"red","color":"#e74c3c"}}

2) sentence_color
Match sentence → color

Example:
{{"id":"car_red","sentence":"The car is red.","color":"#e74c3c"}}

IMPORTANT:
- Return ONLY valid JSON.
- Do not add explanations.
- Do not use markdown.

JSON format:

{{
"type": "simple",
"description": "Match the color with the correct word",
"items": [
  {{}}
]
}}
"""

    try:

        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": contexto_english},
                {"role": "user", "content": prompt}
            ],
            max_tokens=500,
            temperature=0.9
        )

        texto = response["choices"][0]["message"]["content"]

        # limpiar posible markdown
        texto = texto.strip()
        texto = re.sub(r"```json", "", texto)
        texto = re.sub(r"```", "", texto)

        data = json.loads(texto)

        return data

    except Exception as e:

        print("⚠️ Error generando nivel IA:", e)

        # fallback para que el juego nunca se rompa
        return {
            "type": "simple",
            "description": "Match the color with the word",
            "items": [
                {"id": "red", "word": "red", "color": "#e74c3c"},
                {"id": "blue", "word": "blue", "color": "#3498db"},
                {"id": "green", "word": "green", "color": "#2ecc71"},
                {"id": "yellow", "word": "yellow", "color": "#f1c40f"},
                {"id": "black", "word": "black", "color": "#000000"},
            ]
        }