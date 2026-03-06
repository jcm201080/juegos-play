# tetris/logic/piezas.py
import random

class PiezaTetris:
    """Define las piezas del Tetris"""
    
    # Formas de las piezas (matrices 4x4)
    FORMAS = {
        'I': [
            [0, 0, 0, 0],
            [1, 1, 1, 1],
            [0, 0, 0, 0],
            [0, 0, 0, 0]
        ],
        'O': [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
        ],
        'T': [
            [0, 0, 0, 0],
            [0, 1, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0]
        ],
        'S': [
            [0, 0, 0, 0],
            [0, 1, 1, 0],
            [1, 1, 0, 0],
            [0, 0, 0, 0]
        ],
        'Z': [
            [0, 0, 0, 0],
            [1, 1, 0, 0],
            [0, 1, 1, 0],
            [0, 0, 0, 0]
        ],
        'L': [
            [0, 0, 0, 0],
            [1, 0, 0, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0]
        ],
        'J': [
            [0, 0, 0, 0],
            [0, 0, 1, 0],
            [1, 1, 1, 0],
            [0, 0, 0, 0]
        ]
    }
    
    # Colores para cada pieza (hex)
    COLORES = {
        'I': '#00ffff',  # Cian
        'O': '#ffff00',  # Amarillo
        'T': '#aa00ff',  # Morado
        'S': '#00ff00',  # Verde
        'Z': '#ff0000',  # Rojo
        'L': '#ffaa00',  # Naranja
        'J': '#0000ff'   # Azul
    }
    
    def __init__(self, tipo=None):
        if tipo is None:
            tipo = random.choice(list(self.FORMAS.keys()))
        self.tipo = tipo
        self.forma = [fila[:] for fila in self.FORMAS[tipo]]
        self.color = self.COLORES[tipo]
        self.x = 3  # Posición inicial en el tablero (columna)
        self.y = 0  # Posición inicial en el tablero (fila)
        
    def rotar(self):
        """Rota la pieza 90 grados a la derecha"""
        # Transponer la matriz y luego invertir cada fila
        nueva_forma = []
        for i in range(len(self.forma[0])):
            nueva_fila = []
            for j in range(len(self.forma) - 1, -1, -1):
                nueva_fila.append(self.forma[j][i])
            nueva_forma.append(nueva_fila)
        self.forma = nueva_forma
        
    def copia(self):
        """Crea una copia de la pieza"""
        nueva_pieza = PiezaTetris(self.tipo)
        nueva_pieza.forma = [fila[:] for fila in self.forma]
        nueva_pieza.x = self.x
        nueva_pieza.y = self.y
        return nueva_pieza
        
    def obtener_posiciones(self):
        """Devuelve las posiciones ocupadas por la pieza"""
        posiciones = []
        for i, fila in enumerate(self.forma):
            for j, valor in enumerate(fila):
                if valor:
                    posiciones.append((self.x + j, self.y + i))
        return posiciones