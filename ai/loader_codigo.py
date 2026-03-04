import os

BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))


# =========================
# 📄 README
# =========================
def cargar_readme():

    ruta = os.path.join(BASE_DIR, "README.md")

    if os.path.exists(ruta):

        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()

    return "README no disponible."


# =========================
# 🧠 app.py
# =========================
def cargar_app():

    ruta = os.path.join(BASE_DIR, "app.py")

    if os.path.exists(ruta):

        with open(ruta, "r", encoding="utf-8") as f:
            return f.read()[:3000]

    return ""


# =========================
# 📂 routes
# =========================
def cargar_routes():

    rutas_dir = os.path.join(BASE_DIR, "routes")

    texto = ""

    if not os.path.exists(rutas_dir):
        return ""

    for archivo in os.listdir(rutas_dir):

        if archivo.endswith(".py"):

            ruta = os.path.join(rutas_dir, archivo)

            try:
                with open(ruta, "r", encoding="utf-8") as f:

                    contenido = f.read()[:2000]

                    texto += f"\n\nArchivo routes/{archivo}:\n"
                    texto += contenido

            except Exception:
                pass

    return texto


# =========================
# 🎱 bingo
# =========================
def cargar_bingo():

    bingo_dir = os.path.join(BASE_DIR, "bingo")

    texto = ""

    if not os.path.exists(bingo_dir):
        return ""

    for root, dirs, files in os.walk(bingo_dir):

        for archivo in files:

            if archivo.endswith(".py"):

                ruta = os.path.join(root, archivo)

                try:
                    with open(ruta, "r", encoding="utf-8") as f:

                        contenido = f.read()[:1500]

                        ruta_relativa = ruta.replace(BASE_DIR, "")

                        texto += f"\n\nArchivo {ruta_relativa}:\n"
                        texto += contenido

                except Exception:
                    pass

    return texto


# =========================
# 🧠 Contexto completo
# =========================
def cargar_contexto_codigo():

    readme = cargar_readme()
    routes = cargar_routes()
    app = cargar_app()
    bingo = cargar_bingo()

    contexto = f"""
DOCUMENTACIÓN DEL PROYECTO:

{readme[:3000]}


ARCHIVO PRINCIPAL app.py:

{app}


RUTAS DE LA APLICACIÓN:

{routes[:5000]}


CÓDIGO DEL SISTEMA DE BINGO:

{bingo[:5000]}
"""

    return contexto