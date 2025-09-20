const barra = document.getElementById("barra");
const actual = document.getElementById("actual");
const total = document.getElementById("total");
const form = document.getElementById("form-excel");
const actualizaciones = document.getElementById("Actualizaciones");
let intervalo = null;

form.addEventListener("submit", function(e) {
    e.preventDefault();

    const formData = new FormData(form);

    fetch(form.action, {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        agregarLog("Importación iniciada", "info");
        
        if (intervalo) clearInterval(intervalo);
        intervalo = setInterval(() => {
            fetch("/progreso")
                .then(r => r.json())
                .then(data => {
                    barra.style.width = data.valor + "%";
                    barra.innerText = data.valor + "%";
                    actual.textContent = data.actual;
                    total.textContent = data.total;
                    console.log("PROGRESO: "+data.valor + "%");
                agregarLog(("Progreso"+data.valor + "%"), "success");
                    
                    if (data.valor >= 100) {
                        clearInterval(intervalo);
                        intervalo = null;
                        agregarLog("Importación finalizada", "secondary");

                    }
            });
        }, 1000);
    })
    .catch(error => {
        console.error("Error al enviar el formulario:", error);
    });
});

function agregarLog(mensaje, tipo = "info") {
    // tipo puede ser: info, success, warning, danger
    const logs = document.getElementById("logs");

    const card = document.createElement("div");
    card.className = `card my-2 border-${tipo}`;

    const body = document.createElement("div");
    body.className = "card-body p-2 text-left";

    body.innerHTML = `<span class="badge bg-${tipo} text-uppercase">${tipo}</span> ${mensaje}`;
    
    card.appendChild(body);
    logs.appendChild(card);

    // Scroll automatico al ultimo log
    logs.scrollTop = logs.scrollHeight;
}
