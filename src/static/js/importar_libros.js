const barra = document.getElementById("barra");
const actual = document.getElementById("actual");
const total = document.getElementById("total");
const form = document.getElementById("form-excel");
const logs = document.getElementById("logs");
const nota = document.getElementById("nota");
let intervalo = null;
const progressbar = document.getElementById("progressbar");
let i = 0;

let logIndex = 0;

form.addEventListener("submit", function(e) {
    e.preventDefault();
    progressbar.classList.remove("d-none");
    nota.classList.add('d-none');
    logs.innerHTML = "";
    logIndex = 0;
    const formData = new FormData(form);

    fetch(form.action, {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        agregarLog("Importación iniciada", "secondary");
        let descargar_errores = false;
        if (intervalo) clearInterval(intervalo);
        intervalo = setInterval(() => {
            fetch("/progreso")
                .then(r => r.json())
                .then(data => {
                    barra.style.width = data.valor + "%";
                    barra.innerText = data.valor + "%";
                    actual.textContent = data.actual - data.contador_errores;
                    total.textContent = data.total;
                    if(data.error){
                        descargar_errores = true;
                    }
                    
                    if ((data.valor >= 100)) {
                        if(descargar_errores){
                            agregarLog(("!: "+data.error), "danger");
                            agregarLog(("!: "+data.duplicados), "danger")
                            agregarLog("Descargar errores","descargar_errores")
                        }
                        clearInterval(intervalo);
                        intervalo = null;
                        agregarLog("Importación finalizada", "secondary");
                    }
            });
        }, 600);
    })
    .catch(error => {
        console.error("Error al enviar el formulario:", error);
        agregarLog("Error al iniciar importación: " + error.message, "danger");
    });
});

function agregarLog(mensaje, tipo = "info", delay = 0) { 
    setTimeout(() => { 
        const card = document.createElement("div");
        card.className = `card my-1 text-left border-${tipo}`;

        const body = document.createElement("div");
        body.className = "card-body p-2 text-start";

        body.innerHTML = `<span class="badge text-${tipo} ">
                            <i class="bi bi-circle-fill"></i>
                            <span class="vr mx-2" ></span>
                            </span> ${mensaje}`;

        if(tipo == "descargar_errores"){
            card.className = `card my-1 text-left border-warning`;
            body.innerHTML = `<span class="badge text-warning ">
                                <i class="bi bi-circle-fill"></i>
                                <span class="vr mx-2" ></span>
                                </span><a class="btn btn-warning" href="/descargar_errores">${mensaje}</a>`;
        }
        
        card.appendChild(body);
        
        Object.assign(card.style, {
            transform: 'translateY(2px)',
            visibility: 'hidden',
            transition: 'none'
        });
        
        // Inserta aun invisible
        logs.appendChild(card);
        
        requestAnimationFrame(() => {
            card.style.transition = ''; 
            card.style.visibility = 'visible';
            card.classList.add('log-animate');
        });
        
        setTimeout(() => {
            card.classList.remove('log-animate');
        }, 400); 
        
        logIndex++;
    }, delay);
}
