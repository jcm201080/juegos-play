// static/js/auth.js

const API_BASE = window.location.origin;
const STORAGE_KEY = "jcm_user";

window.JCM_USER = null;
window.JCM_NEXT_URL = null;

// ===============================
// 🌍 FUNCIONES GLOBALES
// ===============================

window.closeLoginModal = function () {
    const authModal = document.getElementById("authModal");
    if (!authModal) return;

    authModal.classList.add("hidden");

    const hint = document.getElementById("loginHint");
    if (hint) hint.classList.add("hidden");
};

window.openLoginModal = function () {
    const authModal = document.getElementById("authModal");
    if (!authModal) return;

    authModal.classList.remove("hidden");

    const hint = document.getElementById("loginHint");
    if (!window.JCM_USER && hint) {
        hint.classList.remove("hidden");
    } else if (hint) {
        hint.classList.add("hidden");
    }
};

document.addEventListener("DOMContentLoaded", () => {

    // ===============================
    // 📌 ELEMENTOS
    // ===============================

    const openAuthBtn = document.getElementById("openAuthBtn");
    const headerUsernameBox = document.getElementById("headerUsernameBox");
    const headerUsernameText = document.getElementById("headerUsernameText");
    const headerLogoutBtn = document.getElementById("headerLogoutBtn");
    const headerHistoryLink = document.getElementById("headerHistoryLink");

    const authModal = document.getElementById("authModal");
    const closeAuthBtn = document.getElementById("closeAuthBtn");

    const loginForm = document.getElementById("loginForm");
    const registerForm = document.getElementById("registerForm");

    const loginMessage = document.getElementById("loginMessage");
    const registerMessage = document.getElementById("registerMessage");

    const authGuest = document.getElementById("auth-guest");
    const authLogged = document.getElementById("auth-logged");

    const currentUsernameSpan = document.getElementById("currentUsername");
    const currentBestScoreSpan = document.getElementById("currentBestScore");
    const currentTotalScoreSpan = document.getElementById("currentTotalScore");

    const logoutBtn = document.getElementById("logoutBtn");
    const goGamesBtn = document.getElementById("goGamesBtn");

    const tabLogin = document.getElementById("tabLogin");
    const tabRegister = document.getElementById("tabRegister");

    const forgotPasswordLink = document.getElementById("forgotPasswordLink");

    // ===============================
    // 🎛 Tabs Login / Register
    // ===============================

    if (tabLogin && tabRegister && loginForm && registerForm) {

        tabLogin.addEventListener("click", () => {
            tabLogin.classList.add("active");
            tabRegister.classList.remove("active");

            loginForm.classList.remove("hidden");
            registerForm.classList.add("hidden");
        });

        tabRegister.addEventListener("click", () => {
            tabRegister.classList.add("active");
            tabLogin.classList.remove("active");

            registerForm.classList.remove("hidden");
            loginForm.classList.add("hidden");
        });
    }

    // ===============================
    // 🎮 Botón ir a juegos
    // ===============================

    if (goGamesBtn) {
        goGamesBtn.addEventListener("click", () => {
            window.closeLoginModal();

            if (window.JCM_NEXT_URL) {
                const target = window.JCM_NEXT_URL;
                window.JCM_NEXT_URL = null;
                window.location.href = target;
            } else {
                window.location.href = "/";
            }
        });
    }

    if (openAuthBtn) openAuthBtn.addEventListener("click", window.openLoginModal);
    if (closeAuthBtn) closeAuthBtn.addEventListener("click", window.closeLoginModal);

    if (authModal) {
        const backdrop = authModal.querySelector(".auth-modal-backdrop");
        if (backdrop) backdrop.addEventListener("click", window.closeLoginModal);
    }

    // ===============================
    // 👤 LOCALSTORAGE
    // ===============================

    const saved = localStorage.getItem(STORAGE_KEY);
    if (saved) {
        try {
            const user = JSON.parse(saved);
            if (user && user.id) window.JCM_USER = user;
        } catch {
            localStorage.removeItem(STORAGE_KEY);
        }
    }

    function setUser(user) {
        window.JCM_USER = user;
        localStorage.setItem(STORAGE_KEY, JSON.stringify(user));
        updateAuthUI();
    }

    function clearUser() {
        window.JCM_USER = null;
        localStorage.removeItem(STORAGE_KEY);
        updateAuthUI();
    }

    // ===============================
    // 🎨 ACTUALIZAR UI
    // ===============================

    function updateAuthUI() {
        const user = window.JCM_USER;

        if (authGuest && authLogged) {
            if (user) {
                authGuest.classList.add("hidden");
                authLogged.classList.remove("hidden");

                if (currentUsernameSpan) currentUsernameSpan.textContent = user.username;
                if (currentBestScoreSpan) currentBestScoreSpan.textContent = user.best_score ?? 0;
                if (currentTotalScoreSpan) currentTotalScoreSpan.textContent = user.total_score ?? 0;

            } else {
                authGuest.classList.remove("hidden");
                authLogged.classList.add("hidden");
            }
        }

        if (openAuthBtn) openAuthBtn.classList.toggle("hidden", !!user);

        if (headerUsernameBox && headerUsernameText) {
            if (user) {
                headerUsernameText.textContent = user.username;
                headerUsernameBox.classList.remove("hidden");
            } else {
                headerUsernameBox.classList.add("hidden");
            }
        }

        if (headerLogoutBtn) headerLogoutBtn.classList.toggle("hidden", !user);
        if (headerHistoryLink) headerHistoryLink.classList.toggle("hidden", !user);

        window.dispatchEvent(new CustomEvent("jcm:user-changed", { detail: { user } }));
    }

    updateAuthUI();

    // ===============================
    // 🔁 SINCRONIZAR CON BACKEND
    // ===============================

    async function syncSessionFromBackend() {
        try {
            const resp = await fetch(`${API_BASE}/api/me`, {
                method: "GET",
                credentials: "include"
            });

            if (!resp.ok) return;

            const data = await resp.json();

            if (data.logged_in && data.user) {
                setUser(data.user);
                if (data.next_url) window.JCM_NEXT_URL = data.next_url;
            } else {
                clearUser();
            }

        } catch (e) {
            console.warn("Error sincronizando sesión:", e);
        }
    }

    syncSessionFromBackend();

    // ===============================
    // 📝 REGISTER
    // ===============================

    if (registerForm) {
        registerForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            registerMessage.textContent = "";
            registerMessage.className = "auth-message";

            const email = document.getElementById("registerEmail").value.trim();
            const username = document.getElementById("registerUsername").value.trim();
            const password = document.getElementById("registerPassword").value.trim();

            if (!email || !username || !password) {
                registerMessage.textContent = "Rellena todos los campos.";
                registerMessage.classList.add("error");
                return;
            }

            try {
                const resp = await fetch(`${API_BASE}/api/register`, {
                    method: "POST",
                    credentials: "include",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, username, password }),
                });

                const data = await resp.json();

                if (!data.success) {
                    registerMessage.textContent = data.error || "Error al registrar.";
                    registerMessage.classList.add("error");
                    return;
                }

                setUser(data.user);
                window.closeLoginModal();

            } catch {
                registerMessage.textContent = "Error de conexión con el servidor.";
                registerMessage.classList.add("error");
            }
        });
    }

    // ===============================
    // 🔐 LOGIN
    // ===============================

    if (loginForm) {
        loginForm.addEventListener("submit", async (e) => {
            e.preventDefault();

            loginMessage.textContent = "";
            loginMessage.className = "auth-message";

            const email = document.getElementById("loginEmail").value.trim();
            const password = document.getElementById("loginPassword").value.trim();

            if (!email || !password) {
                loginMessage.textContent = "Rellena email y contraseña.";
                loginMessage.classList.add("error");
                return;
            }

            try {
                const resp = await fetch(`${API_BASE}/api/login`, {
                    method: "POST",
                    credentials: "include",
                    headers: { "Content-Type": "application/json" },
                    body: JSON.stringify({ email, password }),
                });

                const data = await resp.json();

                if (!data.success) {
                    loginMessage.textContent = data.error || "No se pudo iniciar sesión.";
                    loginMessage.classList.add("error");
                    return;
                }

                setUser(data.user);
                window.closeLoginModal();

                if (window.JCM_NEXT_URL) {
                    const target = window.JCM_NEXT_URL;
                    window.JCM_NEXT_URL = null;
                    window.location.href = target;
                } else {
                    window.location.reload();
                }

            } catch {
                loginMessage.textContent = "Error de conexión con el servidor.";
                loginMessage.classList.add("error");
            }
        });
    }

    // ===============================
    // 🚪 LOGOUT
    // ===============================

    async function doLogout() {
        try {
            await fetch(`${API_BASE}/api/logout`, {
                method: "POST",
                credentials: "include",
            });
        } finally {
            clearUser();
            window.location.reload();
        }
    }

    if (logoutBtn) logoutBtn.addEventListener("click", doLogout);
    if (headerLogoutBtn) headerLogoutBtn.addEventListener("click", doLogout);

    // ===============================
    // 🔑 FORGOT PASSWORD (placeholder)
    // ===============================

    if (forgotPasswordLink) {
        forgotPasswordLink.addEventListener("click", (e) => {
            e.preventDefault();
            alert("Sistema de recuperación próximamente disponible.");
        });
    }

});
