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
        
        // Estado del juego
        this.tablero = Array(this.alto).fill().map(() => Array(this.ancho).fill(0));
        this.piezaActual = null;
        this.siguientePieza = null;
        this.puntuacion = 0;
        this.nivel = 1;
        this.lineas = 0;
        this.gameOver = false;
        this.partidaActiva = false;
        
        // Intervalo del juego
        this.intervaloJuego = null;
        this.velocidadBase = 500; // ms
        
        // Detectar si es móvil REAL o pantalla pequeña
        this.esMovilReal = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        this.esPantallaPequena = window.innerWidth <= 768;
        this.usarControlesTactiles = this.esMovilReal || this.esPantallaPequena;
        
        // Colores de las piezas
        this.colores = {
            'I': '#00ffff',
            'O': '#ffff00',
            'T': '#aa00ff',
            'S': '#00ff00',
            'Z': '#ff0000',
            'L': '#ffaa00',
            'J': '#0000ff',
            '0': '#111'
        };
        
        // Bind de eventos
        this.bindEventos();
        this.crearControlesMovil();
        
        // Dibujar tablero vacío
        this.dibujar();
        
        // Cargar ranking al inicio
        this.cargarRanking();
        this.cargarEstadisticas();

        // Escuchar cambios de tamaño de pantalla
        window.addEventListener('resize', () => {
            this.esPantallaPequena = window.innerWidth <= 768;
            this.usarControlesTactiles = this.esMovilReal || this.esPantallaPequena;
            this.actualizarVisibilidadControles();
        });
    }
    
    actualizarVisibilidadControles() {
        const controles = document.querySelector('.controles-movil');
        if (controles) {
            if (this.usarControlesTactiles) {
                controles.style.display = 'block';
            } else {
                controles.style.display = 'none';
            }
        }
    }
    
    bindEventos() {
        document.addEventListener('keydown', (e) => {
            // Las teclas SIEMPRE funcionan si hay partida activa
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

        // Eventos táctiles (siempre disponibles, pero solo se activan en móvil)
        let touchStartX = 0;
        let touchStartY = 0;
        let touchStartTime = 0;

        this.canvas.addEventListener('touchstart', (e) => {
            if (!this.partidaActiva || this.gameOver) return;
            e.preventDefault();
            const touch = e.touches[0];
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
            touchStartTime = Date.now();
        });

        this.canvas.addEventListener('touchend', (e) => {
            if (!this.partidaActiva || this.gameOver || !touchStartX) return;
            e.preventDefault();

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

    crearControlesMovil() {
        // Solo crear controles si es necesario
        if (!this.usarControlesTactiles) return;

        // Verificar si ya existen
        if (document.querySelector('.controles-movil')) return;

        const controlesDiv = document.createElement('div');
        controlesDiv.className = 'controles-movil';
        controlesDiv.innerHTML = `
            <div class="control-fila">
                <button class="btn-control" id="btn-izquierda">←</button>
                <button class="btn-control" id="btn-abajo">↓</button>
                <button class="btn-control" id="btn-derecha">→</button>
            </div>
            <div class="control-fila">
                <button class="btn-control" id="btn-rotar">↻ Rotar</button>
                <button class="btn-control" id="btn-instantanea">⬇️⬇️ Caída</button>
            </div>
        `;

        // Insertar DESPUÉS del panel central
        const panelCentral = document.querySelector('.panel-central');
        if (panelCentral) {
            panelCentral.parentNode.insertBefore(controlesDiv, panelCentral.nextSibling);
        }

        // Bind de eventos
        document.getElementById('btn-izquierda')?.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.partidaActiva && !this.gameOver) this.mover('izquierda');
        });
        
        document.getElementById('btn-derecha')?.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.partidaActiva && !this.gameOver) this.mover('derecha');
        });
        
        document.getElementById('btn-abajo')?.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.partidaActiva && !this.gameOver) this.mover('abajo');
        });
        
        document.getElementById('btn-rotar')?.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.partidaActiva && !this.gameOver) this.mover('rotar');
        });
        
        document.getElementById('btn-instantanea')?.addEventListener('click', (e) => {
            e.preventDefault();
            if (this.partidaActiva && !this.gameOver) this.caidaInstantanea();
        });
    }

    // ... (el resto de métodos igual: cargarRanking, mostrarRanking, cargarEstadisticas, 
    // mostrarEstadisticas, nuevaPartida, actualizarEstado, mover, caidaInstantanea,
    // iniciarBucleJuego, detenerBucleJuego, dibujar, dibujarCelda, 
    // dibujarSiguientePieza, dibujarCuadricula, mostrarGameOver)
    
    // [AQUÍ VA EL RESTO DE MÉTODOS IGUAL QUE ANTES]
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    window.juego = new TetrisGame('canvas-tetris', 'canvas-siguiente');
});