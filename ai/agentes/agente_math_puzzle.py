from ai.contexto_general import contexto_plataforma
import json

class AgenteMathPuzzle:
    def __init__(self):
        self.nombre = "Math Puzzle Assistant"
        self.contexto = self._cargar_contexto()
    
    def _cargar_contexto(self):
        return """
        Eres un asistente especializado en el juego Math Grid Puzzle.
        
        REGLAS DEL JUEGO:
        - Grid con operaciones matemáticas (+, -, ×, ÷)
        - Los números deben cumplir las operaciones horizontales y verticales
        - Cada número solo se usa una vez
        - 5 vidas por partida
        - Puntuación base + bonus por tiempo
        
        ESTRATEGIAS DE AYUDA:
        1. Para principiantes: sugerir empezar por las esquinas
        2. Para nivel medio: señalar operaciones con resultados únicos
        3. Para nivel difícil: dar pistas sobre restricciones lógicas
        4. Nunca dar la solución completa
        
        TIPOS DE PISTA:
        - "Prueba a colocar el número X en la celda (fila,columna)"
        - "El resultado de la operación en esta fila debe ser Y"
        - "Este número solo puede ir en estas 2 posiciones"
        """
    
    def generar_pista(self, puzzle_data, grid_actual):
        """Genera una pista personalizada según el estado actual"""
        # Analizar el grid actual
        celdas_vacias = self._contar_vacias(grid_actual)
        nivel = puzzle_data.get('level', 1)
        
        if celdas_vacias > 8:
            return "🔍 Empieza por las celdas que tienen operaciones con resultados fijos"
        elif celdas_vacias > 4:
            return "💡 Fíjate en las operaciones de multiplicación, suelen tener menos combinaciones posibles"
        else:
            return "🎯 Ya casi lo tienes! Revisa las operaciones con números grandes"
    
    def _contar_vacias(self, grid):
        vacias = 0
        for row in grid:
            for cell in row:
                if cell.get('value') is None:
                    vacias += 1
        return vacias

# Instancia global
agente_puzzle = AgenteMathPuzzle()