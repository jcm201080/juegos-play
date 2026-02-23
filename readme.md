juegos-play/
│
├── app.py
├── config.py
├── db.py
├── README.md
│
├── routes/                    # Rutas generales de la plataforma
│   ├── auth_routes.py
│   ├── perfil_routes.py
│   ├── home_routes.py
│   └── ...
│
├── bingo/
│   │
│   ├── logic/                 # 🔥 LÓGICA COMPARTIDA (motor común)
│   │   ├── bolas.py
│   │   ├── cartones.py
│   │   ├── validaciones.py
│   │   └── bingo_stats.py
│   │
│   ├── classic/
│   │   ├── routes/
│   │   │   ├── bingo_routes.py
│   │   │   └── ranking_routes.py
│   │   │
│   │   ├── templates/
│   │   │   ├── bingo_sala.html
│   │   │   ├── ranking_classic.html
│   │   │   └── ...
│   │   │
│   │   └── static/
│   │
│   ├── online/
│   │   ├── routes/
│   │   │   ├── bingo_routes.py
│   │   │   └── ranking_routes.py
│   │   │
│   │   ├── templates/
│   │   │   ├── bingo_online.html
│   │   │   └── ranking_online.html
│   │   │
│   │   └── static/
│
├── static/
│   ├── css/
│   ├── js/
│   └── sounds/
│
└── templates/
    ├── base.html
    ├── home.html
    ├── perfil.html
    └── ...
