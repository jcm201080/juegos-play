// tetris/static/tetris.js

class TetrisGame {
    constructor(canvasId, canvasSiguienteId) {
        this.canvas = document.getElementById(canvasId);
        this.ctx = this.canvas.getContext('2d');
        this.canvasSiguiente = document.getElementById(canvasSiguienteId);
        this.ctxSiguiente = this.canvasSiguiente.getContext('2d');
        
        // Tamaño de las celdas
        this.celdaSize = 30;
        this.ancho = 10;
        this.alto = 20;
        
        // Estado del juego - INICIALIZAR VACÍO
        this.tablero = Array(this.alto).fill().map(() => Array(this.ancho).fill(0));
        this.piezaActual = null;
        this.siguientePieza = null;
        this.puntuacion = 0;
        this.nivel = 1;
        this.lineas = 0;
        this.gameOver = false;
        this.partidaActiva = false;  // Nueva bandera para saber si hay partida activa
        
        // Intervalo del juego
        this.intervaloJuego = null;
        this.velocidadBase = 500; // ms
        
        // Detectar si es móvil
        this.esMovil = 'ontouchstart' in window;
        this.esPantallaPequena = window.innerWidth <= 768;
        this.usarControlesTactiles = this.esMovil || this.esPantallaPequena;
        // Colores de las piezas
        this.colores = {
            'I': '#00ffff',  // Cian
            'O': '#ffff00',  // Amarillo
            'T': '#aa00ff',  // Morado
            'S': '#00ff00',  // Verde
            'Z': '#ff0000',  // Rojo
            'L': '#ffaa00',  // Naranja
            'J': '#0000ff',  // Azul
            '0': '#111'      // Vacío
        };
        
        // Bind de eventos
        this.bindEventos();
        this.crearControlesMovil();
        
        // NO iniciar partida automáticamente - eliminado this.nuevaPartida()
        
        // Dibujar tablero vacío
        this.dibujar();
        
        // Cargar ranking al inicio
        this.cargarRanking();
        this.cargarEstadisticas();

        // 🟢 AQUÍ VA EL EVENT LISTENER DE RESIZE 
        window.addEventListener('resize', () => {
            this.esPantallaPequena = window.innerWidth <= 768;
            this.usarControlesTactiles = this.esMovil || this.esPantallaPequena;
            
            // Si hay controles, mostrarlos u ocultarlos según el tamaño
            const controles = document.querySelector('.controles-movil');
            if (controles) {
                if (this.usarControlesTactiles) {
                    controles.style.display = 'block';
                } else {
                    controles.style.display = 'none';
                }
            } else if (this.usarControlesTactiles) {
                // Si no existen pero deberían, crearlos
                this.crearControlesMovil();
            }
        });
    }
    
    bindEventos() {
        document.addEventListener('keydown', (e) => {
            // Solo permitir movimientos si hay partida activa y no está terminada
            if (!this.partidaActiva || this.gameOver) return;
            
            switch(e.key) {
                case 'ArrowLeft':
                    e.preventDefault();
                    this.mover('izquierda');
                    break;
                case 'ArrowRight':
                    e.preventDefault();
                    this.mover('derecha');
                    break;
                case 'ArrowDown':
                    e.preventDefault();
                    this.mover('abajo');
                    break;
                case 'ArrowUp':
                    e.preventDefault();
                    this.mover('rotar');
                    break;
                case ' ':
                    e.preventDefault();
                    this.caidaInstantanea();
                    break;
            }
        });

        if (this.esMovil) {
            let touchStartX = 0;
            let touchStartY = 0;
            let touchStartTime = 0;

            this.canvas.addEventListener('touchstart', (e) => {
                const touch = e.touches[0];
                touchStartX = touch.clientX;
                touchStartY = touch.clientY;
                touchStartTime = Date.now();
            });

            this.canvas.addEventListener('touchend', (e) => {
                if (!this.partidaActiva || this.gameOver || !touchStartX) return;

                const touchEnd = e.changedTouches[0];
                const deltaX = touchEnd.clientX - touchStartX;
                const deltaY = touchEnd.clientY - touchStartY;
                const deltaTime = Date.now() - touchStartTime;

                if (Math.abs(deltaX) > Math.abs(deltaY)) {
                    if (Math.abs(deltaX) > 30) {
                        if (deltaX > 0) {
                            this.mover('derecha');
                        } else {
                            this.mover('izquierda');
                        }
                    }
                } else {
                    if (Math.abs(deltaY) > 30) {
                        if (deltaY > 0) {
                            if (deltaTime < 300) {
                                this.caidaInstantanea();
                            } else {
                                this.mover('abajo');
                            }
                        } else {
                            this.mover('rotar');
                        }
                    }
                }

                touchStartX = 0;
                touchStartY = 0;
            });
        }
    }

