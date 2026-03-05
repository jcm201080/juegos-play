# scripts/descargar_una_imagen.py
import hashlib
import requests
import os

def descargar_imagen_especifica(prompt):
    """Descarga una imagen específica para un prompt"""
    
    IMAGE_CACHE_DIR = "static/img/ai_generated/"
    os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)
    
    prompt_hash = hashlib.md5(f"{prompt}_cartoon".encode()).hexdigest()
    filename = f"{IMAGE_CACHE_DIR}{prompt_hash}.jpg"
    
    # Buscar en Pexels
    PEXELS_API_KEY = "563492ad6f91700001000001ccf7a6d776f64b90b4fbe0db1f3b4a6d"
    
    query = prompt.replace("A ", "").replace("_", " ")
    
    headers = {"Authorization": PEXELS_API_KEY}
    search_url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&orientation=square"
    
    response = requests.get(search_url, headers=headers)
    if response.status_code == 200:
        data = response.json()
        if data["photos"]:
            img_url = data["photos"][0]["src"]["medium"]
            img_response = requests.get(img_url)
            with open(filename, "wb") as f:
                f.write(img_response.content)
            print(f"✅ Imagen guardada: {filename}")
            return True
    
    print(f"❌ No se pudo descargar: {prompt}")
    return False

# Ejemplo de uso
descargar_imagen_especifica("A purple elephant running")