# tetris/routes/tetris_routes.py
from flask import Blueprint, render_template, jsonify, request, session
import json
import time
from tetris.logic.piezas import PiezaTetris
from tetris.logic.tablero import TableroTetris

# Importar tu decorador de autenticación
from routes.auth_routes import login_required

# Importar funciones de base de datos
from db import (
    guardar_partida_tetris, 
    ensure_tetris_stats, 
    obtener_ranking_tetris,
    obtener_estadisticas_tetris,
    obtener_ultimas_partidas_tetris
)

# Crear el blueprint
tetris_bp = Blueprint('tetris', __name__, 
                      url_prefix='/tetris',
                      template_folder='../templates',
                      static_folder='../static',
                      static_url_path='/static/tetris')

# Función auxiliar para obtener el usuario actual
def get_current_user():
    """Obtiene el usuario actual de la sesión"""
    user_id = session.get('user_id')
    if user_id:
        # Crear un objeto usuario simple con los datos de la sesión
        class Usuario:
            def __init__(self, id, username):
                self.id = id
                self.username = username
                self.is_authenticated = True
        
        return Usuario(user_id, session.get('username', 'Usuario'))
    return None

@tetris_bp.route('/')
@login_required
def index():
    """Página principal del Tetris"""
    user = get_current_user()
    return render_template('tetris.html', 
                         usuario=user,
                         titulo="Tetris - Juegos Play")

