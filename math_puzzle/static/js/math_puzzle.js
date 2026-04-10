class MathPuzzleGame {
    constructor() {
        this.grid = [];
        this.numbersPool = [];
        this.puzzleId = null;
        this.level = 2;
        this.lives = 5;
        this.score = 0;
        this.seconds = 0;
        this.timer = null;
        this.gridSize = 3;
        
        this.init();
    }
    
    init() {
        console.log("🎮 Math Puzzle inicializado");
        document.getElementById('newGameBtn').addEventListener('click', () => this.newGame());
        document.getElementById('levelSelect').addEventListener('change', (e) => {
            this.level = parseInt(e.target.value);
            this.newGame();
        });
        document.getElementById('checkSolutionBtn').addEventListener('click', () => this.checkSolution());
        document.getElementById('hintBtn').addEventListener('click', () => this.getHint());
        document.getElementById('resetBtn').addEventListener('click', () => this.resetGame());
        
        // Cerrar modal
        document.querySelector('.close')?.addEventListener('click', () => {
            document.getElementById('hintModal').style.display = 'none';
        });
        
        this.newGame();
    }
    
    newGame() {
        console.log("🆕 Nuevo juego, nivel:", this.level);
        
        fetch('/api/math-puzzle/new', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({ level: this.level })
        })
        .then(res => res.json())
        .then(data => {
            console.log("📦 Puzzle recibido:", data);
            this.grid = data.grid;
            this.numbersPool = data.numbers_pool;
            this.puzzleId = data.id;
            this.lives = data.max_lives || 5;
            this.gridSize = data.grid_size || 3;
            
            document.getElementById('lives').textContent = this.lives;
            document.getElementById('score').textContent = this.score;
            
            this.renderGrid();
            this.renderNumbersPool();
            this.startTimer();
            this.updateRanking();
        })
        .catch(err => {
            console.error("❌ Error:", err);
            alert("Error al cargar el puzzle");
        });
    }
    
    renderGrid() {
        const gridElement = document.getElementById('puzzleGrid');
        gridElement.innerHTML = '';
        
        const size = this.gridSize; // Supongamos 3 (para un puzzle de 2x2 números + resultados)
        const visualSize = size * 2 - 1; 

        for (let i = 0; i < visualSize; i++) {
            const row = document.createElement('tr');
            for (let j = 0; j < visualSize; j++) {
                const cell = document.createElement('td');
                cell.className = 'puzzle-cell';

                const isNumRow = i % 2 === 0;
                const isNumCol = j % 2 === 0;

                // 1. CASO: CELDAS DE NÚMEROS O RESULTADOS
                if (isNumRow && isNumCol) {
                    const r = i / 2;
                    const c = j / 2;
                    const cellData = this.grid[r][c];

                    // Si es la última fila o última columna, es un RESULTADO (fijo)
                    if (r === size - 1 || c === size - 1) {
                        cell.textContent = cellData.value;
                        cell.classList.add('result-cell');
                    } else {
                        // Es un espacio para que el usuario juegue
                        if (cellData.value === null) {
                            cell.textContent = '?';
                            cell.classList.add('empty-slot');
                            cell.addEventListener('dragover', (e) => e.preventDefault());
                            cell.addEventListener('drop', (e) => this.handleDrop(e, r, c));
                        } else {
                            cell.textContent = cellData.value;
                            cell.classList.add('fixed-number');
                        }
                    }
                }
                // 2. CASO: SIGNOS IGUAL (=)
                else if ((isNumRow && j === visualSize - 2) || (isNumCol && i === visualSize - 2)) {
                    cell.textContent = '=';
                    cell.classList.add('operator-cell', 'equal-sign');
                }
                // 3. CASO: OPERADORES (+, -, x)
                else if (isNumRow || isNumCol) {
                    const r = Math.floor(i / 2);
                    const c = Math.floor(j / 2);
                    // Extraer el operador de la lógica de tu grid
                    cell.textContent = isNumRow ? this.grid[r][c].right_op : this.grid[r][c].down_op;
                    cell.classList.add('operator-cell');
                }

                row.appendChild(cell);
            }
            gridElement.appendChild(row);
        }
    }
    renderNumbersPool() {
        const poolElement = document.getElementById('availableNumbers');
        poolElement.innerHTML = '';
        
        this.numbersPool.forEach((num, index) => {
            const numElement = document.createElement('div');
            numElement.className = 'number-token';
            numElement.textContent = num;
            numElement.setAttribute('draggable', true);
            numElement.setAttribute('data-value', num);
            numElement.setAttribute('data-index', index);
            
            numElement.addEventListener('dragstart', (e) => {
                e.dataTransfer.setData('text/plain', num);
                e.target.style.opacity = '0.5';
            });
            
            numElement.addEventListener('dragend', (e) => {
                e.target.style.opacity = '1';
            });
            
            poolElement.appendChild(numElement);
        });
    }
    
    handleDrop(e, row, col) {
        e.preventDefault();
        const value = parseInt(e.dataTransfer.getData('text/plain'));
        
        // Buscar el número en el pool
        const index = this.numbersPool.indexOf(value);
        if (index > -1) {
            // Eliminar del pool
            this.numbersPool.splice(index, 1);
            
            // Colocar en la celda
            const cell = e.target;
            cell.textContent = value;
            cell.classList.remove('empty');
            cell.classList.add('filled');
            cell.setAttribute('data-placed-value', value);
            
            // Actualizar grid
            this.grid[row][col].value = value;
            
            this.renderNumbersPool();
        }
    }
    
    startTimer() {
        if (this.timer) clearInterval(this.timer);
        this.seconds = 0;
        
        this.timer = setInterval(() => {
            this.seconds++;
            const mins = Math.floor(this.seconds / 60);
            const secs = this.seconds % 60;
            document.getElementById('timer').textContent = 
                `${mins.toString().padStart(2, '0')}:${secs.toString().padStart(2, '0')}`;
        }, 1000);
    }
    
    checkSolution() {
        // Verificar si todas las celdas están llenas
        let allFilled = true;
        for (let i = 0; i < this.gridSize; i++) {
            for (let j = 0; j < this.gridSize; j++) {
                if (this.grid[i][j].value === null) {
                    allFilled = false;
                    break;
                }
            }
        }
        
        if (!allFilled) {
            alert(`❓ Faltan números por colocar (${this.numbersPool.length} restantes)`);
            return;
        }
        
        // Validar con el servidor
        fetch('/api/math-puzzle/validate', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                grid: this.grid,
                puzzle_id: this.puzzleId,
                time_spent: this.seconds,
                lives: this.lives,
                level: this.level
            })
        })
        .then(res => res.json())
        .then(data => {
            if (data.valid) {
                this.score += data.score;
                document.getElementById('score').textContent = this.score;
                alert(`🎉 ¡Correcto! +${data.score} puntos`);
                this.newGame(); // Siguiente puzzle
            } else {
                this.lives--;
                document.getElementById('lives').textContent = this.lives;
                
                if (this.lives <= 0) {
                    alert('😵 Game Over! Has perdido todas las vidas');
                    this.score = 0;
                    this.newGame();
                } else {
                    alert(`❌ Incorrecto! Te quedan ${this.lives} vidas`);
                }
            }
        });
    }
    
    getHint() {
        fetch('/api/math-puzzle/hint', {
            method: 'POST',
            headers: { 'Content-Type': 'application/json' },
            body: JSON.stringify({
                level: this.level,
                grid: this.grid,
                puzzle_id: this.puzzleId
            })
        })
        .then(res => res.json())
        .then(data => {
            document.getElementById('hintText').textContent = data.hint;
            document.getElementById('hintModal').style.display = 'block';
        });
    }
    
    resetGame() {
        if (confirm('¿Reiniciar el puzzle actual?')) {
            this.newGame();
        }
    }
    
    updateRanking() {
        fetch(`/api/math-puzzle/ranking?level=${this.level}`)
        .then(res => res.json())
        .then(data => {
            console.log("🏆 Ranking:", data);
            const tbody = document.querySelector('#rankingTable tbody');
            tbody.innerHTML = '';
            
            if (data.length === 0) {
                tbody.innerHTML = '<tr><td colspan="4" style="text-align: center;">No hay puntuaciones aún</td></tr>';
            } else {
                data.forEach((entry, index) => {
                    const row = tbody.insertRow();
                    row.innerHTML = `
                        <td>${index + 1}</td>
                        <td>${entry.username || 'Anónimo'}</td>
                        <td>${entry.score}</td>
                        <td>${entry.time_spent || 0}s</td>
                    `;
                });
            }
            
            document.getElementById('rankingLevel').textContent = this.level;
        });
    }
}

// Iniciar cuando cargue la página
document.addEventListener('DOMContentLoaded', () => {
    console.log("📄 Página cargada, iniciando juego...");
    new MathPuzzleGame();
});