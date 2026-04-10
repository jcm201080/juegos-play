juegos-play/
│
├── routes/
│   └── math_puzzle_routes.py          # Rutas del puzzle
│
├── math_puzzle/                        # 📐 JUEGO DE PUZZLE MATEMÁTICO
│   ├── logic/
│   │   ├── grid_generator.py           # Genera grids según nivel
│   │   ├── puzzle_validator.py         # Valida soluciones
│   │   └── puzzle_stats.py             # Estadísticas y ranking
│   │
│   ├── templates/
│   │   └── math_puzzle.html            # Interfaz del juego
│   │
│   ├── static/
│   │   ├── css/
│   │   │   └── math_puzzle.css         # Estilos específicos
│   │   └── js/
│   │       └── math_puzzle.js          # Lógica cliente (drag & drop, timer)
│   │
│   └── levels/                          # Configuración por nivel
│       ├── level_1.json                 # Fácil (solo sumas/restas)
│       ├── level_2.json                 # Medio (con multiplicación)
│       └── level_3.json                 # Difícil (operaciones combinadas)
│
├── ai/agentes/
│   └── agente_math_puzzle.py            # Asistente IA para el puzzle
│
└── database/
    └── migrations/
        └── add_math_puzzle_tables.sql   # Tablas para puntuaciones