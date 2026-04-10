import random
import hashlib
from datetime import datetime

class MathPuzzleGenerator:
    def __init__(self):
        self.levels = {
            1: {  # Fácil - solo sumas/restas
                'operations': ['+', '-'],
                'grid_size': 3,
                'min_number': 1,
                'max_number': 20,
                'empty_cells': 4  # Número de celdas vacías
            },
            2: {  # Medio - sumas/restas/multiplicaciones
                'operations': ['+', '-', '×'],
                'grid_size': 3,
                'min_number': 1,
                'max_number': 30,
                'empty_cells': 5
            },
            3: {  # Difícil - todas las operaciones
                'operations': ['+', '-', '×', '÷'],
                'grid_size': 4,
                'min_number': 1,
                'max_number': 50,
                'empty_cells': 8
            }
        }
    
    def _calcular(self, a, b, op):
        """Calcula el resultado de una operación de forma segura"""
        if op == '+':
            return a + b
        elif op == '-':
            return a - b
        elif op == '×':
            return a * b
        elif op == '÷':
            # Solo divisiones exactas
            if b != 0 and a % b == 0:
                return a // b
            return None
        return None
    
    def _generar_numero_seguro(self, min_val, max_val, exclude=None):
        """Genera un número evitando valores excluidos"""
        if exclude is None:
            exclude = []
        while True:
            num = random.randint(min_val, max_val)
            if num not in exclude:
                return num
    
    def _generar_fila_valida(self, size, min_val, max_val, operations):
        """Genera una fila con operaciones válidas"""
        numeros = []
        ops_horizontal = []
        
        # Generar números aleatorios
        for i in range(size):
            numeros.append(random.randint(min_val, max_val))
        
        # Generar operaciones válidas
        for i in range(size - 1):
            op = random.choice(operations)
            resultado = self._calcular(numeros[i], numeros[i+1], op)
            
            # Si la operación no es válida (especialmente división), cambiamos números
            intentos = 0
            while resultado is None and intentos < 10:
                if op == '÷':
                    # Para división, aseguramos que sea exacta
                    numeros[i+1] = self._generar_numero_seguro(1, max_val // 2)
                    resultado = self._calcular(numeros[i], numeros[i+1], op)
                intentos += 1
            
            if resultado is None:
                # Si no funciona, cambiamos la operación
                op = random.choice(['+', '-', '×'])
                resultado = self._calcular(numeros[i], numeros[i+1], op)
            
            ops_horizontal.append(op)
        
        return numeros, ops_horizontal
    
    def _generar_grid_valido(self, config):
        """Genera un grid completo con todas las operaciones válidas"""
        size = config['grid_size']
        min_val = config['min_number']
        max_val = config['max_number']
        operations = config['operations']
        
        # Generar todas las filas
        grid_numeros = []
        ops_horizontales = []
        
        for i in range(size):
            numeros, ops_fila = self._generar_fila_valida(size, min_val, max_val, operations)
            grid_numeros.append(numeros)
            ops_horizontales.append(ops_fila)
        
        # Verificar operaciones verticales
        ops_verticales = []
        for col in range(size):
            ops_col = []
            for row in range(size - 1):
                # Buscar una operación válida para esta columna
                op = random.choice(operations)
                resultado = self._calcular(grid_numeros[row][col], grid_numeros[row+1][col], op)
                
                intentos = 0
                while resultado is None and intentos < 10:
                    op = random.choice(operations)
                    resultado = self._calcular(grid_numeros[row][col], grid_numeros[row+1][col], op)
                    intentos += 1
                
                if resultado is None:
                    # Si no hay operación válida, ajustamos los números
                    op = random.choice(['+', '-', '×'])
                    resultado = self._calcular(grid_numeros[row][col], grid_numeros[row+1][col], op)
                
                ops_col.append(op)
            ops_verticales.append(ops_col)
        
        return grid_numeros, ops_horizontales, ops_verticales
    
    def generate_puzzle(self, level, user_id=None):
        """Genera un puzzle válido"""
        config = self.levels[level]
        
        # Generar grid válido
        numeros, ops_h, ops_v = self._generar_grid_valido(config)
        
        # Crear grid con operaciones
        grid_completo = []
        size = config['grid_size']
        
        for i in range(size):
            row = []
            for j in range(size):
                celda = {
                    'value': numeros[i][j],
                    'right_op': ops_h[i][j] if j < size - 1 else None,
                    'down_op': ops_v[j][i] if i < size - 1 else None,  # Transpuesto
                }
                
                # Calcular resultados
                if j < size - 1:
                    celda['right_result'] = self._calcular(
                        numeros[i][j], numeros[i][j+1], ops_h[i][j]
                    )
                if i < size - 1:
                    celda['down_result'] = self._calcular(
                        numeros[i][j], numeros[i+1][j], ops_v[j][i]
                    )
                
                row.append(celda)
            grid_completo.append(row)
        
        # Quitar números para el puzzle
        puzzle_grid = []
        numbers_pool = []
        celdas_vacias = config['empty_cells']
        
        # Hacer copia profunda
        for i in range(size):
            row = []
            for j in range(size):
                row.append(grid_completo[i][j].copy())
            puzzle_grid.append(row)
        
        # Quitar números aleatoriamente
        posiciones = [(i, j) for i in range(size) for j in range(size)]
        random.shuffle(posiciones)
        
        for i, j in posiciones[:celdas_vacias]:
            if puzzle_grid[i][j]['value'] is not None:
                numbers_pool.append(puzzle_grid[i][j]['value'])
                puzzle_grid[i][j]['value'] = None
        
        # Mezclar pool
        random.shuffle(numbers_pool)
        
        # ID único
        unique_str = str(grid_completo) + str(datetime.now())
        if user_id:
            unique_str += str(user_id)
        puzzle_id = hashlib.md5(unique_str.encode()).hexdigest()[:8]
        
        return {
            'id': puzzle_id,
            'grid': puzzle_grid,
            'numbers_pool': numbers_pool,
            'level': level,
            'grid_size': size,
            'max_lives': 5,
            'time_limit': 180 - (level * 30)  # 150s, 120s, 90s
        }
    
    def validate_solution(self, user_grid, puzzle_id, time_spent, lives):
        """Valida la solución del usuario"""
        # Aquí deberías comparar con la solución original
        # Por ahora, asumimos que es válida para pruebas
        score = 1000 - time_spent + (lives * 100)
        return True, max(score, 100), "¡Correcto! 🎉"

generator = MathPuzzleGenerator()
generate_puzzle = generator.generate_puzzle
validate_solution = generator.validate_solution