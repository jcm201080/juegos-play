# 🎮 Juegos Play - Plataforma de Juegos Multijugador

Plataforma web de juegos con soporte para partidas en tiempo real, rankings globales, estadísticas detalladas y asistentes de IA especializados por juego.

## 📋 Tabla de Contenidos
- [Estructura del Proyecto](#-estructura-del-proyecto)
- [Juegos Disponibles](#-juegos-disponibles)
- [Sistema de Inteligencia Artificial](#-sistema-de-inteligencia-artificial)
- [Base de Datos](#-base-de-datos)
- [API Endpoints](#-api-endpoints)
- [Instalación](#-instalación)
- [Tecnologías](#-tecnologías)
- [Características](#-características)

## 📁 Estructura del Proyecto

juegos-play/
│
├── app.py # Punto de entrada principal
├── config.py # Configuraciones globales
├── db.py # Conexiones y funciones BD
├── requirements.txt # Dependencias del proyecto
├── README.md # Este archivo
│
├── ai/ # 🤖 SISTEMA DE AGENTES IA
│ ├── agente_router.py # Router principal (decide qué agente usar)
│ ├── loader_codigo.py # Carga README y código para contexto
│ ├── contexto_general.py # Contexto global de la plataforma
│ │
│ └── agentes/ # Agentes especializados por juego
│ ├── agente_bingo.py # Asistente para Bingo
│ ├── contexto_bingo.py # Contexto específico del Bingo
│ ├── agente_tetris.py # Asistente para Tetris
│ ├── contexto_tetris.py # Contexto específico del Tetris
│ └── ... (futuros juegos)
│
├── routes/ # 📍 RUTAS Y CONTROLADORES
│ ├── auth_routes.py # Autenticación (login/registro)
│ ├── perfil_routes.py # Perfil de usuario
│ ├── home_routes.py # Página principal
│ ├── admin_routes.py # Panel de administración
│ ├── juego_mate_routes.py # Juego de cálculo
│ ├── puzzle_routes.py # Puzzle matemático
│ ├── english_games_routes.py # Juegos de inglés
│ └── chess_routes.py # Ajedrez
│
├── bingo/ # 🎱 JUEGO DE BINGO
│ │
│ ├── logic/ # Motor compartido
│ │ ├── bolas.py # Gestión del bombo
│ │ ├── cartones.py # Generación de cartones
│ │ ├── validaciones.py # Validación de línea/bingo
│ │ ├── bingo_stats.py # Estadísticas de bingo
│ │ └── bingo_online_stats.py # Estadísticas online
│ │
│ ├── classic/ # Bingo clásico (salas privadas)
│ │ ├── routes/
│ │ │ └── bingo_routes.py # API del bingo clásico
│ │ ├── templates/
│ │ │ └── bingo_sala.html # Interfaz de sala
│ │ └── sockets/
│ │ └── bingo_socket.py # WebSockets tiempo real
│ │
│ └── bingo_online/ # Bingo online (matchmaking)
│ ├── routes/
│ │ └── bingo_online_routes.py
│ ├── templates/
│ │ └── bingo_online.html
│ ├── sockets/
│ │ └── bingo_online_socket.py
│ └── state.py # Estado global de salas
│
├── tetris/ # 🧩 JUEGO DE TETRIS
│ │
│ ├── logic/ # Lógica del juego
│ │ ├── piezas.py # Definición de 7 piezas (I,O,T,S,Z,L,J)
│ │ └── tablero.py # Lógica de movimientos y colisiones
│ │
│ ├── routes/
│ │ └── tetris_routes.py # API REST del Tetris
│ │ ├── / # Página del juego
│ │ ├── /api/nueva-partida # Iniciar partida
│ │ ├── /api/mover # Mover pieza
│ │ ├── /api/estado # Estado actual
│ │ ├── /api/ranking # Ranking global
│ │ └── /api/estadisticas # Estadísticas personales
│ │
│ ├── static/
│ │ ├── tetris.css # Estilos específicos
│ │ └── tetris.js # Cliente con Canvas y controles
│ │
│ └── templates/
│ └── tetris.html # Interfaz del juego
│
├── static/ # 🎨 ARCHIVOS ESTÁTICOS GLOBALES
│ ├── css/
│ │ ├── style.css # Estilos globales
│ │ └── responsive.css # Media queries
│ ├── js/
│ │ ├── main.js # JavaScript global
│ │ └── modal.js # Modal de login/registro
│ └── sounds/ # Efectos de sonido
│
├── templates/ # 📄 PLANTILLAS HTML
│ ├── base.html # Plantilla base con navbar
│ ├── home.html # Página principal con grid de juegos
│ ├── perfil.html # Perfil de usuario
│ ├── login_modal.html # Modal de autenticación
│ └── admin/ # Panel de administración
│ └── dashboard.html
│
├── utils/ # 🛠 UTILIDADES
│ ├── visitas.py # Contador de visitas
│ └── validators.py # Validadores
│
├── models/ # 📊 MODELOS DE DATOS
│ ├── init.py # Exporta modelos
│ └── visita.py # Modelo de visitas
│
├── database/ # 💾 BASE DE DATOS
│ └── play.db # SQLite database
│
└── venv/ # Entorno virtual Python


## 🎮 Juegos Disponibles

### 🎱 Bingo
**Dos modalidades de juego:**
- **Bingo Clásico**: Crea salas privadas para jugar con amigos
- **Bingo Online**: Matchmaking automático con otros jugadores

**Características:**
- ✅ Salas en tiempo real con WebSockets
- ✅ Estadísticas detalladas por jugador
- ✅ Historial de partidas y eventos
- ✅ Sistema de puntos y rankings
- ✅ Asistente IA integrado en cada sala

**API Endpoints:**
- `POST /api/bingo/nueva-sala` - Crear sala privada
- `POST /api/bingo/unirse` - Unirse a sala por código
- `GET /api/bingo/estado/<codigo>` - Estado de la sala
- `POST /api/bingo/sacar-bola` - Extraer bola (admin)
- `POST /api/bingo/cantar-linea` - Cantar línea
- `POST /api/bingo/cantar-bingo` - Cantar bingo

### 🧩 Tetris
**El clásico juego de bloques con características modernas:**

**Mecánicas:**
- 7 piezas clásicas (I, O, T, S, Z, L, J)
- Sistema de niveles (velocidad progresiva)
- Puntuación por líneas (1, 2, 3 o TETRIS)
- Detección automática de TETRIS (4 líneas)
- Game Over al llegar al tope

**Sistema de Puntuación:**
1 línea = 100 × nivel
2 líneas = 300 × nivel
3 líneas = 500 × nivel
4 líneas = 800 × nivel (TETRIS + bonus)


**Controles:**
- **Teclado:** ← → ↑ ↓ (rotar) y Espacio (caída)
- **Móvil:** Botones en pantalla + gestos táctiles
  - Swipe ← → : Mover
  - Swipe ↑ : Rotar
  - Swipe ↓ lento: Bajar rápido
  - Swipe ↓ rápido: Caída instantánea

**API Endpoints:**
- `GET /tetris/` - Interfaz del juego
- `POST /tetris/api/nueva-partida` - Nueva partida
- `POST /tetris/api/mover` - Mover pieza (izquierda/derecha/abajo/rotar)
- `GET /tetris/api/estado` - Estado actual
- `GET /tetris/api/ranking` - Ranking global
- `GET /tetris/api/estadisticas` - Estadísticas personales
- `POST /tetris/api/terminar-partida` - Guardar partida

## 🤖 Sistema de Inteligencia Artificial

El proyecto implementa una arquitectura multi-agente donde cada juego tiene su propio asistente especializado.

### 🔌 Endpoints de IA

#### 1. Agente de Bingo (`/api/bingo-ai`)
```python
POST /api/bingo-ai
{
    "mensaje": "¿Me quedan muchas bolas?",
    "codigo": "ABC123"  # Código de sala (opcional)
}

Response:
{
    "respuesta": "Quedan 45 bolas en el bombo. Los números cantados son: 23, 45, 67..."
}

Contexto disponible cuando hay código de sala:

Lista de jugadores conectados

Últimas bolas extraídas (historial)

Línea cantada (true/false)

Bingo cantado (true/false)

2. Agente de Tetris (/api/tetris-ai)

POST /api/tetris-ai
{
    "tablero": [[0,0,0,...], ...],  # Matriz 10x20
    "pieza_actual": {
        "tipo": "T",
        "forma": [[0,1,0], [1,1,1], [0,0,0]],
        "x": 3,
        "y": 0
    },
    "puntuacion": 1200,
    "nivel": 3
}

Response:
{
    "consejo": "Prueba a rotar la pieza T para encajarla en ese hueco..."
}

Funciones del agente de Tetris:

Explicar reglas básicas

Dar consejos en tiempo real

Sugerir estrategias de colocación

Explicar sistema de puntuación

Ayudar con controles

3. Agente General (/api/ai)

POST /api/ai
{
    "mensaje": "¿Qué juegos hay disponibles?",
    "pagina": "home"  # Página actual (opcional)
}

Response:
{
    "respuesta": "Actualmente tenemos: Bingo, Tetris, Cálculo rápido..."
}
4. Agente Público para Portfolio (/api/agente-portfolio)

POST /api/agente-portfolio
{
    "pregunta": "¿Qué es Juegos Play?"
}

Response:
{
    "respuesta": "Juegos Play es una plataforma de juegos multijugador...",
    "fuente": "agente_juegos"
}

🧠 Arquitectura de Agentes

                    ┌─────────────────┐
                    │  agente_router  │
                    │  (router.py)    │
                    └────────┬────────┘
                             │
              ┌──────────────┼──────────────┐
              │              │              │
         ┌────▼───┐    ┌─────▼────┐   ┌────▼────┐
         │ Bingo  │    │  Tetris  │   │ General │
         │ Agent  │    │  Agent   │   │  Agent  │
         └────────┘    └──────────┘   └─────────┘
              │              │              │
         ┌────▼───┐    ┌─────▼────┐   ┌────▼────┐
         │Contexto│    │ Contexto │   │Contexto │
         │ Bingo  │    │  Tetris  │   │ General │
         └────────┘    └──────────┘   └─────────┘



📊 Base de Datos
Tablas de Usuarios

users (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    email TEXT NOT NULL UNIQUE,
    username TEXT NOT NULL UNIQUE,
    password_hash TEXT NOT NULL,
    best_score INTEGER DEFAULT 0,
    total_score INTEGER DEFAULT 0,
    level_unlocked INTEGER DEFAULT 1,
    role TEXT DEFAULT 'user',
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    reset_token TEXT,
    reset_expires TEXT
);

Tablas de Bingo

-- Estadísticas acumuladas
bingo_stats (
    user_id INTEGER PRIMARY KEY,
    partidas_jugadas INTEGER DEFAULT 0,
    lineas INTEGER DEFAULT 0,
    cruces INTEGER DEFAULT 0,
    x INTEGER DEFAULT 0,
    bingos INTEGER DEFAULT 0,
    bingos_fallidos INTEGER DEFAULT 0,
    puntos_totales INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Historial de partidas
bingo_partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    ganador_id INTEGER,
    duracion_sec INTEGER,
    jugadores INTEGER,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(ganador_id) REFERENCES users(id)
);

-- Eventos de partida
bingo_eventos (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    partida_id INTEGER NOT NULL,
    user_id INTEGER NOT NULL,
    tipo TEXT NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(partida_id) REFERENCES bingo_partidas(id),
    FOREIGN KEY(user_id) REFERENCES users(id)
);

Tablas de Tetris

-- Estadísticas acumuladas
tetris_stats (
    user_id INTEGER PRIMARY KEY,
    partidas_jugadas INTEGER DEFAULT 0,
    puntuacion_maxima INTEGER DEFAULT 0,
    puntuacion_total INTEGER DEFAULT 0,
    lineas_totales INTEGER DEFAULT 0,
    tetris_conseguidos INTEGER DEFAULT 0,
    nivel_maximo INTEGER DEFAULT 1,
    tiempo_total_jugado INTEGER DEFAULT 0,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Historial de partidas
tetris_partidas (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    user_id INTEGER NOT NULL,
    puntuacion INTEGER NOT NULL,
    nivel INTEGER NOT NULL,
    lineas INTEGER NOT NULL,
    tetris_conseguidos INTEGER DEFAULT 0,
    duracion_sec INTEGER NOT NULL,
    created_at TEXT DEFAULT CURRENT_TIMESTAMP,
    FOREIGN KEY(user_id) REFERENCES users(id)
);

-- Índices para mejorar rendimiento
CREATE INDEX IF NOT EXISTS idx_tetris_partidas_user ON tetris_partidas(user_id);
CREATE INDEX IF NOT EXISTS idx_tetris_partidas_puntuacion ON tetris_partidas(puntuacion DESC);

🚀 Instalación
Requisitos Previos
Python 3.12+

pip (gestor de paquetes)

Git

Pasos de Instalación

# 1. Clonar el repositorio
git clone https://github.com/tu-usuario/juegos-play.git
cd juegos-play

# 2. Crear entorno virtual
python -m venv venv

# 3. Activar entorno virtual
# Linux/Mac:
source venv/bin/activate
# Windows:
# venv\Scripts\activate

# 4. Instalar dependencias
pip install -r requirements.txt

# 5. Configurar variables de entorno
cp .env.example .env
# Editar .env con tus valores

# 6. Inicializar base de datos
python db.py

# 7. Ejecutar en desarrollo
python app.py

# 8. Abrir navegador
# http://localhost:5001

Despliegue en Producción (VPS)

# Usar Gunicorn con Eventlet para WebSockets
gunicorn --worker-class eventlet \
         -w 1 \
         --bind 0.0.0.0:5000 \
         --access-logfile - \
         --error-logfile - \
         app:app

# Con systemd (recomendado)
# Crear archivo /etc/systemd/system/juegos-play.service

🛠 Tecnologías
Backend
Framework: Flask 3.0+

Tiempo Real: Flask-SocketIO, Eventlet

Base de Datos: SQLite + sqlite3

IA: LiteLLM (integración con múltiples LLMs)

Autenticación: Sesiones con cookies seguras

Frontend
HTML5/CSS3: Diseño responsive

JavaScript: Canvas para juegos

WebSockets: Comunicación tiempo real

PWA: Manifest y Service Workers

Herramientas de Desarrollo
Control de versiones: Git

Entorno virtual: venv

Dependencias: pip + requirements.txt

✨ Características
✅ Implementadas
Sistema de autenticación (registro/login)

Perfiles de usuario

Juego de Bingo completo (clásico y online)

Juego de Tetris completo

Juego de cálculo rápido

Puzzle matemático

Juegos de inglés

Ajedrez multijugador

Rankings globales

Estadísticas personales

Asistente IA para Bingo

Asistente IA para Tetris

Controles táctiles para móvil

Panel de administración

Contador de visitas

🚧 En Desarrollo
Más juegos (Sudoku, Wordle)

Torneos semanales

Logros y medallas

Amigos y mensajería

Modo oscuro

Soporte para más idiomas

📄 Licencia
© 2024 Jesús CM - Todos los derechos reservados.

👤 Autor
Jesús CM

📧 Email: jcm201080@gmail.com

🌐 Web: jesuscmweb.com

🐙 GitHub: @jcm201080

⭐ ¿Te gusta el proyecto? ¡No olvides darle una estrella en GitHub!