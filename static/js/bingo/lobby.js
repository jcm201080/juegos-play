// =======================
// LOBBY
// =======================

function guardarNombre() {
    const input = document.getElementById("nombreJugador");
    const nombre = input ? input.value.trim() : "Jugador";
    localStorage.setItem("bingo_nombre", nombre);
}

function unirseSala() {
    const codigo = document.getElementById("codigoSala").value.trim().toUpperCase();
    if (!codigo) return;

    guardarNombre();
    window.location.href = `/bingo/classic/${codigo}`;
}

// =======================
// 💬 CHAT GLOBAL LOBBY
// =======================

console.log("🔥 LOBBY CHAT ACTIVADO");

const lobbySocket = io("/bingo-classic");

lobbySocket.on("connect", () => {
    console.log("🟢 Lobby conectado");
    lobbySocket.emit("join_lobby_classic");
});

const lobbyInput = document.getElementById("lobbyChatInput");
const lobbyBtn = document.getElementById("lobbySendBtn");
const lobbyMessages = document.getElementById("lobbyChatMessages");

function enviarMensajeLobby() {
    const mensaje = lobbyInput.value.trim();
    if (!mensaje) return;

    lobbySocket.emit("lobby_chat_message", { message: mensaje });
    lobbyInput.value = "";
}

lobbyBtn?.addEventListener("click", enviarMensajeLobby);

lobbyInput?.addEventListener("keypress", (e) => {
    if (e.key === "Enter") enviarMensajeLobby();
});

lobbySocket.on("lobby_new_message", (data) => {
    const div = document.createElement("div");
    div.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
    lobbyMessages.appendChild(div);
    lobbyMessages.scrollTop = lobbyMessages.scrollHeight;
});

lobbySocket.on("lobby_chat_history", (historial) => {
    lobbyMessages.innerHTML = "";

    historial.forEach((data) => {
        const div = document.createElement("div");
        div.innerHTML = `<strong>${data.username}:</strong> ${data.message}`;
        lobbyMessages.appendChild(div);
    });

    lobbyMessages.scrollTop = lobbyMessages.scrollHeight;
});