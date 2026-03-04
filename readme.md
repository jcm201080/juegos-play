## 📁 Estructura del proyecto

```text
juegos-play/
│
├── app.py
├── config.py
├── db.py
├── README.md
│
├── ai/                        # 🧠 Asistentes y lógica de IA
│   ├── agente_bingo.py        # Agente IA del bingo
│   └── contexto_bingo.py      # Contexto y reglas del bingo para la IA
│
├── routes/                    # Rutas generales de la plataforma
│   ├── auth_routes.py
│   ├── perfil_routes.py
│   ├── home_routes.py
│   └── ...
│
├── bingo/
│   │
│   ├── logic/                 # Motor compartido del bingo
│   │   ├── bolas.py
│   │   ├── cartones.py
│   │   ├── validaciones.py
│   │   └── bingo_stats.py
│   │
│   ├── classic/               # Bingo clásico (salas privadas)
│   │   ├── routes/
│   │   ├── templates/
│   │   └── sockets/
│   │
│   ├── bingo_online/          # Bingo online (matchmaking automático)
│   │   ├── routes/
│   │   ├── templates/
│   │   └── sockets/
│
├── static/
│   ├── css/
│   ├── js/
│   └── sounds/
│
├── templates/
│   ├── base.html
│   ├── home.html
│   ├── perfil.html
│   └── ...
│
├── utils/
├── scripts/
├── models/
├── database/
│
└── venv/
```

### 🧠 Inteligencia Artificial

El proyecto incluye un asistente basado en IA que ayuda a los jugadores dentro del bingo.

Funciones del asistente:

* Explicar reglas del juego
* Ayudar a nuevos jugadores
* Responder preguntas sobre la partida
* Usar el contexto real de la sala (jugadores, bolas, estado del juego)

El asistente se comunica con el backend mediante la API:

```
/api/bingo-ai
```
