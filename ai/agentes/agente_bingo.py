import os
from litellm import completion
from .contexto_bingo import contexto_bingo

# Lista de modelos válidos para intentar en orden
MODELOS_GROQ = [
    "groq/llama-3.3-70b-versatile",    # Primera opción recomendada
    "groq/llama-3.1-8b-instant",       # Segunda opción (más rápida)
    "groq/mixtral-8x7b-32768",         # Tercera opción
    "groq/gemma2-9b-it",                # Cuarta opción
]

def preguntar_agente_bingo(pregunta, estado=None):
    """
    Envía una pregunta al agente de IA usando Groq con reintentos automáticos
    y contexto del estado actual de la partida.
    
    Args:
        pregunta (str): La pregunta del usuario
        estado (dict, opcional): Diccionario con el estado actual de la partida
                                 (jugadores, última bola, bolas recientes, etc.)
    
    Returns:
        str: Respuesta de la IA o mensaje de error
    """
    try:
        # Verificar API key
        api_key = os.environ.get("GROQ_API_KEY")
        if not api_key:
            return "Error: No se encontró la clave de API de Groq. Verifica tu archivo .env"
        
        # Construir mensajes para la IA
        messages = [
            {
                "role": "system",
                "content": contexto_bingo  # Contexto base del asistente
            }
        ]
        
        # Añadir contexto del estado de la partida si existe
        if estado:
            contexto_estado = f"""
            📊 ESTADO ACTUAL DE LA PARTIDA:
            
            • Jugadores: {estado.get("jugadores", "No disponible")}
            • Última bola: {estado.get("ultima_bola", "Ninguna")}
            • Últimas bolas: {estado.get("bolas_recientes", "Ninguna")}
            • Línea cantada: {estado.get("linea_cantada", "No")}
            • Bingo cantado: {estado.get("bingo_cantado", "No")}
            • Cartones visibles: {estado.get("cartones_visibles", "No disponible")}
            """
            
            messages.append({
                "role": "system",
                "content": contexto_estado
            })
        
        # Añadir la pregunta del usuario
        messages.append({
            "role": "user",
            "content": pregunta
        })
        
        # Opcional: imprimir para depuración
        print(f"📨 Consultando a la IA con estado: {bool(estado)}")
        
        errores = []
        
        # Intentar con cada modelo hasta que uno funcione
        for modelo in MODELOS_GROQ:
            try:
                print(f"🔄 Intentando con modelo: {modelo}")
                
                respuesta = completion(
                    model=modelo,
                    messages=messages,
                    api_key=api_key,
                    temperature=0.7,  # Ajusta según necesites
                    max_tokens=500     # Límite para respuestas concisas
                )
                
                # Si llegamos aquí, el modelo funcionó
                print(f"✅ Modelo {modelo} respondió correctamente")
                return respuesta.choices[0].message.content
                
            except Exception as e:
                error_msg = str(e)
                errores.append(f"{modelo}: {error_msg}")
                print(f"❌ Error con {modelo}: {error_msg[:100]}...")
                
                # Si es error de modelo descontinuado, continuamos con el siguiente
                if "decommissioned" in error_msg or "not supported" in error_msg:
                    continue
                else:
                    # Si es otro tipo de error (API key, rate limit, etc.), lo propagamos
                    raise
        
        # Si ningún modelo funcionó
        return f"Error: No se pudo encontrar un modelo disponible. Intentos fallidos: {len(errores)}"
        
    except Exception as e:
        # Manejo de errores específicos
        error_msg = str(e)
        if "Invalid API Key" in error_msg:
            return "Error: La clave de API de Groq no es válida. Por favor, verifica tu clave en https://console.groq.com"
        elif "Rate limit" in error_msg:
            return "Error: Has excedido el límite de solicitudes. Espera un momento y vuelve a intentar."
        else:
            print(f"🔥 Error inesperado: {error_msg}")
            return f"Error al comunicarse con la IA: {error_msg}"