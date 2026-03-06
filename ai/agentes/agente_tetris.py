# ai/agentes/agente_tetris.py
from litellm import completion

contexto_tetris = """
Eres un asistente experto en Tetris, el clásico juego de bloques.

REGLAS DEL TETRIS:
- El tablero tiene 10 columnas y 20 filas
- Hay 7 piezas: I (línea), O (cuadrado), T, S, Z, L, J
- Las piezas caen desde arriba y debes colocarlas
- Objetivo: completar líneas horizontales
- Cuando completas 1, 2, 3 o 4 líneas, desaparecen y ganas puntos

SISTEMA DE PUNTUACIÓN:
- 1 línea = 100 × nivel
- 2 líneas = 300 × nivel
- 3 líneas = 500 × nivel
- 4 líneas (TETRIS) = 800 × nivel

CONTROLES:
- Teclado: ← → ↑ ↓ y Espacio para caída instantánea
- Móvil: Botones en pantalla + gestos táctiles (swipe)

ESTRATEGIAS BÁSICAS:
- Mantén el tablero lo más plano posible
- No dejes huecos aislados
- Guarda espacio para la pieza larga (I)
- Las piezas T son útiles para girar en espacios pequeños
- Mira siempre la siguiente pieza para planificar

Puedes dar consejos en tiempo real, explicar reglas, ayudar con controles
y sugerir estrategias según la situación del tablero.
"""

def preguntar_agente_tetris(pregunta, contexto_partida=None):
    """
    Agente especializado en Tetris.
    
    Args:
        pregunta (str): Pregunta del usuario
        contexto_partida (dict): Contexto actual de la partida (opcional)
    
    Returns:
        str: Respuesta del agente
    """
    
    # Construir el contexto con información de la partida si existe
    contexto = contexto_tetris
    
    if contexto_partida:
        tablero = contexto_partida.get('tablero', [])
        pieza = contexto_partida.get('pieza_actual', {})
        puntuacion = contexto_partida.get('puntuacion', 0)
        nivel = contexto_partida.get('nivel', 1)
        lineas = contexto_partida.get('lineas', 0)
        
        contexto += f"\n\nCONTEXTO ACTUAL DE LA PARTIDA:\n"
        contexto += f"- Puntuación: {puntuacion}\n"
        contexto += f"- Nivel: {nivel}\n"
        contexto += f"- Líneas completadas: {lineas}\n"
        if pieza:
            contexto += f"- Pieza actual: {pieza.get('tipo', 'desconocida')}\n"
    
    try:
        response = completion(
            model="groq/llama-3.3-70b-versatile",
            messages=[
                {"role": "system", "content": contexto},
                {"role": "user", "content": pregunta}
            ],
            max_tokens=300,
            temperature=0.7
        )
        
        return response["choices"][0]["message"]["content"]
    
    except Exception as e:
        print(f"Error en agente Tetris: {e}")
        return "Lo siento, tengo problemas para responder ahora. ¿En qué más puedo ayudarte con el Tetris?"