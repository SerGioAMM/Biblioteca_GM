const tabla_vista_previa = document.getElementById("vista_previa");
const body_tabla_vista_previa = tabla_vista_previa.querySelector("tbody");
const btn_exportar = document.getElementById("btn-exportar");

function agregar_vista_previa(autor, libro, lugar, editorial, anio, paginas, isbn, tomo, categoria, notacion, copias, delay = 0) {
    setTimeout(() => {
        const fila = document.createElement('tr');
        fila.classList.add('small');
        
        // Estado inicial
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
        
        // Inserta aun invisible
        body_tabla_vista_previa.appendChild(fila);
        
        requestAnimationFrame(() => {  
            fila.style.transition = '';  
            fila.style.visibility = 'visible'; 
            fila.classList.add('row-animate');
        });
        
    }, delay);
}

function limpiarTabla() {
    // Limpia SOLO el tbody (no toca thead)
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

btn_exportar.addEventListener("click", () => {
    // Limpia la tabla antes de cargar nuevos datos
    limpiarTabla();
    
    fetch('/vista_previa')
        .then(r => {
            if (!r.ok) {
                throw new Error('Error en la respuesta del servidor');
            }
            return r.json();
        })
        .then(data => {
            console.log("data:", data);
            
            if (Array.isArray(data) && data.length > 0) {
                // Itera con delay secuencial (150ms por fila para fluidez)
                data.forEach((fila, index) => {
                    const { nombre_autor, apellido_autor, Titulo, lugar, editorial, ano_publicacion, numero_paginas, ISBN, tomo, codigo_seccion, notacion, numero_copias } = fila;
                    const autorCompleto = (nombre_autor + " " + apellido_autor).trim();
                    agregar_vista_previa(autorCompleto, Titulo, lugar, editorial, ano_publicacion, numero_paginas, ISBN, tomo, codigo_seccion, notacion, numero_copias, index * 200);
                });
            } else {
                console.log("No hay datos para mostrar");
                mostrarMensajeNoDatos();
            }
        })
        .catch(error => {
            console.error("Error al fetch:", error);
            mostrarMensajeNoDatos("Error al cargar datos: " + error.message);
        });
});
