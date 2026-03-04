document.addEventListener("DOMContentLoaded", () => {

    const isBingoPage = window.location.pathname.includes("bingo");

    const aiBox = document.getElementById("aiAssistant");
    const aiInput = document.getElementById("aiInput");
    const aiSend = document.getElementById("aiSend");
    const aiMessages = document.getElementById("aiMessages");
    const aiClose = document.getElementById("aiClose");
    const aiToggle = document.getElementById("aiToggle");

    if (!aiBox) return;

    // Mostrar solo en páginas de bingo
    if (!isBingoPage) {
        aiBox.style.display = "none";
        return;
    }

    // Botón cerrar
    if (aiClose) {
        aiClose.onclick = () => {
            aiBox.style.display = "none";
        };
    }

    // Botón toggle
    if (aiToggle) {

        aiToggle.style.display = "block";

        aiToggle.onclick = () => {

            if (aiBox.style.display === "none") {
                aiBox.style.display = "flex";
            } else {
                aiBox.style.display = "none";
            }

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

                const res = await fetch("/api/bingo-ai", {
                    method: "POST",
                    headers: {
                        "Content-Type": "application/json"
                    },
                    body: JSON.stringify({
                        mensaje: mensaje
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