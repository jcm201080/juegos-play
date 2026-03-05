from litellm import completion, image_generation
from ai.agentes.contexto_english import contexto_english
import json
import re
import os
import hashlib
import base64
import requests
import random

# Configuración de imágenes
IMAGE_CACHE_DIR = "static/img/ai_generated/"
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

# ===============================
# 🤖 Generador de imágenes con caché
# ===============================
def generar_o_obtener_imagen(prompt, estilo="cartoon"):
    """
    Genera imagen con IA o la obtiene de caché
    """
    prompt_hash = hashlib.md5(f"{prompt}_{estilo}".encode()).hexdigest()
    filename = f"{IMAGE_CACHE_DIR}{prompt_hash}.jpg"
    url_filename = f"/static/img/ai_generated/{prompt_hash}.jpg"
    
    # Si ya existe, devolver
    if os.path.exists(filename):
        print(f"✅ Imagen en caché: {url_filename}")
        return url_filename
    
    # 🟢 Si no existe, usamos las imágenes que ya descargamos
    # En lugar de intentar generar nuevas, devolvemos None
    # y el juego usará emojis como fallback
    print(f"⚠️ Imagen no encontrada en caché para: {prompt}")
    print(f"   Usando emoji fallback. Si quieres esta imagen, ejecuta el script de descarga con: {prompt}")
    return None
    
    # 🔴 Comentamos todo el código de generación para evitar error 402
    """
    try:
        print(f"🎨 Generando imagen para: {prompt}")
        
        # Configurar API keys según el proveedor
        if "stability" in os.environ.get("IMAGE_PROVIDER", "stability"):
            # Stability AI
            api_key = os.environ.get("STABILITY_API_KEY")
            if not api_key:
                print("⚠️ STABILITY_API_KEY no configurada")
                return None
                
            response = requests.post(
                "https://api.stability.ai/v2beta/stable-image/generate/sd3",
                headers={
                    "authorization": f"Bearer {api_key}",
                    "accept": "image/*"
                },
                files={"none": ''},
                data={
                    "prompt": f"{prompt}, {estilo}, simple, clear, white background",
                    "output_format": "jpeg",
                    "aspect_ratio": "1:1"
                },
                timeout=30
            )
            
            if response.status_code == 200:
                with open(filename, "wb") as f:
                    f.write(response.content)
                print(f"✅ Imagen generada y guardada: {filename}")
                return url_filename
            else:
                print(f"❌ Error Stability AI: {response.status_code}")
                return None
                
        else:
            # Usar liteLLM para otros proveedores
            response = image_generation(
                model="dall-e-3",
                prompt=f"{prompt}, {estilo}, simple, clear, white background",
                size="1024x1024",
                n=1
            )
            
            if response and hasattr(response, 'data') and len(response.data) > 0:
                image_url = response.data[0].url
                img_response = requests.get(image_url)
                with open(filename, "wb") as f:
                    f.write(img_response.content)
                return url_filename
            
    except Exception as e:
        print(f"⚠️ Error generando imagen: {e}")
        return None
    """

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
    """Genera un nivel según el nivel del usuario"""
    
    # Niveles 1-5: Sistema tradicional (colores, números)
    if level <= 5:
        return generar_nivel_tradicional(level)
    
    # Niveles 6-15: Imágenes simples
    elif level <= 15:
        return generar_nivel_imagenes_simples(level)
    
    # Niveles 16-25: Objetos con imágenes (si existen) o emojis
    elif level <= 25:
        return generar_nivel_objetos_inteligente(level)
    
    # Niveles 26-35: Frases complejas con imágenes
    elif level <= 35:
        return generar_nivel_frases_complejas(level)
    
    # Niveles 36+: Mezcla inteligente
    else:
        # Alternar entre tipos para variedad
        if level % 3 == 0:
            return generar_nivel_objetos_inteligente(level)
        elif level % 3 == 1:
            return generar_nivel_imagenes_simples(level)
        else:
            return generar_nivel_frases_complejas(level)

# ===============================
# 🎮 Generadores específicos
# ===============================