   // En tetris.js, actualizar crearControlesMovil()

    crearControlesMovil() {
        // Solo crear si es necesario (móvil real o pantalla pequeña)
        
        if (!this.usarControlesTactiles) return;

        // Verificar si ya existen
        if (document.querySelector('.controles-movil')) return;

        console.log('📱 Creando controles táctiles');

        const controlesDiv = document.createElement('div');
        controlesDiv.className = 'controles-movil';
        controlesDiv.innerHTML = `
            <div class="control-fila">
                <button class="btn-control" id="btn-izquierda">←</button>
                <button class="btn-control" id="btn-abajo">↓</button>
                <button class="btn-control" id="btn-derecha">→</button>
            </div>
            <div class="control-fila">
                <button class="btn-control btn-rotar" id="btn-rotar">↻ Rotar</button>
                <button class="btn-control btn-caida" id="btn-instantanea">⬇️⬇️ Caída</button>
            </div>
        `;
        // mover la pieza siguiente debajo del tablero en móvil
        if (this.usarControlesTactiles) {
            const panelCentral = document.querySelector('.panel-central');
            if (panelCentral && this.canvasSiguiente) {
                panelCentral.appendChild(this.canvasSiguiente);
            }
        }

        // Insertar DESPUÉS del panel central (tablero)
        const panelCentral = document.querySelector('.panel-central');
        if (panelCentral) {
            panelCentral.parentNode.insertBefore(controlesDiv, panelCentral.nextSibling);
            console.log('✅ Controles insertados después del tablero');
        }

        // Bind de eventos
        const bindButton = (id, accion) => {
            const btn = document.getElementById(id);
            if (!btn) return;

            // móvil
            btn.addEventListener('touchstart', (e) => {
                e.preventDefault();
                accion();
            });

            // ordenador
            btn.addEventListener('click', (e) => {
                e.preventDefault();
                accion();
            });
        };

        bindButton('btn-izquierda', () => this.mover('izquierda'));
        bindButton('btn-derecha', () => this.mover('derecha'));
        bindButton('btn-abajo', () => this.mover('abajo'));
        bindButton('btn-rotar', () => this.mover('rotar'));
        bindButton('btn-instantanea', () => this.caidaInstantanea());
    }

    async cargarRanking() {
        try {
            const response = await fetch('/tetris/api/ranking');
            const data = await response.json();
            
            if (data.success && data.ranking) {
                this.mostrarRanking(data.ranking);
            }
        } catch (error) {
            console.error('Error al cargar ranking:', error);
        }
    }

    mostrarRanking(ranking) {
        let rankingDiv = document.querySelector('.ranking-tetris');
        if (!rankingDiv) {
            rankingDiv = document.createElement('div');
            rankingDiv.className = 'ranking-tetris';
            rankingDiv.innerHTML = '<h4>🏆 Ranking Tetris</h4>';
            document.querySelector('.panel-izquierdo')?.appendChild(rankingDiv);
        }

        let html = '<h4>🏆 Ranking Tetris</h4><ol>';
        ranking.forEach((jugador) => {
            html += `<li>
                <strong>${jugador.username}</strong> - ${jugador.puntuacion_maxima} pts
                <small>(Nivel ${jugador.nivel_maximo})</small>
            </li>`;
        });
        html += '</ol>';

        rankingDiv.innerHTML = html;
    }

