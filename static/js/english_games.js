// static/js/english_games.js
document.addEventListener("DOMContentLoaded", () => {
    // === Usuario ===
    const API_BASE = window.location.origin;
    let currentUser = null;

    const userGuestDiv = document.getElementById("gameUserGuest");
    const userLoggedDiv = document.getElementById("gameUserLogged");
    const spanUserName = document.getElementById("currentUserName");
    const spanBestScoreGlobal = document.getElementById("currentUserBestScore");
    const spanTotalScore = document.getElementById("currentUserTotalScore");
    const spanBestScoreLevel = document.getElementById("currentUserLevelBestScore");
    const levelText = document.getElementById("eg-current-level");

    // === Estado del juego ===
    let errors = 0;
    const MAX_ERRORS = 5;
    let score = 0;
    let currentLevel = 1;
    let time = 0;
    let timerId = null;
    let remainingPairs = 0;

    // === Colores base (15) ===
    const BASE_COLORS = [
        { id: "red", word: "red", color: "#e74c3c" },
        { id: "blue", word: "blue", color: "#3498db" },
        { id: "yellow", word: "yellow", color: "#f1c40f" },
        { id: "green", word: "green", color: "#2ecc71" },
        { id: "black", word: "black", color: "#000000" },
        { id: "white", word: "white", color: "#ecf0f1" },
        { id: "orange", word: "orange", color: "#e67e22" },
        { id: "purple", word: "purple", color: "#9b59b6" },
        { id: "pink", word: "pink", color: "#ff6baf" },
        { id: "brown", word: "brown", color: "#8e5b3c" },
        { id: "grey", word: "grey", color: "#7f8c8d" },
        { id: "beige", word: "beige", color: "#f5deb3" },
        { id: "lightblue", word: "light blue", color: "#85c1e9" },
        { id: "darkgreen", word: "dark green", color: "#145a32" },
        { id: "gold", word: "gold", color: "#ffd700" },
    ];

    const WORD_SETS = {

    animals: [
    {word:"dog",emoji:"🐶"},
    {word:"cat",emoji:"🐱"},
    {word:"cow",emoji:"🐄"},
    {word:"horse",emoji:"🐎"},
    {word:"sheep",emoji:"🐑"},
    {word:"pig",emoji:"🐖"},
    {word:"lion",emoji:"🦁"},
    {word:"tiger",emoji:"🐯"},
    {word:"elephant",emoji:"🐘"},
    {word:"monkey",emoji:"🐒"}
    ],

    food: [
    {word:"apple",emoji:"🍎"},
    {word:"banana",emoji:"🍌"},
    {word:"pizza",emoji:"🍕"},
    {word:"burger",emoji:"🍔"},
    {word:"bread",emoji:"🍞"},
    {word:"cheese",emoji:"🧀"},
    {word:"egg",emoji:"🥚"},
    {word:"carrot",emoji:"🥕"},
    {word:"grapes",emoji:"🍇"},
    {word:"watermelon",emoji:"🍉"}
    ],

    vehicles: [
    {word:"car",emoji:"🚗"},
    {word:"bus",emoji:"🚌"},
    {word:"bike",emoji:"🚲"},
    {word:"train",emoji:"🚆"},
    {word:"plane",emoji:"✈️"},
    {word:"boat",emoji:"🚤"},
    {word:"truck",emoji:"🚚"}
    ],

    clothes: [
    {word:"shirt",emoji:"👕"},
    {word:"pants",emoji:"👖"},
    {word:"dress",emoji:"👗"},
    {word:"shoe",emoji:"👟"},
    {word:"hat",emoji:"🧢"}
    ],

    objects: [
    {word:"phone",emoji:"📱"},
    {word:"computer",emoji:"💻"},
    {word:"book",emoji:"📚"},
    {word:"clock",emoji:"⏰"},
    {word:"camera",emoji:"📷"},
    {word:"key",emoji:"🔑"}
    ]

    };

    // === Configuración de niveles ===
    const COLOR_LEVELS = {
        1: {
            type: "simple", // palabra ↔ color
            description: "Nivel 1: Arrastra la palabra en inglés hasta el color correcto.",
            items: BASE_COLORS.slice(0, 6), // 6 colores básicos
        },
        2: {
            type: "simple",
            description: "Nivel 2: Más colores. ¡Recuerda bien sus nombres en inglés!",
            items: BASE_COLORS, // los 15 colores
        },
        3: {
            type: "sentence_image", // frase ↔ imagen
            description: "Nivel 3: Une la frase con la imagen del color correcto.",
            items: [
                {
                    id: "cow_black",
                    sentence: "This cow is black.",
                    img: "/static/img/english/cow_black.jpeg",
                    alt: "Black cow",
                },
                {
                    id: "sheep_white",
                    sentence: "This sheep is white.",
                    img: "/static/img/english/sheep_white.jpeg",
                    alt: "White sheep",
                },
                {
                    id: "dog_brown",
                    sentence: "This dog is brown.",
                    img: "/static/img/english/dog_brown.jpeg",
                    alt: "Brown dog",
                },
                {
                    id: "cat_grey",
                    sentence: "This cat is grey.",
                    img: "/static/img/english/cat_grey.jpeg",
                    alt: "Grey cat",
                },
                {
                    id: "car_red",
                    sentence: "This car is red.",
                    img: "/static/img/english/car_red.jpeg",
                    alt: "Red car",
                },
                {
                    id: "car_blue",
                    sentence: "This car is blue.",
                    img: "/static/img/english/car_blue.jpeg",
                    alt: "Blue car",
                },
            ],
        },
        4: {
            type: "sentence_image",
            description: "Nivel 4: Frases con dos colores. Fíjate bien en la imagen.",
            items: [
                {
                    id: "cow_red_black",
                    sentence: "This cow is red and black.",
                    img: "/static/img/english/cow_red_black.jpeg",
                    alt: "Red and black cow",
                },
                {
                    id: "sheep_white_black",
                    sentence: "This sheep is white and black.",
                    img: "/static/img/english/sheep_white_black.jpeg",
                    alt: "White and black sheep",
                },
                {
                    id: "dog_brown_white",
                    sentence: "This dog is brown and white.",
                    img: "/static/img/english/dog_brown_white.jpeg",
                    alt: "Brown and white dog",
                },
                {
                    id: "cat_grey_white",
                    sentence: "This cat is grey and white.",
                    img: "/static/img/english/cat_grey_white.jpeg",
                    alt: "Grey and white cat",
                },
                {
                    id: "car_blue_yellow",
                    sentence: "This car is blue and yellow.",
                    img: "/static/img/english/car_blue_yellow.jpeg",
                    alt: "Blue and yellow car",
                },
                {
                    id: "car_orange_green",
                    sentence: "This car is orange and green.",
                    img: "/static/img/english/car_orange_green.jpeg",
                    alt: "Orange and green car",
                },
            ],
        },
        5: {
            type: "composite", // frases ↔ cuadro con 3 colores
            description: "Nivel 5: Une la frase con el cuadro que contiene esos tres colores.",
            baseColors: BASE_COLORS,
            count: 5,
        },
    };

    // === Referencias al DOM ===
    const errorsSpan = document.getElementById("eg-errors");
    const scoreSpan = document.getElementById("eg-score");
    const levelSpan = document.getElementById("eg-level");
    const timeSpan = document.getElementById("eg-time");

    const descriptionP = document.getElementById("eg-description");
    const targetsTitle = document.getElementById("eg-targets-title");

    const wordsContainer = document.getElementById("eg-words");
    const targetsContainer = document.getElementById("eg-targets");

    const messageP = document.getElementById("eg-message");
    const startBtn = document.getElementById("eg-start-btn");

    // Ranking
    const rankingBody = document.getElementById("eg-ranking-body");

    // === Sonidos ===
    const soundCorrect = new Audio("/static/sounds/correct.wav");
    const soundWrong = new Audio("/static/sounds/wrong.wav");
    const soundWin = new Audio("/static/sounds/end.wav");
    const soundLose = new Audio("/static/sounds/lose.wav"); // opcional

    const AI_LEVEL_TYPES = [
        "colors",
        "numbers",
        "objects",
        "color_objects"
    ];

    function getAILevelType(level){

    if(level < 8) return "colors";

    if(level < 12) return "numbers";

    if(level < 20){
    const types=["colors","numbers","animals"];
    return types[Math.floor(Math.random()*types.length)];
    }

    if(level < 40){
    const types=["animals","food","vehicles","colors"];
    return types[Math.floor(Math.random()*types.length)];
    }

    const types=[
    "colors",
    "numbers",
    "animals",
    "food",
    "vehicles",
    "clothes",
    "objects"
    ];

    return types[Math.floor(Math.random()*types.length)];

    }

    function generateWordEmojiLevel(setName){

    const set = WORD_SETS[setName];

    if(!set) return null;

    const items = shuffleArray([...set]).slice(0,5);

    return {
    type:setName,
    description:`Match the word with the ${setName}`,
    items:items.map(o=>({
    id:o.word,
    word:o.word,
    emoji:o.emoji
    }))
    };

    }

    function numberToEnglish(n){

    const words = [
    "zero","one","two","three","four","five","six","seven","eight","nine",
    "ten","eleven","twelve","thirteen","fourteen","fifteen","sixteen",
    "seventeen","eighteen","nineteen","twenty"
    ];

    if(n<=20) return words[n];

    if(n<100){

    const tens=["","","twenty","thirty","forty","fifty","sixty","seventy","eighty","ninety"];

    const t=Math.floor(n/10);
    const u=n%10;

    return u===0 ? tens[t] : tens[t]+" "+words[u];

    }

    return n.toString();

    }

    function generateLocalLevel(type) {
        if(WORD_SETS[type]){

        return generateWordEmojiLevel(type);

        }

        if (type === "colors") {

            const items = shuffleArray([...BASE_COLORS]).slice(0,5);

            return {
                type: "simple",
                description: "Match the color with the word",
                items
            };

        }

        if (type === "numbers") {

            const max = Math.min(currentLevel + 5, 100);

            const items = [];

            for (let i = 1; i <= 5; i++) {

                const n = Math.floor(Math.random() * max) + 1;

                items.push({
                    id: "n" + n,
                    word: numberToEnglish(n),
                    value: n.toString()
                });

            }

            return {
                type: "numbers",
                description: "Match the number with the word",
                items
            };

        }

        if (type === "objects") {

            const objects = [
                {id:"dog", word:"dog", emoji:"🐶"},
                {id:"cat", word:"cat", emoji:"🐱"},
                {id:"car", word:"car", emoji:"🚗"},
                {id:"apple", word:"apple", emoji:"🍎"},
                {id:"banana", word:"banana", emoji:"🍌"},
                {id:"bus", word:"bus", emoji:"🚌"},
                {id:"bike", word:"bike", emoji:"🚲"},
                {id:"train", word:"train", emoji:"🚆"}
            ];

            const selected = shuffleArray(objects).slice(0,5);

            return {
                type: "objects",
                description: "Match the object with the word",
                items: selected
            };

        }

        return null;

    }

    function safePlay(audio) {
        if (!audio) return;
        audio.currentTime = 0;
        audio.play().catch(() => {});
    }

    // === Utilidades generales ===
    function setMessage(text, type = "") {
        messageP.textContent = text;
        messageP.className = "english-message";
        if (type) {
            messageP.classList.add(type); // "success" | "error" | "info"
        }
    }

    function updateHUD() {
        errorsSpan.textContent = errors + " / " + MAX_ERRORS;
        scoreSpan.textContent = score;
        levelSpan.textContent = currentLevel;
        timeSpan.textContent = time;
    }

    function stopTimer() {
        if (timerId) {
            clearInterval(timerId);
            timerId = null;
        }
    }

    function startTimer() {
        stopTimer();
        time = 0;
        timeSpan.textContent = time;
        timerId = setInterval(() => {
            time++;
            timeSpan.textContent = time;
        }, 1000);
    }

    function shuffleArray(array) {
        let currentIndex = array.length;
        let randomIndex;
        while (currentIndex !== 0) {
            randomIndex = Math.floor(Math.random() * currentIndex);
            currentIndex--;
            [array[currentIndex], array[randomIndex]] = [array[randomIndex], array[currentIndex]];
        }
        return array;
    }

    //Crear con ia niveles
    async function fetchAILevel() {

        try {

            const resp = await fetch("/api/english/next-level");
            const data = await resp.json();

            if (!data.ok) {
                throw new Error("AI level generation failed");
            }

            return data.data;

        } catch (err) {

            console.error("Error generando nivel IA:", err);
            return null;

        }

    }

    // Sanear nivel IA (en caso de que venga mal formado)
    function sanitizeAILevel(level) {

        if (!level || !level.items) return null;

        const cleanItems = [];

        for (const item of level.items) {

            // simple
            if (level.type === "simple") {

                if (!item.id || !item.word || !item.color) continue;

                cleanItems.push({
                    id: item.id,
                    word: item.word,
                    color: item.color
                });

            }

            // sentence_image
            else if (level.type === "sentence_image") {

                if (!item.id || !item.sentence || !item.img) continue;

                cleanItems.push({
                    id: item.id,
                    sentence: item.sentence,
                    img: item.img,
                    alt: item.alt || "image"
                });

            }

        }

        level.items = cleanItems;

        return level;

    }

    // Cargar nivel usuario
    async function cargarNivelUsuario() {

        try {

            const resp = await fetch("/api/english/next-level");
            const data = await resp.json();

            if (!data.ok) throw new Error("No se pudo obtener nivel");

            currentLevel = data.level;

            if (levelText) {
                levelText.textContent = currentLevel;
            }

        } catch (err) {

            console.error("Error cargando nivel:", err);

        }

    }

    // Construye combinaciones aleatorias de 3 colores para el nivel 5
    function buildCompositeItems(baseColors, count) {
        const results = [];
        const usedIds = new Set();
        let attempts = 0;

        while (results.length < count && attempts < 50) {
            attempts++;

            const shuffled = shuffleArray([...baseColors]);
            const trio = shuffled.slice(0, 3); // 3 colores distintos

            const sortedIds = trio.map((c) => c.id).sort();
            const id = sortedIds.join("_");
            if (usedIds.has(id)) continue; // evitar combos repetidos

            usedIds.add(id);
            const colors = trio.map((c) => c.color);
            const words = trio.map((c) => c.word);

            const sentence = `This color contains ${words[0]}, ${words[1]} and ${words[2]}.`;

            results.push({
                id,
                sentence,
                colors,
            });
        }
        return results;
    }

    // === Render del tablero según nivel actual ===
    async function renderBoard() {

        let levelCfg = COLOR_LEVELS[currentLevel];

        // 🔹 Si no existe nivel local → generar con IA
        if (!levelCfg) {

            const type = getAILevelType(currentLevel);

            let aiLevel = generateLocalLevel(type);

            if (!aiLevel) {
                const aiLevelRaw = await fetchAILevel();
                aiLevel = sanitizeAILevel(aiLevelRaw);
            }

            if (!aiLevel) {
                setMessage("Nivel IA inválido. Generando otro...", "error");
                return renderBoard();
            }

            levelCfg = aiLevel;

        }

        if (!levelCfg) return;

        if (levelCfg.type === "simple") {
            targetsTitle.textContent = "Colores";
        } else if (levelCfg.type === "sentence_image") {
            targetsTitle.textContent = "Imágenes";
        } else if (levelCfg.type === "composite") {
            targetsTitle.textContent = "Colores combinados";
        } else if (WORD_SETS[levelCfg.type]) {
            targetsTitle.textContent = levelCfg.type;
        }

        descriptionP.textContent = levelCfg.description;

        wordsContainer.innerHTML = "";
        targetsContainer.innerHTML = "";

        let items;
        if (levelCfg.type === "composite") {
            items = buildCompositeItems(levelCfg.baseColors, levelCfg.count);
        } else {
            items = shuffleArray([...levelCfg.items]);
        }

        remainingPairs = items.length;

        // =========================
        // NUMBERS
        // =========================
        if (levelCfg.type === "numbers") {

            targetsTitle.textContent = "Numbers";

            items.forEach((item) => {

                const wordEl = document.createElement("div");
                wordEl.classList.add("eg-word");
                wordEl.textContent = item.word;
                wordEl.draggable = true;
                wordEl.dataset.targetId = item.id;
                wordEl.addEventListener("dragstart", onDragStart);

                wordsContainer.appendChild(wordEl);

            });

            const targets = shuffleArray([...items]);

            targets.forEach((item) => {

                const targetEl = document.createElement("div");
                targetEl.classList.add("eg-target");
                targetEl.dataset.id = item.id;
                targetEl.textContent = item.value;

                targetEl.addEventListener("dragover", onDragOver);
                targetEl.addEventListener("drop", onDrop);

                targetsContainer.appendChild(targetEl);

            });

            return;
        }

        // Objetos
        if (levelCfg.type === "objects" || WORD_SETS[levelCfg.type]) {

            targetsTitle.textContent = "Objects";

            items.forEach((item) => {

                const wordEl = document.createElement("div");
                wordEl.classList.add("eg-word");
                wordEl.textContent = item.word;
                wordEl.draggable = true;
                wordEl.dataset.targetId = item.id;
                wordEl.addEventListener("dragstart", onDragStart);

                wordsContainer.appendChild(wordEl);

            });

            const targets = shuffleArray([...items]);

            targets.forEach((item) => {

                const targetEl = document.createElement("div");
                targetEl.classList.add("eg-target");
                targetEl.dataset.id = item.id;
                targetEl.textContent = item.emoji;

                targetEl.addEventListener("dragover", onDragOver);
                targetEl.addEventListener("drop", onDrop);

                targetsContainer.appendChild(targetEl);

            });

            return;
        }


        if (levelCfg.type === "simple") {
            // Palabras (izquierda)
            items.forEach((item) => {
                const wordEl = document.createElement("div");
                wordEl.classList.add("eg-word");
                wordEl.textContent = item.word;
                wordEl.draggable = true;
                wordEl.dataset.targetId = item.id;
                wordEl.addEventListener("dragstart", onDragStart);
                wordsContainer.appendChild(wordEl);
            });

            // Cuadrados de color (derecha)
            const targets = shuffleArray([...items]);
            targets.forEach((item) => {
                const targetEl = document.createElement("div");
                targetEl.classList.add("eg-target", "eg-target-color");
                targetEl.dataset.id = item.id;
                targetEl.style.backgroundColor = item.color;
                if (item.id === "white" || item.id === "beige" || item.id === "lightblue") {
                    targetEl.classList.add("eg-target-light");
                }
                targetEl.addEventListener("dragover", onDragOver);
                targetEl.addEventListener("drop", onDrop);
                targetsContainer.appendChild(targetEl);
            });
        } else if (levelCfg.type === "sentence_image") {
            // Frases (izquierda)
            items.forEach((item) => {
                const wordEl = document.createElement("div");
                wordEl.classList.add("eg-word");
                wordEl.textContent = item.sentence;
                wordEl.draggable = true;
                wordEl.dataset.targetId = item.id;
                wordEl.addEventListener("dragstart", onDragStart);
                wordsContainer.appendChild(wordEl);
            });

            // Imágenes (derecha)
            const targets = shuffleArray([...items]);
            targets.forEach((item) => {
                const targetEl = document.createElement("div");
                targetEl.classList.add("eg-target", "eg-target-image");
                targetEl.dataset.id = item.id;

                const img = document.createElement("img");
                img.src = item.img;
                img.alt = item.alt || "Image";
                targetEl.appendChild(img);

                targetEl.addEventListener("dragover", onDragOver);
                targetEl.addEventListener("drop", onDrop);
                targetsContainer.appendChild(targetEl);
            });
        } else if (levelCfg.type === "composite") {
            // Frases (izquierda)
            items.forEach((item) => {
                const wordEl = document.createElement("div");
                wordEl.classList.add("eg-word");
                wordEl.textContent = item.sentence;
                wordEl.draggable = true;
                wordEl.dataset.targetId = item.id;
                wordEl.addEventListener("dragstart", onDragStart);
                wordsContainer.appendChild(wordEl);
            });

            // Cuadros combinados (derecha)
            const targets = shuffleArray([...items]);
            targets.forEach((item) => {
                const targetEl = document.createElement("div");
                targetEl.classList.add("eg-target", "eg-target-composite");
                targetEl.dataset.id = item.id;

                const [c1, c2, c3] = item.colors;
                targetEl.style.background = `linear-gradient(
                    90deg,
                    ${c1} 0%,   ${c1} 33%,
                    ${c2} 33%,  ${c2} 66%,
                    ${c3} 66%,  ${c3} 100%
                )`;

                targetEl.addEventListener("dragover", onDragOver);
                targetEl.addEventListener("drop", onDrop);
                targetsContainer.appendChild(targetEl);
            });
        }
    }

    // === Drag & drop ===
    function onDragStart(ev) {
        ev.dataTransfer.setData("text/plain", ev.target.dataset.targetId);
        ev.dataTransfer.effectAllowed = "move";
        ev.target.classList.add("dragging");
    }

    function onDragOver(ev) {
        ev.preventDefault();
        ev.dataTransfer.dropEffect = "move";
        ev.currentTarget.classList.add("eg-target-hover");
    }

    function onDrop(ev) {
        ev.preventDefault();
        const target = ev.currentTarget;
        target.classList.remove("eg-target-hover");

        const expectedId = target.dataset.id;
        const draggedId = ev.dataTransfer.getData("text/plain");

        const draggingEl = document.querySelector(
            `.eg-word.dragging[data-target-id="${draggedId}"]`
        );
        if (draggingEl) {
            draggingEl.classList.remove("dragging");
        }

        if (!draggedId || !expectedId) return;

        if (draggedId === expectedId) {
            // ✅ Acierto
            safePlay(soundCorrect);
            score += 10;
            remainingPairs--;

            target.classList.add("eg-target-correct");
            target.dataset.completed = "true";

            if (draggingEl) {
                draggingEl.classList.add("eg-word-correct");
                draggingEl.draggable = false;
                setTimeout(() => draggingEl.remove(), 300);
            }

            setMessage("¡Bien hecho! 👍", "success");
            updateHUD();

            if (remainingPairs === 0) {

                safePlay(soundWin);
                stopTimer();

                setMessage(
                    "🎉 ¡Nivel completado! Cargando siguiente nivel...",
                    "success"
                );

                // guardar puntuación
                if (window.JCM_USER && window.JCM_USER.id) {
                    saveEnglishColorsScore().catch((err) =>
                        console.error("Error guardando puntuación:", err)
                    );
                }

                // subir nivel en backend
                async function avanzarNivel() {

                    try {

                        await fetch("/api/english/complete-level", {
                            method: "POST"
                        });

                    } catch (err) {
                        console.error("Error avanzando nivel:", err);
                    }

                }

                // cargar siguiente nivel
                setTimeout(async () => {

                    await avanzarNivel();

                    await cargarNivelUsuario();

                    errors = 0;
                    score = 0;
                    time = 0;
                    updateHUD();

                    await renderBoard();

                    startTimer();

                }, 1500);
            }
        } else {
            // ❌ Error
            safePlay(soundWrong);
            errors++;
            updateHUD();
            setMessage("Ups... respuesta incorrecta.", "error");

            if (errors >= MAX_ERRORS) {
                stopTimer();

                setMessage(
                    "❌ Demasiados errores. Repites el nivel.",
                    "error"
                );

                setTimeout(async () => {

                    errors = 0;
                    score = 0;

                    updateHUD();

                    await renderBoard();

                    startTimer();

                }, 2000);
            }
        }
    }

    document.addEventListener("dragend", () => {
        document
            .querySelectorAll(".eg-word.dragging")
            .forEach((el) => el.classList.remove("dragging"));
    });

    // === Gestión del panel de usuario ===
    function updateUserPanel(stats = null) {
        // Sin usuario
        if (!currentUser) {
            userGuestDiv?.classList.remove("hidden");
            userLoggedDiv?.classList.add("hidden");
            return;
        }

        // Con usuario
        userGuestDiv?.classList.add("hidden");
        userLoggedDiv?.classList.remove("hidden");

        spanUserName.textContent = currentUser.username || "";

        if (stats) {
            spanBestScoreGlobal.textContent = stats.best_global ?? 0;
            spanTotalScore.textContent = stats.total_score ?? 0;
            spanBestScoreLevel.textContent = stats.best_level ?? 0;
        } else {
            spanBestScoreGlobal.textContent ||= "0";
            spanTotalScore.textContent ||= "0";
            spanBestScoreLevel.textContent ||= "0";
        }
    }

    // ✅ Sin endpoint /api/current-user: sincronizamos con auth.js
    function syncUserFromAuth() {
        currentUser = window.JCM_USER ? { ...window.JCM_USER } : null;
        updateUserPanel();
    }

    // Si cambia el usuario (login/logout), refrescamos
    window.addEventListener("jcm:user-changed", (ev) => {
        const user = ev.detail?.user || null;
        currentUser = user ? { ...user } : null;
        updateUserPanel();
    });

    // === Ranking del juego ===
    async function fetchRanking() {
        if (!rankingBody) return;

        try {
            const resp = await fetch(`${API_BASE}/api/english-colors/ranking`);
            if (!resp.ok) throw new Error("HTTP " + resp.status);
            const data = await resp.json();
            if (!data.ok) throw new Error("Respuesta no OK");

            const ranking = data.ranking || [];
            rankingBody.innerHTML = "";

            if (ranking.length === 0) {
                const tr = document.createElement("tr");
                const td = document.createElement("td");
                td.colSpan = 4;
                td.textContent = "Todavía no hay puntuaciones registradas.";
                tr.appendChild(td);
                rankingBody.appendChild(tr);
                return;
            }

            ranking.forEach((item) => {
                const tr = document.createElement("tr");

                const tdPos = document.createElement("td");
                tdPos.textContent = item.position;

                const tdUser = document.createElement("td");
                tdUser.textContent = item.username;

                const tdBest = document.createElement("td");
                tdBest.textContent = item.best_score;

                const tdGames = document.createElement("td");
                tdGames.textContent = item.games_played;

                tr.appendChild(tdPos);
                tr.appendChild(tdUser);
                tr.appendChild(tdBest);
                tr.appendChild(tdGames);

                rankingBody.appendChild(tr);
            });
        } catch (err) {
            console.error("Error cargando ranking:", err);
        }
    }

    // === Guardar puntuación del juego en el backend ===
    async function saveEnglishColorsScore() {
        const payload = {
            level: currentLevel,
            score: score,
            duration_sec: time,
        };

        const resp = await fetch(`${API_BASE}/api/english-colors/save-score`, {
            method: "POST",
            credentials: "include", // ✅ CLAVE para que viaje la cookie de sesión
            headers: { "Content-Type": "application/json" },
            body: JSON.stringify(payload),
        });

        if (!resp.ok) {
            console.warn("No se pudo guardar la puntuación (HTTP " + resp.status + ")");
            return;
        }

        const data = await resp.json();
        if (data.ok) {
            updateUserPanel({
                best_global: data.best_global,
                total_score: data.total_score,
                best_level: data.best_level,
            });
            // Actualizar ranking tras nueva puntuación
            fetchRanking();
        }
    }

    // === Botón Empezar ===
    startBtn.addEventListener("click", () => {
        errors = 0;
        score = 0;
        time = 0;
        updateHUD();
        renderBoard();
        startTimer();
        setMessage("¡Empieza! Arrastra cada palabra / frase hasta su pareja correcta.", "info");
    });

    // === Inicialización ===
    (async () => {

        await cargarNivelUsuario();

        updateHUD();

        setMessage('Pulsa "Empezar nivel" para comenzar.', "info");

    })();

    // Sincronizar usuario y cargar ranking al entrar
    syncUserFromAuth();
    fetchRanking();
});
