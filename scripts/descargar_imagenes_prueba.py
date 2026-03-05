#!/usr/bin/env python3
"""
Script para descargar imágenes de prueba usando Pexels API
"""

import os
import hashlib
import requests
import time
import random

# Configuración
IMAGE_CACHE_DIR = "static/img/ai_generated/"
os.makedirs(IMAGE_CACHE_DIR, exist_ok=True)

# Tu API key de Pexels (gratis, regístrate en https://www.pexels.com/api/)
PEXELS_API_KEY = "dndjp2dQ14IuNQ4M7UQZ3BaYYL9jkCC4UNZLwTtJ15yC4IzqPbJxIgMP"  # API key demo

# Lista de palabras para buscar
PALABRAS = [
    "dog", "cat", "car", "apple", "ball", "bird", "fish", "house",
    "key", "camera", "clock", "computer", "phone", "book", "pencil", "chair",
    "lion", "elephant", "giraffe", "airplane", "train", "robot", "flower", "tree",
    "cow", "horse", "sheep", "pig", "duck", "rabbit", "turtle", "butterfly"
]

COLORES = ["red", "blue", "green", "yellow", "brown", "white", "black", "orange", "purple", "pink"]
ACCIONES = ["sleeping", "running", "eating", "flying", "sitting"]

def generar_hash(prompt):
    """Genera el mismo hash que usa el juego"""
    return hashlib.md5(f"{prompt}_cartoon".encode()).hexdigest()

def descargar_imagen_pexels(query, prompt=None):
    """Descarga una imagen de Pexels"""
    
    if prompt is None:
        prompt = query
    
    filename = f"{IMAGE_CACHE_DIR}{generar_hash(prompt)}.jpg"
    
    # Si ya existe, no descargar de nuevo
    if os.path.exists(filename):
        print(f"✅ Ya existe: {os.path.basename(filename)}")
        return True
    
    headers = {
        "Authorization": PEXELS_API_KEY
    }
    
    # Buscar en Pexels
    search_url = f"https://api.pexels.com/v1/search?query={query}&per_page=5&orientation=square"
    
    try:
        print(f"📥 Buscando: {query}")
        response = requests.get(search_url, headers=headers, timeout=10)
        
        if response.status_code == 200:
            data = response.json()
            
            if data["photos"]:
                # Tomar la primera foto
                foto = data["photos"][0]
                img_url = foto["src"]["medium"]  # 400x400
                
                # Descargar la imagen
                img_response = requests.get(img_url, timeout=10)
                if img_response.status_code == 200:
                    with open(filename, "wb") as f:
                        f.write(img_response.content)
                    print(f"✅ Guardada: {os.path.basename(filename)}")
                    return True
                else:
                    print(f"❌ Error descargando imagen: {img_response.status_code}")
                    return False
            else:
                print(f"⚠️ No se encontraron imágenes para: {query}")
                return False
        else:
            print(f"❌ Error API {response.status_code}: {query}")
            return False
            
    except Exception as e:
        print(f"❌ Error: {e}")
        return False

def descargar_lote_imagenes():
    """Descarga un lote de imágenes para probar"""
    
    print("🎨 Descargando imágenes de prueba desde Pexels...")
    print("=" * 50)
    
    total_descargadas = 0
    
    # 1. Imágenes simples (objeto + color)
    print("\n📦 Imágenes simples (objeto + color):")
    queries = []
    for _ in range(15):
        palabra = random.choice(PALABRAS)
        color = random.choice(COLORES)
        query = f"{color} {palabra}"
        prompt = f"A {color} {palabra}"
        queries.append((query, prompt))
    
    for query, prompt in queries:
        if descargar_imagen_pexels(query, prompt):
            total_descargadas += 1
        time.sleep(0.5)  # Pausa para no saturar la API
    
    # 2. Imágenes con acciones
    print("\n🏃 Imágenes con acciones:")
    queries_accion = []
    for _ in range(10):
        palabra = random.choice(PALABRAS)
        color = random.choice(COLORES)
        accion = random.choice(ACCIONES)
        query = f"{color} {palabra}"
        prompt = f"A {color} {palabra} {accion}"
        queries_accion.append((query, prompt))
    
    for query, prompt in queries_accion:
        if descargar_imagen_pexels(query, prompt):
            total_descargadas += 1
        time.sleep(0.5)
    
    # 3. Objetos simples
    print("\n🔑 Objetos simples:")
    for palabra in random.sample(PALABRAS, 10):
        if descargar_imagen_pexels(palabra, f"A {palabra}"):
            total_descargadas += 1
        time.sleep(0.5)
    
    print("\n" + "=" * 50)
    print(f"✨ Descarga completada!")
    print(f"📁 Total de imágenes: {total_descargadas}")
    print(f"📍 Directorio: {IMAGE_CACHE_DIR}")
    
    # Mostrar las imágenes descargadas
    archivos = os.listdir(IMAGE_CACHE_DIR)
    print(f"\n📸 Primeras 10 imágenes:")
    for i, archivo in enumerate(sorted(archivos)[:10]):
        print(f"  {i+1}. {archivo}")

def verificar_imagenes_cargadas():
    """Verifica cuántas imágenes hay en caché"""
    archivos = os.listdir(IMAGE_CACHE_DIR)
    print(f"\n📊 Estadísticas de caché:")
    print(f"  Total imágenes: {len(archivos)}")
    
    # Mostrar algunas imágenes como ejemplo
    if archivos:
        print(f"\n  Ejemplos:")
        for archivo in random.sample(archivos, min(5, len(archivos))):
            print(f"    - {archivo}")

if __name__ == "__main__":
    random.seed(42)
    descargar_lote_imagenes()
    verificar_imagenes_cargadas()