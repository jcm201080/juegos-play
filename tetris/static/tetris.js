// tetris/static/tetris.js

class TetrisGame {
    constructor(canvasId, canvasSiguienteId) {
        console.log('🎮 Iniciando Tetris...');
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
        this.velocidadBase = 500;
        
        // Detectar móvil
        this.esMovilReal = /Android|webOS|iPhone|iPad|iPod|BlackBerry|IEMobile|Opera Mini/i.test(navigator.userAgent);
        this.esPantallaPequena = window.innerWidth <= 768;
        this.usarControlesTactiles = this.esMovilReal || this.esPantallaPequena;
        
        console.log('📱 ¿Es móvil?', this.esMovilReal);
        console.log('📏 ¿Pantalla pequeña?', this.esPantallaPequena);
        console.log('🎮 ¿Usar controles táctiles?', this.usarControlesTactiles);
        
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
        
        // Cargar datos
        this.cargarRanking();
        this.cargarEstadisticas();
    }
    
    bindEventos() {
        console.log('🔌 Bindeando eventos...');
        
        // Teclado (siempre disponible)
        document.addEventListener('keydown', (e) => {
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

        // Botón nueva partida
        const btnNueva = document.getElementById('btn-nueva-partida');
        if (btnNueva) {
            btnNueva.addEventListener('click', () => {
                console.log('🆕 Click en Nueva Partida');
                this.nuevaPartida();
            });
        }

        // Eventos táctiles para el canvas
        let touchStartX = 0;
        let touchStartY = 0;
        let touchStartTime = 0;

        this.canvas.addEventListener('touchstart', (e) => {
            e.preventDefault();
            console.log('👆 Touch start en canvas');
            const touch = e.touches[0];
            touchStartX = touch.clientX;
            touchStartY = touch.clientY;
            touchStartTime = Date.now();
        });

        this.canvas.addEventListener('touchend', (e) => {
            e.preventDefault();
            if (!touchStartX) {
                console.log('❌ No hay touch start registrado');
                return;
            }
            
            console.log('👆 Touch end en canvas');
            
            if (!this.partidaActiva || this.gameOver) {
                console.log('❌ Partida no activa o game over');
                touchStartX = 0;
                touchStartY = 0;
                return;
            }

            const touchEnd = e.changedTouches[0];
            const deltaX = touchEnd.clientX - touchStartX;
            const deltaY = touchEnd.clientY - touchStartY;
            const deltaTime = Date.now() - touchStartTime;

            console.log('📍 Delta X:', deltaX, 'Delta Y:', deltaY, 'Tiempo:', deltaTime);

            if (Math.abs(deltaX) > Math.abs(deltaY)) {
                if (Math.abs(deltaX) > 30) {
                    if (deltaX > 0) {
                        console.log('👉 Mover derecha');
                        this.mover('derecha');
                    } else {
                        console.log('👈 Mover izquierda');
                        this.mover('izquierda');
                    }
                }
            } else {
                if (Math.abs(deltaY) > 30) {
                    if (deltaY > 0) {
                        if (deltaTime < 300) {
                            console.log('⬇️⬇️ Caída instantánea');
                            this.caidaInstantanea();
                        } else {
                            console.log('⬇️ Mover abajo');
                            this.mover('abajo');
                        }
                    } else {
                        console.log('🔄 Rotar');
                        this.mover('rotar');
                    }
                }
            }

            touchStartX = 0;
            touchStartY = 0;
        });
    }

    crearControlesMovil() {
        if (!this.usarControlesTactiles) {
            console.log('❌ No se crean controles táctiles');
            return;
        }

        if (document.querySelector('.controles-movil')) {
            console.log('⚠️ Controles ya existen');
            return;
        }

        console.log('➕ Creando controles táctiles...');

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

        // Insertar después del panel central
        const panelCentral = document.querySelector('.panel-central');
        if (panelCentral) {
            panelCentral.parentNode.insertBefore(controlesDiv, panelCentral.nextSibling);
            console.log('✅ Controles insertados');
        }

        // Bind de eventos a los botones
        const bindButton = (id, accion) => {
            const btn = document.getElementById(id);
            if (btn) {
                btn.addEventListener('click', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                    console.log(`🔘 Click en ${id}`);
                    if (this.partidaActiva && !this.gameOver) {
                        accion();
                    } else {
                        console.log('❌ Partida no activa');
                    }
                });
                
                btn.addEventListener('touchstart', (e) => {
                    e.preventDefault();
                    e.stopPropagation();
                });
            }
        };

        bindButton('btn-izquierda', () => this.mover('izquierda'));
        bindButton('btn-derecha', () => this.mover('derecha'));
        bindButton('btn-abajo', () => this.mover('abajo'));
        bindButton('btn-rotar', () => this.mover('rotar'));
        bindButton('btn-instantanea', () => this.caidaInstantanea());
    }
    
    async nuevaPartida() {
        console.log('🆕 Solicitando nueva partida...');
        try {
            const response = await fetch('/tetris/api/nueva-partida', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                }
            });
            
            const data = await response.json();
            console.log('📦 Respuesta:', data);
            
            if (data.success) {
                console.log('✅ Partida creada');
                this.partidaActiva = true;
                this.actualizarEstado(data);
                this.iniciarBucleJuego();
                this.cargarEstadisticas();
                this.cargarRanking();
            } else {
                console.error('❌ Error:', data.error);
            }
        } catch (error) {
            console.error('❌ Error en nuevaPartida:', error);
        }
    }
    
    async mover(direccion) {
        console.log(`🎮 Mover: ${direccion}`);
        if (this.gameOver) {
            console.log('❌ Game over');
            return;
        }
        
        try {
            const response = await fetch('/tetris/api/mover', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ direccion })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.actualizarEstado(data);
                
                if (data.game_over) {
                    console.log('💀 Game over');
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

    // ... (el resto de métodos igual que antes, pero añade console.log en los importantes)
    
    async caidaInstantanea() {
        console.log('⬇️⬇️ Caída instantánea');
        // ... resto igual
    }
    
    actualizarEstado(data) {
        console.log('📊 Actualizando estado');
        // ... resto igual
    }
}

// Inicializar
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Página cargada, inicializando Tetris');
    window.juego = new TetrisGame('canvas-tetris', 'canvas-siguiente');
});