    async cargarEstadisticas() {
        try {
            const response = await fetch('/tetris/api/estadisticas');
            const data = await response.json();
            
            if (data.success && data.estadisticas) {
                this.mostrarEstadisticas(data.estadisticas, data.ultimas_partidas);
            }
        } catch (error) {
            console.error('Error al cargar estadísticas:', error);
        }
    }

    mostrarEstadisticas(estadisticas, ultimasPartidas) {
        let statsDiv = document.querySelector('.estadisticas-tetris');
        if (!statsDiv) {
            statsDiv = document.createElement('div');
            statsDiv.className = 'estadisticas-tetris';
            statsDiv.innerHTML = '<h4>📊 Tus Estadísticas</h4>';
            document.querySelector('.panel-izquierdo')?.appendChild(statsDiv);
        }

        let html = `
            <h4>📊 Tus Estadísticas</h4>
            <div class="stats-grid">
                <p>🏆 Máxima: ${estadisticas.puntuacion_maxima}</p>
                <p>🎮 Partidas: ${estadisticas.partidas_jugadas}</p>
                <p>📈 Total pts: ${estadisticas.puntuacion_total}</p>
                <p>🧱 Líneas: ${estadisticas.lineas_totales}</p>
                <p>🎯 Tetris: ${estadisticas.tetris_conseguidos}</p>
                <p>⭐ Nivel máx: ${estadisticas.nivel_maximo}</p>
            </div>
        `;

        if (ultimasPartidas?.length > 0) {
            html += '<h5>Últimas partidas:</h5><ul>';
            ultimasPartidas.slice(0, 3).forEach(p => {
                const fecha = new Date(p.created_at).toLocaleDateString();
                html += `<li>${fecha}: ${p.puntuacion} pts (${p.lineas} líneas)</li>`;
            });
            html += '</ul>';
        }

        statsDiv.innerHTML = html;
    }
    
    async nuevaPartida() {
        try {
            const response = await fetch('/tetris/api/nueva-partida', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.partidaActiva = true;
                this.actualizarEstado(data);
                this.iniciarBucleJuego();
                this.cargarEstadisticas();
                this.cargarRanking();
            }
        } catch (error) {
            console.error('Error:', error);
        }
    }
    
    actualizarEstado(data) {
        console.log('📊 actualizarEstado llamado', data);  // 🟢 AÑADIR
        
        if (data.tablero) {
            console.log('🎮 Tablero recibido:', data.tablero);  // 🟢 AÑADIR
            
            this.tablero = data.tablero.tablero;
            this.piezaActual = data.tablero.pieza_actual;
            this.siguientePieza = data.tablero.siguiente_pieza;
            this.puntuacion = data.tablero.puntuacion || 0;
            this.nivel = data.tablero.nivel || 1;
            this.lineas = data.tablero.lineas_completadas || 0;
            this.gameOver = data.tablero.game_over || false;
            
            console.log('🔄 Estado actualizado:', {  // 🟢 AÑADIR
                puntuacion: this.puntuacion,
                nivel: this.nivel,
                lineas: this.lineas,
                gameOver: this.gameOver
            });
            
            // Actualizar UI
            document.getElementById('puntuacion').textContent = this.puntuacion;
            document.getElementById('nivel').textContent = this.nivel;
            document.getElementById('lineas').textContent = this.lineas;
            
            console.log('🎨 Llamando a dibujar()');  // 🟢 AÑADIR
            this.dibujar();
        } else {
            console.log('❌ No hay tablero en data');  // 🟢 AÑADIR
        }
    }
    
