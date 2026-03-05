document.addEventListener("DOMContentLoaded", () => {

    const aiBox = document.getElementById("aiAssistant");
    const aiInput = document.getElementById("aiInput");
    const aiSend = document.getElementById("aiSend");
    const aiMessages = document.getElementById("aiMessages");
    const aiClose = document.getElementById("aiClose");
    const aiToggle = document.getElementById("aiToggle");

    if (!aiBox) return;

    // 👋 Mensaje inicial del asistente
    if (aiMessages) {
        aiMessages.innerHTML = `
            <div class="ai-bot">
                👋 Hola. Puedo ayudarte con las reglas del juego o resolver dudas.
            </div>
        `;
    }

    // Botón cerrar
    if (aiClose) {
        aiClose.onclick = () => {
            aiBox.classList.add("hidden");
        };
    }

    // Botón toggle (abrir / cerrar chat)
    if (aiToggle) {

        aiToggle.onclick = () => {
            aiBox.classList.toggle("hidden");
        };

    }

    // Enviar mensaje
    if (aiSend && aiInput) {

        aiSend.onclick = async () => {

            const mensaje = aiInput.value.trim();
            if (!mensaje) return;

            aiMessages.innerHTML += `
                <div class="ai-user">🧑 ${mensaje}</div>
            `;

            aiInput.value = "";

            try {

                const res = await fetch("/api/ai", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        mensaje: mensaje,
                        pagina: window.location.pathname
                    })
                });

                const data = await res.json();

                aiMessages.innerHTML += `
                    <div class="ai-bot">🤖 ${data.respuesta}</div>
                `;

                aiMessages.scrollTop = aiMessages.scrollHeight;

            } catch (err) {

                console.error("Error IA:", err);

                aiMessages.innerHTML += `
                    <div class="ai-bot">⚠️ No se pudo contactar con la IA</div>
                `;

            }

        };

        // Enviar con ENTER
        aiInput.addEventListener("keypress", function (e) {

            if (e.key === "Enter") {
                e.preventDefault();
                aiSend.click();
            }

        });

    }

});