@tetris_bp.route('/api/nueva-partida', methods=['POST'])
@login_required
def nueva_partida():
    """Inicia una nueva partida"""
    try:
        user_id = session.get('user_id')
        
        # Asegurar que tiene estadísticas en la BD
        ensure_tetris_stats(user_id)
        
        # Crear nuevo tablero
        tablero = TableroTetris()
        
        # Guardar estado inicial en sesión
        session['tetris_tablero'] = tablero.to_dict()
        session['tetris_puntuacion'] = 0
        session['tetris_nivel'] = 1
        session['tetris_lineas'] = 0
        session['tetris_tetris_count'] = 0
        session['tetris_partida_activa'] = True
        session['tetris_tiempo_inicio'] = time.time()
        
        return jsonify({
            'success': True,
            'mensaje': 'Nueva partida creada',
            'tablero': tablero.to_dict()
        })
    except Exception as e:
        print(f"Error en nueva_partida: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tetris_bp.route('/api/mover', methods=['POST'])
@login_required
def mover_pieza():
    """Mueve la pieza actual"""
    try:
        data = request.json
        direccion = data.get('direccion')
        
        # Recuperar estado de la sesión
        tablero_dict = session.get('tetris_tablero')
        if not tablero_dict:
            return jsonify({
                'success': False,
                'error': 'No hay partida activa'
            }), 400
        
        tablero = TableroTetris.from_dict(tablero_dict)
        
        # Guardar líneas antes del movimiento para detectar tetris
        lineas_antes = tablero.lineas_completadas
        
        # Procesar movimiento
        resultado = tablero.mover_pieza(direccion)
        
        # Detectar si se hizo un tetris (4 líneas de golpe)
        if 'fijado' in resultado.get('movimiento', '') and tablero.lineas_completadas - lineas_antes >= 4:
            session['tetris_tetris_count'] = session.get('tetris_tetris_count', 0) + 1
        
        # Actualizar sesión
        session['tetris_tablero'] = tablero.to_dict()
        session['tetris_puntuacion'] = tablero.puntuacion
        session['tetris_nivel'] = tablero.nivel
        session['tetris_lineas'] = tablero.lineas_completadas
        
        # Si es game over, guardar la partida automáticamente
        if tablero.game_over:
            user_id = session.get('user_id')
            tiempo_inicio = session.get('tetris_tiempo_inicio', time.time())
            duracion = int(time.time() - tiempo_inicio)
            
            guardar_partida_tetris(
                user_id=user_id,
                puntuacion=tablero.puntuacion,
                nivel=tablero.nivel,
                lineas=tablero.lineas_completadas,
                tetris_conseguidos=session.get('tetris_tetris_count', 0),
                duracion_sec=duracion
            )
            
            # Limpiar sesión de juego (opcional)
            session['tetris_partida_activa'] = False
        
        return jsonify({
            'success': True,
            'tablero': tablero.to_dict(),
            'puntuacion': tablero.puntuacion,
            'nivel': tablero.nivel,
            'lineas': tablero.lineas_completadas,
            'tetris_count': session.get('tetris_tetris_count', 0),
            'game_over': tablero.game_over
        })
        
    except Exception as e:
        print(f"Error en mover_pieza: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tetris_bp.route('/api/estado', methods=['GET'])
@login_required
def obtener_estado():
    """Obtiene el estado actual de la partida"""
    try:
        tiempo_actual = time.time()
        tiempo_inicio = session.get('tetris_tiempo_inicio', tiempo_actual)
        duracion = int(tiempo_actual - tiempo_inicio) if session.get('tetris_partida_activa') else 0
        
        return jsonify({
            'success': True,
            'tablero': session.get('tetris_tablero'),
            'puntuacion': session.get('tetris_puntuacion', 0),
            'nivel': session.get('tetris_nivel', 1),
            'lineas': session.get('tetris_lineas', 0),
            'tetris_count': session.get('tetris_tetris_count', 0),
            'partida_activa': session.get('tetris_partida_activa', False),
            'tiempo_segundos': duracion
        })
    except Exception as e:
        print(f"Error en obtener_estado: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tetris_bp.route('/api/terminar-partida', methods=['POST'])
@login_required
def terminar_partida():
    """Termina la partida actual y guarda puntuación"""
    try:
        user_id = session.get('user_id')
        puntuacion = session.get('tetris_puntuacion', 0)
        nivel = session.get('tetris_nivel', 1)
        lineas = session.get('tetris_lineas', 0)
        tetris_count = session.get('tetris_tetris_count', 0)
        tiempo_inicio = session.get('tetris_tiempo_inicio', time.time())
        duracion = int(time.time() - tiempo_inicio)
        
        # Guardar la partida en la BD
        if user_id and puntuacion > 0:
            guardar_partida_tetris(
                user_id=user_id,
                puntuacion=puntuacion,
                nivel=nivel,
                lineas=lineas,
                tetris_conseguidos=tetris_count,
                duracion_sec=duracion
            )
        
        # Limpiar sesión
        session.pop('tetris_tablero', None)
        session.pop('tetris_puntuacion', None)
        session.pop('tetris_nivel', None)
        session.pop('tetris_lineas', None)
        session.pop('tetris_tetris_count', None)
        session.pop('tetris_partida_activa', None)
        session.pop('tetris_tiempo_inicio', None)
        
        return jsonify({
            'success': True,
            'mensaje': 'Partida terminada',
            'puntuacion_final': puntuacion
        })
    except Exception as e:
        print(f"Error en terminar_partida: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tetris_bp.route('/api/ranking', methods=['GET'])
@login_required
def ranking():
    """Obtiene el ranking de Tetris"""
    try:
        ranking_data = obtener_ranking_tetris(limite=10)
        return jsonify({
            'success': True,
            'ranking': ranking_data
        })
    except Exception as e:
        print(f"Error en ranking: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

@tetris_bp.route('/api/estadisticas', methods=['GET'])
@login_required
def estadisticas():
    """Obtiene las estadísticas del usuario actual"""
    try:
        user_id = session.get('user_id')
        stats = obtener_estadisticas_tetris(user_id)
        ultimas_partidas = obtener_ultimas_partidas_tetris(user_id, limite=5)
        
        return jsonify({
            'success': True,
            'estadisticas': stats,
            'ultimas_partidas': ultimas_partidas
        })
    except Exception as e:
        print(f"Error en estadisticas: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500

# Endpoint de prueba para ver la sesión
@tetris_bp.route('/api/debug', methods=['GET'])
def debug_sesion():
    """Muestra información de la sesión (solo para desarrollo)"""
    return jsonify({
        'session_data': {
            'user_id': session.get('user_id'),
            'username': session.get('username'),
            'tetris_partida_activa': session.get('tetris_partida_activa', False),
            'tetris_puntuacion': session.get('tetris_puntuacion', 0),
            'tetris_nivel': session.get('tetris_nivel', 1),
            'tetris_lineas': session.get('tetris_lineas', 0),
            'tetris_tetris_count': session.get('tetris_tetris_count', 0),
            'session_keys': list(session.keys())
        }
    })


# tetris/routes/tetris_routes.py - Añadir al final

@tetris_bp.route('/api/ia', methods=['POST'])
@login_required
def consultar_ia():
    """Endpoint para el asistente IA del Tetris"""
    try:
        data = request.json
        pregunta = data.get('pregunta', '')
        
        if not pregunta:
            return jsonify({
                'success': False,
                'error': 'No se recibió ninguna pregunta'
            }), 400
        
        # Obtener contexto actual de la partida si existe
        contexto_partida = None
        tablero_dict = session.get('tetris_tablero')
        
        if tablero_dict:
            contexto_partida = {
                'tablero': tablero_dict.get('tablero', []),
                'pieza_actual': tablero_dict.get('pieza_actual'),
                'puntuacion': session.get('tetris_puntuacion', 0),
                'nivel': session.get('tetris_nivel', 1),
                'lineas': session.get('tetris_lineas', 0)
            }
        
        # Usar el router de IA
        from ai.agente_router import preguntar_agente_general
        
        respuesta = preguntar_agente_general(
            pregunta=pregunta,
            pagina="tetris",
            contexto_adicional=contexto_partida
        )
        
        return jsonify({
            'success': True,
            'respuesta': respuesta
        })
        
    except Exception as e:
        print(f"Error en consultar_ia: {e}")
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500