    async mover(direccion) {
        if (this.gameOver) return;
        
        try {
            const response = await fetch('/tetris/api/mover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ direccion })
            });
            
            const data = await response.json();
            console.log('📦 Respuesta mover:', data);  // 🟢 AÑADIR
            
            if (data.success) {
                console.log('✅ Movimiento exitoso, actualizando...');  // 🟢 AÑADIR
                this.actualizarEstado(data);
                
                if (data.game_over) {
                    console.log('💀 GAME OVER');  // 🟢 AÑADIR
                    this.partidaActiva = false;
                    this.detenerBucleJuego();
                    this.mostrarGameOver();
                    this.cargarRanking();
                    this.cargarEstadisticas();
                }
            }
        } catch (error) {
            console.error('❌ Error al mover:', error);
        }
    }
    
    async caidaInstantanea() {
        if (this.gameOver) return;

        const piezaInicial = this.piezaActual?.tipo;

        while (!this.gameOver) {
            const response = await fetch('/tetris/api/mover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ direccion: 'abajo' })
            });

            const data = await response.json();
            this.actualizarEstado(data);

            const piezaNueva = data.tablero?.pieza_actual?.tipo;

            // si cambia la pieza, parar
            if (piezaNueva !== piezaInicial) break;
        }
    }
    
    iniciarBucleJuego() {
        if (this.intervaloJuego) clearInterval(this.intervaloJuego);
        
        this.intervaloJuego = setInterval(() => {
            if (!this.gameOver) this.mover('abajo');
        }, this.velocidadBase / this.nivel);
    }
    
    detenerBucleJuego() {
        if (this.intervaloJuego) {
            clearInterval(this.intervaloJuego);
            this.intervaloJuego = null;
        }
    }
    
    dibujar() {
        console.log('🎨 Dibujando tablero...');  // 🟢 AÑADIR
        
        // Limpiar canvases
        this.ctx.clearRect(0, 0, this.canvas.width, this.canvas.height);
        this.ctxSiguiente.clearRect(0, 0, this.canvasSiguiente.width, this.canvasSiguiente.height);
        
        // Dibujar tablero (vacío o con piezas)
        for (let y = 0; y < this.alto; y++) {
            for (let x = 0; x < this.ancho; x++) {
                const valor = this.tablero[y]?.[x];
                this.dibujarCelda(x, y, valor || '0');
            }
        }
        // 👻 Dibujar pieza fantasma
        const yFantasma = this.obtenerPosicionFantasma();

        if (yFantasma !== null && this.piezaActual) {

            const pieza = this.piezaActual;

            this.ctx.globalAlpha = 0.05;

            for (let i = 0; i < pieza.forma.length; i++) {
                for (let j = 0; j < pieza.forma[i].length; j++) {

                    if (!pieza.forma[i][j]) continue;

                    const x = pieza.x + j;
                    const y = yFantasma + i;

                    if (y >= 0) {
                        this.dibujarCelda(x, y, pieza.tipo);
                    }
                }
            }

            this.ctx.globalAlpha = 1;
        }
        
        // Dibujar pieza actual solo si hay partida activa
        if (this.partidaActiva && this.piezaActual && !this.gameOver) {
            console.log('🎨 Dibujando pieza actual:', this.piezaActual.tipo);  // 🟢 AÑADIR
            
            const pieza = this.piezaActual;
            if (pieza.forma) {
                for (let i = 0; i < pieza.forma.length; i++) {
                    for (let j = 0; j < pieza.forma[i].length; j++) {
                        if (pieza.forma[i][j]) {
                            const x = pieza.x + j;
                            const y = pieza.y + i;
                            if (y >= 0) {
                                this.dibujarCelda(x, y, pieza.tipo);
                            }
                        }
                    }
                }
            }
        }

        
        
        // Dibujar siguiente pieza
        this.dibujarSiguientePieza();
        
        // Dibujar cuadrícula
        this.dibujarCuadricula();
        
        // Si no hay partida activa, mostrar mensaje
        if (!this.partidaActiva) {
            this.ctx.fillStyle = 'rgba(255,255,255,0.8)';
            this.ctx.font = 'bold 20px Arial';
            this.ctx.textAlign = 'center';
        }
        
        console.log('✅ Dibujo completado');  // 🟢 AÑADIR
    }
    dibujarCelda(x, y, tipo) {
        const color = this.colores[tipo] || this.colores['0'];
        
        this.ctx.fillStyle = color;
        this.ctx.fillRect(
            x * this.celdaSize,
            y * this.celdaSize,
            this.celdaSize - 1,
            this.celdaSize - 1
        );
        
        if (tipo !== '0') {
            this.ctx.strokeStyle = 'rgba(255,255,255,0.3)';
            this.ctx.strokeRect(
                x * this.celdaSize,
                y * this.celdaSize,
                this.celdaSize - 1,
                this.celdaSize - 1
            );
        }
    }
    obtenerPosicionFantasma() {

        if (!this.piezaActual) return null;

        const pieza = JSON.parse(JSON.stringify(this.piezaActual));

        let yFantasma = pieza.y;

        while (true) {
            let colision = false;

            for (let i = 0; i < pieza.forma.length; i++) {
                for (let j = 0; j < pieza.forma[i].length; j++) {

                    if (!pieza.forma[i][j]) continue;

                    const x = pieza.x + j;
                    const y = yFantasma + i + 1;

                    if (
                        y >= this.alto ||
                        (y >= 0 && this.tablero[y]?.[x])
                    ) {
                        colision = true;
                        break;
                    }
                }

                if (colision) break;
            }

            if (colision) break;

            yFantasma++;
        }

        return yFantasma;
    }

    dibujarSiguientePieza() {
        if (!this.siguientePieza) return;
        
        const pieza = this.siguientePieza;
        const tamanoCelda = 30;
        const offsetX = (this.canvasSiguiente.width - pieza.forma[0].length * tamanoCelda) / 2;
        const offsetY = (this.canvasSiguiente.height - pieza.forma.length * tamanoCelda) / 2;
        
        // Limpiar canvas de siguiente pieza
        this.ctxSiguiente.clearRect(0, 0, this.canvasSiguiente.width, this.canvasSiguiente.height);
        
        // Dibujar fondo negro
        this.ctxSiguiente.fillStyle = '#111';
        this.ctxSiguiente.fillRect(0, 0, this.canvasSiguiente.width, this.canvasSiguiente.height);
        
        // Dibujar la pieza
        for (let i = 0; i < pieza.forma.length; i++) {
            for (let j = 0; j < pieza.forma[i].length; j++) {
                if (pieza.forma[i][j]) {
                    this.ctxSiguiente.fillStyle = this.colores[pieza.tipo];
                    this.ctxSiguiente.fillRect(
                        offsetX + j * tamanoCelda,
                        offsetY + i * tamanoCelda,
                        tamanoCelda - 2,
                        tamanoCelda - 2
                    );
                    
                    // Borde
                    this.ctxSiguiente.strokeStyle = 'rgba(255,255,255,0.3)';
                    this.ctxSiguiente.strokeRect(
                        offsetX + j * tamanoCelda,
                        offsetY + i * tamanoCelda,
                        tamanoCelda - 2,
                        tamanoCelda - 2
                    );
                }
            }
        }
    }
    
    dibujarCuadricula() {
        this.ctx.strokeStyle = 'rgba(255,255,255,0.1)';
        this.ctx.lineWidth = 0.5;
        
        for (let x = 0; x <= this.ancho; x++) {
            this.ctx.beginPath();
            this.ctx.moveTo(x * this.celdaSize, 0);
            this.ctx.lineTo(x * this.celdaSize, this.canvas.height);
            this.ctx.stroke();
        }
        
        for (let y = 0; y <= this.alto; y++) {
            this.ctx.beginPath();
            this.ctx.moveTo(0, y * this.celdaSize);
            this.ctx.lineTo(this.canvas.width, y * this.celdaSize);
            this.ctx.stroke();
        }
    }
    
    mostrarGameOver() {
        this.ctx.fillStyle = 'rgba(0,0,0,0.7)';
        this.ctx.fillRect(0, 0, this.canvas.width, this.canvas.height);
        
        this.ctx.fillStyle = 'white';
        this.ctx.font = 'bold 30px Arial';
        this.ctx.textAlign = 'center';
        this.ctx.textBaseline = 'middle';
        this.ctx.fillText('GAME OVER', this.canvas.width/2, this.canvas.height/2);
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    window.juego = new TetrisGame('canvas-tetris', 'canvas-siguiente');
});