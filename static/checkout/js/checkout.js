/* CHECKOUT — CONTROL DE PASOS */

function goToStep(step) {
    ["step1", "step2", "step3"].forEach(id => {
        document.getElementById(id).classList.add("hidden");
    });

    document.getElementById(`step${step}`).classList.remove("hidden");
    updateProgress(step);
}

function updateProgress(step) {
    [1, 2, 3].forEach(n => {
        document.getElementById(`prog-${n}`).classList.remove("active");
    });

    for (let i = 1; i <= step; i++) {
        document.getElementById(`prog-${i}`).classList.add("active");
    }

    document.getElementById("line-1").classList.toggle("active", step >= 2);
    document.getElementById("line-2").classList.toggle("active", step == 3);
}

/* ACTUALIZAR RESUMEN DE ENVÍO */
document.addEventListener("click", () => {
    const costoInput = document.getElementById("costoEnvio");
    const resumen = document.getElementById("envioResumen");
    if (!costoInput || !resumen) return;

    resumen.textContent = "$ " + Number(costoInput.value).toLocaleString("es-CO");
});
