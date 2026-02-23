/* global io */

console.log("🌐 online_lobby.js cargado");

const socket = io();

// Elementos UI
const startBtn = document.getElementById("startOnlineBtn");
const playersList = document.getElementById("playersList");
const statusBox = document.getElementById("online-status");
const numPlayersSelect = document.getElementById("numPlayers");
const numCartonesSelect = document.getElementById("numCartones");
const startNowBtn = document.getElementById("startNowBtn");
const countdownSelect = document.getElementById("countdownTime");

// =======================
// 👑 Control botón admin
// =======================
if (startNowBtn) {
    if (window.BINGO_ROLE !== "admin") {
        startNowBtn.classList.add("hidden");
    }
}

// =======================
// 🚀 Iniciar manual
// =======================
if (startNowBtn) {
    startNowBtn.addEventListener("click", () => {
        const maxPlayers = parseInt(numPlayersSelect.value, 10);

        startNowBtn.disabled = true;
        startNowBtn.textContent = "Iniciando...";

        socket.emit("start_online_now", {
            max_players: maxPlayers
        });
    });
}
// =======================
// Click: Buscar partida
// =======================
if (startBtn) {
    startBtn.addEventListener("click", () => {
        const maxPlayers = parseInt(numPlayersSelect.value, 10);
        const numCartones = parseInt(numCartonesSelect.value, 10);

        startBtn.disabled = true;
        startBtn.textContent = "⏳ Buscando jugadores...";

        socket.emit("join_online_lobby", {
            nombre: window.BINGO_USER || "Invitado",
            max_players: maxPlayers,
            cartones: numCartones,
            countdown: countdownSelect ? parseInt(countdownSelect.value, 10) : null,
        });
    });
}



// =======================
//Ocultar botón "Iniciar ahora" si el usuario no es el primero en la lista
socket.on("online_lobby_update", (data) => {
    renderPlayers(data.players || []);
    renderStatus(data.players?.length || 0, data.max_players, data.countdown);


    // 👑 Mostrar botón solo si es admin y hay mínimo 2 jugadores
    if (startNowBtn && window.BINGO_ROLE === "admin") {
        if ((data.players?.length || 0) >= 2) {
            startNowBtn.classList.remove("hidden");
        } else {
            startNowBtn.classList.add("hidden");
        }
    }
});

// =======================
// Render jugadores
// =======================
function renderPlayers(players) {
    if (!playersList) return;

    playersList.innerHTML = "";

    players.forEach((p) => {
        const li = document.createElement("li");

        // Si viene como string (compatibilidad)
        if (typeof p === "string") {
            li.textContent = p;
        } 
        // Si viene como objeto nuevo
        else {
            li.innerHTML = `
                <span>${p.nombre}</span>
                <span class="mini-cartones">🎟️ x${p.cartones ?? 1}</span>
            `;
        }

        playersList.appendChild(li);
    });
}

// =======================
// ⏳ Render estado del lobby
// (jugadores + countdown)
// =======================
function renderStatus(actuales, max, countdown) {
    if (!statusBox) return;

    const total = max > 0 ? max : "∞";

    statusBox.innerHTML = `
        <p>Esperando jugadores…</p>
        <p><strong>${actuales} / ${total}</strong></p>
        <p class="countdown">⏳ ${countdown ?? 30}s</p>
    `;
}

// =======================
// 🚀 Redirección a la sala
// =======================
socket.on("redirect_to_game", (data) => {
    if (!data?.url) return;

    statusBox.innerHTML = `
        <p>🎱 Sala lista</p>
        <p>Entrando a la partida…</p>
    `;

    setTimeout(() => {
        window.location.href = data.url;
    }, 1000);
});
