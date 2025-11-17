/* CHATBOT GLOWIN — FUNCIONALIDAD */

(function () {

    const openBtn = document.getElementById('glowinChatOpen');
    const closeBtn = document.getElementById('glowinChatClose');
    const win = document.getElementById('glowinChat');
    const bodyDiv = document.getElementById('gcwBody');
    const inputBar = document.getElementById('gcwInput');
    const inputText = document.getElementById('gcwText');
    const sendBtn = document.getElementById('gcwSend');

    let state = { step: 'welcome', name: null };

    function addMsg(text, who = 'bot') {
        const b = document.createElement('div');
        b.className = 'msg ' + who;
        b.textContent = text;
        bodyDiv.appendChild(b);
        bodyDiv.scrollTop = bodyDiv.scrollHeight;
    }

    function addQuick(buttons) {
        const wrap = document.createElement('div');
        wrap.className = 'gcw-quick';

        buttons.forEach(btn => {
            const b = document.createElement('button');
            b.textContent = btn.text;
            b.onclick = btn.onClick;
            wrap.appendChild(b);
        });

        bodyDiv.appendChild(wrap);
        bodyDiv.scrollTop = bodyDiv.scrollHeight;
    }

    async function sendToIA(text) {
        const form = new FormData();
        form.append("mensaje", text);

        const res = await fetch("/productos/ia-chat/", {
            method: "POST",
            body: form
        });

        return await res.json();
    }

    function start() {
        bodyDiv.innerHTML = '';
        addMsg('¡Hola! Soy tu asesora Glowin ✨ ¿Puedo ayudarte a encontrar algo hoy?');

        addQuick([
            { text: 'Sí, claro', onClick: yesFlow },
            { text: 'No, gracias', onClick: () => addMsg('Perfecto 🌸. Si necesitas algo, estaré aquí.') }
        ]);
    }

    function yesFlow() {
        state.step = 'ask_name';
        addMsg('¡Genial! ¿Cómo te llamas?');
        inputBar.style.display = 'flex';
        inputText.placeholder = 'Escribe tu nombre';
        inputText.focus();
    }

    function afterName() {
        state.step = "chat";
        addMsg(`Encantada, ${state.name} 💕. ¿Qué categoría deseas explorar?`);
        inputBar.style.display = 'none';

        addQuick([
            { text: 'Maquillaje', onClick: () => categoryFlow("maquillaje") },
            { text: 'Cuidado de la Piel', onClick: () => categoryFlow("piel") },
            { text: 'Cuidado Capilar', onClick: () => categoryFlow("cabello") },
            { text: 'Ropa', onClick: () => categoryFlow("ropa") },
        ]);
    }

    function categoryFlow(cat) {
        const textos = {
            maquillaje: "Perfecto 💄 ¿Qué deseas saber sobre maquillaje?",
            piel: "Excelente 🧴 ¿Qué quieres saber sobre tu piel?",
            cabello: "¡Cabello radiante! 💇‍♀️ ¿Qué deseas saber sobre tu cabello?",
            ropa: "¡Hermoso estilo! 👗 ¿Buscas algo casual, elegante o para una ocasión especial?"
        };

        addMsg(textos[cat]);
        inputBar.style.display = 'flex';
    }

    function handleSend() {
        const text = inputText.value.trim();
        if (!text) return;

        addMsg(text, "user");
        inputText.value = "";

        if (state.step === 'ask_name') {
            state.name = text;
            afterName();
            return;
        }

        sendToIA(text).then(data => {
            if (data.mensaje) addMsg(data.mensaje, "bot");

            if (data.tipo === "producto" && data.url) {

                const html = `
        <div class="gcw-product" style="
            background:white;
            border:1px solid #f3d0de;
            padding:10px;
            border-radius:12px;
            margin-top:10px;
            max-width:240px;
        ">
            ${data.imagen ? `
                <img src="${data.imagen}" style="
                    width:100%;
                    height:180px;
                    object-fit:cover;
                    border-radius:10px;
                ">
            ` : ""}

            <h4 style="font-size:15px; margin-top:8px; font-weight:600;">
                ${data.nombre}
            </h4>

            <p style="font-size:13px; color:#555;">
                ${data.descripcion || ""}
            </p>

            <a href="${data.url}" target="_blank" style="
                display:block;
                text-align:center;
                background:#d63384;
                color:white;
                padding:8px;
                border-radius:10px;
                text-decoration:none;
                margin-top:6px;
                font-size:14px;
            ">
                Ver producto
            </a>
        </div>
    `;

                const wrap = document.createElement("div");
                wrap.innerHTML = html;
                bodyDiv.appendChild(wrap);
                bodyDiv.scrollTop = bodyDiv.scrollHeight;
            }

        });
    }

    openBtn?.addEventListener("click", () => {
        win.style.display = "flex";
        start();
    });

    closeBtn?.addEventListener("click", () => {
        win.style.display = "none";
    });

    sendBtn?.addEventListener("click", handleSend);

    inputText?.addEventListener("keydown", (e) => {
        if (e.key === "Enter") handleSend();
    });

})();
