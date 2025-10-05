const barra = document.getElementById("barra");
const actual = document.getElementById("actual");
const total = document.getElementById("total");
const logs = document.getElementById("logs");
const nota = document.getElementById("nota");
const progressbar = document.getElementById("progressbar");
let intervalo = null;
let logIndex = 0;

const tabla_vista_previa = document.getElementById("vista_previa");
const head_tabla_vista_previa = tabla_vista_previa.querySelector("thead");
const body_tabla_vista_previa = tabla_vista_previa.querySelector("tbody");
const btn_vista_previa = document.getElementById("btn-vista-previa");
const btn_exportar = document.getElementById("btn-exportar");
const form_exportar = document.getElementById("form-exportar");

let cantidad_libros = document.getElementById("cantidad");
let categoria_libros = document.getElementById("filtro-categorias");

function agregar_vista_previa(autor, libro, lugar, editorial, anio, paginas, isbn, tomo, categoria, notacion, copias, delay = 0) {
    setTimeout(() => {
        const fila = document.createElement('tr');
        fila.classList.add('small');

        Object.assign(fila.style, {
            opacity: '0',
            transform: 'translateY(-3px)',
            visibility: 'hidden',
            transition: 'none'
        });

        fila.innerHTML = `
            <td>${autor || ''}</td>
            <td>${libro || ''}</td>
            <td>${lugar || ''}</td>
            <td>${editorial || ''}</td>
            <td>${anio || ''}</td>
            <td>${paginas || ''}</td>
            <td>${isbn || ''}</td>
            <td>${tomo || ''}</td>
            <td>${categoria || ''}</td>
            <td>${notacion || ''}</td>
            <td>${copias || ''}</td>
        `;

        body_tabla_vista_previa.appendChild(fila);

        requestAnimationFrame(() => {
            fila.style.transition = '';
            fila.style.visibility = 'visible';
            fila.classList.add('row-animate');
        });

    }, delay);
}

function limpiarTabla() {
    while (body_tabla_vista_previa.firstChild) {
        body_tabla_vista_previa.removeChild(body_tabla_vista_previa.firstChild);
    }
}

function mostrarMensajeNoDatos(mensaje = "No hay datos disponibles para la vista previa.") {
    limpiarTabla();
    const filaMensaje = document.createElement('tr');
    filaMensaje.className = "no-data-message";
    filaMensaje.innerHTML = `<td colspan="11">${mensaje}</td>`;
    body_tabla_vista_previa.appendChild(filaMensaje);
}

btn_vista_previa.addEventListener("click", () => {
    limpiarTabla();
    head_tabla_vista_previa.classList.remove('d-none');
    nota.classList.add('d-none');
    fetch('/vista_previa/'+(cantidad_libros.value)+'/'+(categoria_libros.value))
        .then(r => {
            if (!r.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return r.json();
        })
        .then(data => {            
            if (Array.isArray(data) && data.length > 0) {
                data.forEach((fila, index) => {
                    const { nombre_autor, apellido_autor, Titulo, lugar, editorial, ano_publicacion, numero_paginas, ISBN, tomo, codigo_seccion, notacion, numero_copias } = fila;
                    agregar_vista_previa((nombre_autor + " " + apellido_autor), Titulo, lugar, editorial, ano_publicacion, numero_paginas, ISBN, tomo, codigo_seccion, notacion, numero_copias, index * 200);
                });
            } else {
                mostrarMensajeNoDatos();
            }
            btn_exportar.classList.remove('d-none');
        })
        .catch(error => {
            console.error("Error al fetch:", error);
            mostrarMensajeNoDatos("Error al cargar datos: " + error.message);
        });
});

// -------------------------------------------------- EXPORTAR CON INTERVALO --------------------------------------------------
form_exportar.addEventListener("submit", function(e) {
    e.preventDefault();
    progressbar.classList.remove("d-none");
    nota.classList.add('d-none');
    logs.innerHTML = "";
    logIndex = 0;
    const formData = new FormData(form_exportar);

    fetch(form_exportar.action, {
        method: "POST",
        body: formData
    })
    .then(response => response.text())
    .then(data => {
        agregarLog("Exportación iniciada", "secondary");

        if (intervalo) clearInterval(intervalo);
        intervalo = setInterval(() => {
            fetch("/progreso_exportacion")
                .then(r => r.json())
                .then(data => {
                    barra.style.width = data.valor + "%";
                    barra.innerText = data.valor + "%";
                    actual.textContent = data.actual;
                    total.textContent = data.total;
                    if (data.valor >= (Math.round(data.actual / data.total))) {
                        if(data.actual < data.total){
                            agregarLog("La cantidad de libros ingresada excede la cantidad de libros registrada en el sistema","danger")
                        }
                        clearInterval(intervalo);
                        intervalo = null;
                        agregarLog("Descargar exportacion","descargar_exportacion");
                        agregarLog("Exportación finalizada", "secondary");
                    }
                })
                .catch(error => {
                    console.error("Error en progreso:", error);
                    agregarLog("Error al obtener progreso: " + error.message, "danger");
                });
        }, 600);
    })
    .catch(error => {
        console.error("Error al enviar el formulario:", error);
        agregarLog("Error al iniciar exportación: " + error.message, "danger");
    });
});

// -------------------------------------------------- LOGS --------------------------------------------------
function agregarLog(mensaje, tipo = "info", delay = 0) { 
    setTimeout(() => { 
        const card = document.createElement("div");
        card.className = `card my-1 text-left border-${tipo}`;

        const body = document.createElement("div");
        body.className = "card-body p-2 text-start";

        body.innerHTML = `<span class="badge text-${tipo} ">
                            <i class="bi bi-circle-fill"></i>
                            <span class="vr mx-2"></span>
                            </span> ${mensaje}`;

        if (tipo == "descargar_exportacion") {
            card.className = `card my-1 text-left border-warning`;
            body.innerHTML = `<span class="badge text-warning ">
                                <i class="bi bi-circle-fill"></i>
                                <span class="vr mx-2"></span>
                                </span><a class="btn btn-warning" href="/descargar_exportacion">${mensaje}</a>`;
        }

        card.appendChild(body);

        Object.assign(card.style, {
            transform: 'translateY(2px)',
            visibility: 'hidden',
            transition: 'none'
        });

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