def generar_nivel_tradicional(level):
    """Niveles 1-5: Sistema tradicional sin imágenes"""
    if level <= 3:
        dificultad = "very easy"
    else:
        dificultad = "easy"
    
    prompt = f"""
You generate levels for an English learning drag-and-drop game.

Level: {level}
Difficulty: {dificultad}

Game goal:
Players must match words with colors.

Rules:
- Generate 6 items.
- Use basic colors: red, blue, green, yellow, black, white.
- Return ONLY valid JSON.

JSON format:
{{
"type": "simple",
"description": "Match the color with the word",
"items": [
  {{"id":"red", "word":"red", "color":"#e74c3c"}}
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
            temperature=0.7
        )
        texto = response["choices"][0]["message"]["content"]
        texto = re.sub(r"```json|```", "", texto.strip())
        return json.loads(texto)
    except:
        # Fallback
        return {
            "type": "simple",
            "description": "Match the color with the word",
            "items": [
                {"id": "red", "word": "red", "color": "#e74c3c"},
                {"id": "blue", "word": "blue", "color": "#3498db"},
                {"id": "green", "word": "green", "color": "#2ecc71"},
                {"id": "yellow", "word": "yellow", "color": "#f1c40f"},
                {"id": "black", "word": "black", "color": "#000000"},
                {"id": "white", "word": "white", "color": "#ffffff"}
            ]
        }

def generar_nivel_imagenes_simples(level):
    """Niveles 6-15: Imágenes simples (frase -> imagen)"""
    objetos = ["dog", "cat", "car", "apple", "ball", "bird", "fish", "house"]
    colores = ["red", "blue", "green", "yellow", "brown", "white", "black"]
    
    items = []
    num_items = 5
    
    for i in range(num_items):
        objeto = random.choice(objetos)
        color = random.choice(colores)
        
        prompt = f"A {color} {objeto}"
        sentence = f"This is a {color} {objeto}."
        
        img_url = generar_o_obtener_imagen(prompt)
        
        if img_url:
            items.append({
                "id": f"img_{i}",
                "sentence": sentence,
                "img": img_url,
                "alt": f"{color} {objeto}"
            })
        else:
            # Fallback a objeto con emoji
            emoji_map = {
                "dog": "🐶", "cat": "🐱", "car": "🚗", "apple": "🍎",
                "ball": "⚽", "bird": "🐦", "fish": "🐟", "house": "🏠"
            }
            items.append({
                "id": f"obj_{i}",
                "word": objeto,
                "emoji": emoji_map.get(objeto, "📦")
            })
    
    # Determinar tipo de nivel
    if all('img' in item for item in items):
        return {
            "type": "sentence_image",
            "description": f"Nivel {level}: Match the sentence with the image",
            "items": items
        }
    else:
        return {
            "type": "objects",
            "description": f"Nivel {level}: Match the word with the emoji",
            "items": [i for i in items if 'emoji' in i]
        }

def generar_nivel_objetos_inteligente(level):
    """Niveles 16-25: Objetos que usan imágenes en caché si existen"""
    objetos = ["key", "camera", "clock", "computer", "phone", "book", "pencil", "chair"]
    
    # Mapa de emojis por defecto
    emoji_map = {
        "key": "🔑", "camera": "📷", "clock": "⏰", "computer": "💻",
        "phone": "📱", "book": "📚", "pencil": "✏️", "chair": "🪑"
    }
    
    items = []
    seleccionados = random.sample(objetos, min(5, len(objetos)))
    
    for objeto in seleccionados:
        # Buscar si existe imagen en caché
        prompt = f"A {objeto}"
        prompt_hash = hashlib.md5(f"{prompt}_cartoon".encode()).hexdigest()
        filename = f"{IMAGE_CACHE_DIR}{prompt_hash}.jpg"
        
        if os.path.exists(filename):
            # Usar imagen si existe en caché
            items.append({
                "id": objeto,
                "word": objeto,
                "img": f"/static/img/ai_generated/{prompt_hash}.jpg"
            })
            print(f"✅ Usando imagen en caché para: {objeto}")
        else:
            # Usar emoji si no hay imagen
            items.append({
                "id": objeto,
                "word": objeto,
                "emoji": emoji_map.get(objeto, "📦")
            })
    
    return {
        "type": "objects",
        "description": f"Nivel {level}: Match the word with the image/emoji",
        "items": items
    }

def generar_nivel_frases_complejas(level):
    """Niveles 26-35: Frases complejas con imágenes"""
    objetos = ["dog", "cat", "lion", "elephant", "robot", "airplane", "train"]
    colores = ["red", "blue", "green", "yellow", "purple", "orange"]
    acciones = ["sleeping", "running", "eating", "flying", "sitting"]
    lugares = ["in the park", "on the table", "under the tree", "near the house"]
    
    items = []
    num_items = 5
    
    for i in range(num_items):
        objeto = random.choice(objetos)
        color = random.choice(colores)
        accion = random.choice(acciones)
        lugar = random.choice(lugares) if level > 30 else ""
        
        if level > 30 and random.choice([True, False]):
            prompt = f"A {color} {objeto} {accion} {lugar}"
            sentence = f"The {color} {objeto} is {accion} {lugar}."
        else:
            prompt = f"A {color} {objeto} {accion}"
            sentence = f"The {color} {objeto} is {accion}."
        
        img_url = generar_o_obtener_imagen(prompt)
        
        if img_url:
            items.append({
                "id": f"img_{i}",
                "sentence": sentence,
                "img": img_url,
                "alt": f"{color} {objeto}"
            })
    
    # Si no hay imágenes, fallback a objetos
    if not items:
        return generar_nivel_objetos_inteligente(level)
    
    return {
        "type": "sentence_image",
        "description": f"Nivel {level}: Match the sentence with the image",
        "items": items
    }