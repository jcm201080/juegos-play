from litellm import completion
from ai.agentes.contexto_english import contexto_english
import json
import re


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
You generate levels for a drag and drop English learning game.

Level: {level}
Difficulty: {dificultad}

Game types allowed:

1 simple:
word → color

Example item:
{{"id":"red","word":"red","color":"#e74c3c"}}

2 sentence_image:
sentence → image

Example item:
{{"id":"dog_black","sentence":"This dog is black.","img":"/static/img/english/dog_black.jpeg","alt":"Black dog"}}

Rules:

- 5 or 6 items
- Beginner vocabulary
- Keep sentences short
- Use colors, animals or objects
- Output ONLY JSON
- Do not add explanations

Return JSON with this structure:

{{
 "type": "simple",
 "description": "Match the color with the word",
 "items": [...]
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
            temperature=0.7
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