# tetris/logic/tablero.py
from tetris.logic.piezas import PiezaTetris
import random

class TableroTetris:
    """Gestiona el tablero y la lógica del juego"""
    
    def __init__(self, ancho=10, alto=20):
        self.ancho = ancho
        self.alto = alto
        self.tablero = [[0 for _ in range(ancho)] for _ in range(alto)]
        self.pieza_actual = None
        self.siguiente_pieza = None
        self.puntuacion = 0
        self.nivel = 1
        self.lineas_completadas = 0
        self.game_over = False
        
        # Inicializar piezas
        self.generar_nueva_pieza()
        self.generar_siguiente_pieza()
        
    def generar_nueva_pieza(self):
        """Genera una nueva pieza para el juego"""
        if self.siguiente_pieza:
            self.pieza_actual = self.siguiente_pieza
            self.pieza_actual.x = self.ancho // 2 - 2
            self.pieza_actual.y = 0
        else:
            self.pieza_actual = PiezaTetris()
            self.pieza_actual.x = self.ancho // 2 - 2
            self.pieza_actual.y = 0
            
        self.generar_siguiente_pieza()
        
        # Verificar si la nueva pieza colisiona (game over)
        if self.colisiona(self.pieza_actual):
            self.game_over = True
            
    def generar_siguiente_pieza(self):
        """Genera la siguiente pieza"""
        self.siguiente_pieza = PiezaTetris()
        
    def colisiona(self, pieza):
        """Verifica si una pieza colisiona con el tablero o bordes"""
        for x, y in pieza.obtener_posiciones():
            # Fuera del tablero
            if x < 0 or x >= self.ancho or y >= self.alto:
                return True
            # Colisión con piezas fijadas
            if y >= 0 and self.tablero[y][x]:
                return True
        return False
        
    def fijar_pieza(self):
        """Fija la pieza actual en el tablero"""
        for x, y in self.pieza_actual.obtener_posiciones():
            if y >= 0:
                self.tablero[y][x] = self.pieza_actual.tipo
                
        # Completar líneas
        lineas_eliminadas = self.eliminar_lineas_completas()
        
        # Actualizar puntuación
        if lineas_eliminadas > 0:
            self.actualizar_puntuacion(lineas_eliminadas)
            
        # Generar nueva pieza
        self.generar_nueva_pieza()
        
    def eliminar_lineas_completas(self):
        """Elimina las líneas completas y devuelve el número eliminado"""
        lineas_eliminadas = 0
        y = self.alto - 1
        
        while y >= 0:
            if all(self.tablero[y]):
                # Eliminar línea
                lineas_eliminadas += 1
                # Mover todas las líneas superiores hacia abajo
                for y2 in range(y, 0, -1):
                    self.tablero[y2] = self.tablero[y2-1][:]
                # La línea superior queda vacía
                self.tablero[0] = [0 for _ in range(self.ancho)]
            else:
                y -= 1
                
        return lineas_eliminadas
        
    def actualizar_puntuacion(self, lineas):
        """Actualiza la puntuación según las líneas eliminadas"""
        # Puntuación clásica del Tetris
        puntuaciones = {1: 100, 2: 300, 3: 500, 4: 800}
        self.puntuacion += puntuaciones.get(lineas, 0) * self.nivel
        
        self.lineas_completadas += lineas
        # Cada 10 líneas, sube el nivel
        self.nivel = 1 + (self.lineas_completadas // 10)
        
    def mover_pieza(self, direccion):
        """Mueve la pieza en la dirección indicada"""
        if self.game_over:
            return {'error': 'Game Over'}
            
        pieza_prueba = self.pieza_actual.copia()
        
        if direccion == 'izquierda':
            pieza_prueba.x -= 1
        elif direccion == 'derecha':
            pieza_prueba.x += 1
        elif direccion == 'abajo':
            pieza_prueba.y += 1
        elif direccion == 'rotar':
            pieza_prueba.rotar()
            
        # Verificar si el movimiento es válido
        if not self.colisiona(pieza_prueba):
            self.pieza_actual = pieza_prueba
            return {'movimiento': 'ok'}
        elif direccion == 'abajo':
            # Si no puede bajar más, fijar la pieza
            self.fijar_pieza()
            return {'movimiento': 'fijado'}
        else:
            return {'movimiento': 'bloqueado'}
            
    def to_dict(self):
        """Convierte el tablero a diccionario para guardar en sesión"""
        return {
            'tablero': self.tablero,
            'pieza_actual': {
                'tipo': self.pieza_actual.tipo,
                'x': self.pieza_actual.x,
                'y': self.pieza_actual.y,
                'forma': self.pieza_actual.forma
            } if self.pieza_actual else None,
            'siguiente_pieza': {
                'tipo': self.siguiente_pieza.tipo,
                'forma': self.siguiente_pieza.forma
            } if self.siguiente_pieza else None,
            'puntuacion': self.puntuacion,
            'nivel': self.nivel,
            'lineas_completadas': self.lineas_completadas,
            'game_over': self.game_over,
            'ancho': self.ancho,
            'alto': self.alto
        }
        
    @classmethod
    def from_dict(cls, data):
        """Crea un tablero desde un diccionario"""
        tablero = cls(data.get('ancho', 10), data.get('alto', 20))
        tablero.tablero = data['tablero']
        tablero.puntuacion = data['puntuacion']
        tablero.nivel = data['nivel']
        tablero.lineas_completadas = data['lineas_completadas']
        tablero.game_over = data['game_over']
        
        # Restaurar pieza actual
        if data.get('pieza_actual'):
            pieza = PiezaTetris(data['pieza_actual']['tipo'])
            pieza.x = data['pieza_actual']['x']
            pieza.y = data['pieza_actual']['y']
            pieza.forma = data['pieza_actual']['forma']
            tablero.pieza_actual = pieza
            
        # Restaurar siguiente pieza
        if data.get('siguiente_pieza'):
            tablero.siguiente_pieza = PiezaTetris(data['siguiente_pieza']['tipo'])
            tablero.siguiente_pieza.forma = data['siguiente_pieza']['forma']
            
        return tablero