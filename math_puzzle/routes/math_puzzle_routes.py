from flask import Blueprint, render_template, session, jsonify, request
from db import (
    get_connection, 
    guardar_puntuacion_math_puzzle,
    obtener_ranking_math_puzzle,
    obtener_estadisticas_math_puzzle,
    ensure_math_puzzle_stats
)
import math_puzzle.logic.grid_generator as grid_gen
import random
import hashlib
from datetime import datetime

math_puzzle_bp = Blueprint('math_puzzle', 
                          __name__, 
                          template_folder='../templates',
                          static_folder='../static',      # Apunta a math_puzzle/static/
                          static_url_path='/static/math_puzzle')

@math_puzzle_bp.route('/math-puzzle')
def math_puzzle():
    """Página principal del puzzle"""
    if 'user_id' not in session:
        return render_template('login_modal.html', game_redirect='math_puzzle')
    
    # Asegurar que el usuario tiene estadísticas
    ensure_math_puzzle_stats(session['user_id'])
    
    # Obtener estadísticas del usuario
    stats = obtener_estadisticas_math_puzzle(session['user_id'])
    
    return render_template('math_puzzle.html', stats=stats)

@math_puzzle_bp.route('/api/math-puzzle/new', methods=['POST'])
def new_puzzle():
    """Genera un nuevo puzzle según nivel"""
    data = request.get_json()
    level = data.get('level', 2)
    user_id = session.get('user_id')
    
    # Validar nivel
    if level not in [1, 2, 3]:
        level = 2
    
    puzzle = grid_gen.generate_puzzle(level, user_id)
    return jsonify(puzzle)

@math_puzzle_bp.route('/api/math-puzzle/validate', methods=['POST'])
def validate_solution():
    """Valida la solución del usuario"""
    data = request.get_json()
    user_grid = data.get('grid')
    puzzle_id = data.get('puzzle_id')
    time_spent = data.get('time_spent', 0)
    lives = data.get('lives', 5)
    user_id = session.get('user_id')
    
    if not user_id:
        return jsonify({'valid': False, 'message': 'Usuario no autenticado'}), 401
    
    # Validar la solución
    is_valid, score, message = grid_gen.validate_solution(user_grid, puzzle_id, time_spent, lives)
    
    if is_valid and user_id:
        # Obtener nivel del puzzle (deberías almacenarlo en algún lado)
        # Por ahora lo obtenemos del grid o de una sesión temporal
        level = data.get('level', 2)
        
        # Guardar puntuación en la base de datos
        guardar_puntuacion_math_puzzle(
            user_id=user_id,
            puzzle_id=puzzle_id,
            level=level,
            score=score,
            time_spent=time_spent,
            lives_remaining=lives
        )
    
    return jsonify({
        'valid': is_valid,
        'score': score,
        'message': message,
        'lives': lives
    })

@math_puzzle_bp.route('/api/math-puzzle/ranking')
def get_ranking():
    """Obtiene ranking global o por nivel"""
    level = request.args.get('level', 2, type=int)
    ranking = obtener_ranking_math_puzzle(level=level, limite=10)
    return jsonify(ranking)

@math_puzzle_bp.route('/api/math-puzzle/stats')
def get_stats():
    """Obtiene estadísticas del usuario"""
    if 'user_id' not in session:
        return jsonify({'error': 'No autenticado'}), 401
    
    stats = obtener_estadisticas_math_puzzle(session['user_id'])
    return jsonify(stats)

@math_puzzle_bp.route('/api/math-puzzle/hint', methods=['POST'])
def get_hint():
    """Solicita una pista (simulada por ahora)"""
    data = request.get_json()
    level = data.get('level', 2)
    current_grid = data.get('grid', [])
    
    # Pistas según nivel
    hints = {
        1: [
            "💡 Empieza por las esquinas, suelen ser más fáciles",
            "🔍 Mira las operaciones de suma, son las más directas",
            "🎯 Los números pequeños suelen ir en operaciones de resta"
        ],
        2: [
            "🔢 Las multiplicaciones te ayudarán a encontrar números grandes",
            "💭 Prueba combinando sumas y restas en la misma fila",
            "✨ Fíjate en los resultados, te darán pistas"
        ],
        3: [
            "🧮 Las divisiones son exactas, busca divisores perfectos",
            "🎲 Intenta resolver las operaciones con resultados más pequeños primero",
            "⚡ Usa la lógica: si un número solo encaja en un lugar, ese es el correcto"
        ]
    }
    
    hint = random.choice(hints.get(level, hints[2]))
    
    return jsonify({'hint': hint})