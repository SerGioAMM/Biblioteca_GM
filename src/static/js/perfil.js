// Elementos del DOM
const btn_perfil = document.getElementById('btn-perfil');
const btn_editar = document.getElementById('btn-editar');
const btn_guardar = document.getElementById('btn-guardar');
const btn_actividad = document.getElementById('btn-actividad');
const btn_notificaciones = document.getElementById('btn-notificaciones');
const btn_marcar_leidas = document.getElementById('btn-marcar-leidas');

const detalles_perfil = document.querySelector('.detalles-perfil');
const actividad_section = document.getElementById('actividad-section');
const notificaciones_section = document.getElementById('notificaciones-section');
const form_editar = document.getElementById('form-editar-perfil');

const btn_texto = btn_editar.querySelector('span');

// Funciones de utilidad
function mostrar(elemento) {
    elemento.classList.remove('d-none');
}

function ocultar(elemento) {
    elemento.classList.add('d-none');
}

function ocultarTodasLasSecciones() {
    ocultar(detalles_perfil);
    ocultar(actividad_section);
    ocultar(notificaciones_section);
    ocultar(form_editar);
}

function resetearBotones() {
    // Resetear todos los botones a su estado normal
    btn_perfil.classList.remove('btn-primary');
    btn_perfil.classList.add('btn-outline-primary');
    
    btn_actividad.classList.remove('btn-primary');
    btn_actividad.classList.add('btn-outline-primary');
    
    btn_notificaciones.classList.remove('btn-primary');
    btn_notificaciones.classList.add('btn-outline-info');
    
    // Resetear botón editar
    btn_texto.textContent = 'Editar Perfil';
    btn_editar.querySelector('i').className = 'bi bi-pencil-square';
    btn_editar.classList.remove('btn-outline-danger');
    btn_editar.classList.add('btn-outline-secondary');
    ocultar(btn_guardar);
}

function activarBoton(boton, estiloActivo) {
    resetearBotones();
    boton.classList.remove('btn-outline-primary', 'btn-outline-info', 'btn-outline-secondary');
    boton.classList.add(estiloActivo);
}

// Event Listeners
btn_perfil.addEventListener("click", () => {
    ocultarTodasLasSecciones();
    activarBoton(btn_perfil, 'btn-primary');
    mostrar(detalles_perfil);
});

btn_actividad.addEventListener("click", () => {
    ocultarTodasLasSecciones();
    activarBoton(btn_actividad, 'btn-primary');
    mostrar(actividad_section);
});

btn_notificaciones.addEventListener("click", () => {
    ocultarTodasLasSecciones();
    activarBoton(btn_notificaciones, 'btn-primary');
    mostrar(notificaciones_section);
});

btn_editar.addEventListener("click", () => {
    if (form_editar.classList.contains('d-none')) {
        // Mostrar formulario de edición
        ocultarTodasLasSecciones();
        mostrar(form_editar);
        mostrar(btn_guardar);
        
        btn_texto.textContent = 'Cancelar';
        btn_editar.querySelector('i').className = 'bi bi-x-circle';
        btn_editar.classList.remove('btn-outline-secondary');
        btn_editar.classList.add('btn-outline-danger');
    } else {
        // Cancelar edición
        ocultarTodasLasSecciones();
        mostrar(detalles_perfil);
        resetearBotones();
        
        // Resetear formulario
        form_editar.reset();
        // Restaurar valores originales
        campos.forEach((campo, i) => {
            if (i < original.length) {
                campo.value = original[i];
            }
        });
        btn_guardar.setAttribute('disabled', '');
    }
});

// Marcar notificaciones como leídas
if (btn_marcar_leidas) {
    btn_marcar_leidas.addEventListener("click", () => {
        fetch('/marcar_notificaciones_leidas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                location.reload();
            }
        })
        .catch(error => {
            console.error('Error:', error);
        });
    });
}

// Manejo del formulario de edición
const editables = document.querySelectorAll('.editable');
let original = [];
let campos = [];

editables.forEach((input) => {
    input.classList.add('border-warning');
    campos.push(input);
});

// Función para verificar si hay cambios
function verificarCambios() {
    let hayCambios = false;
    
    for (let i = 0; i < campos.length; i++) {
        if (campos[i].value !== (original[i] || '')) {
            hayCambios = true;
            break;
        }
    }
    
    // Verificar contraseñas
    const nuevaContrasena = document.querySelector('input[name="nueva_contrasena"]');
    const confirmarContrasena = document.querySelector('input[name="confirmar_contrasena"]');
    
    if (nuevaContrasena && nuevaContrasena.value) {
        hayCambios = true;
    }
    
    if (hayCambios) {
        btn_guardar.removeAttribute('disabled');
    } else {
        btn_guardar.setAttribute('disabled', "");
    }
}

// Validación de contraseñas
function validarContrasenas() {
    const nuevaContrasena = document.querySelector('input[name="nueva_contrasena"]');
    const confirmarContrasena = document.querySelector('input[name="confirmar_contrasena"]');
    
    if (nuevaContrasena.value !== confirmarContrasena.value) {
        confirmarContrasena.setCustomValidity('Las contraseñas no coinciden');
    } else {
        confirmarContrasena.setCustomValidity('');
    }
}

// Inicializar valores originales y eventos
for (let i = 0; i < editables.length; i++) {
    original.push(campos[i].value);
    campos[i].addEventListener("input", verificarCambios);
}

// Event listeners para validación de contraseñas
const nuevaContrasena = document.querySelector('input[name="nueva_contrasena"]');
const confirmarContrasena = document.querySelector('input[name="confirmar_contrasena"]');

if (nuevaContrasena && confirmarContrasena) {
    nuevaContrasena.addEventListener('input', validarContrasenas);
    confirmarContrasena.addEventListener('input', validarContrasenas);
}

// Mostrar detalles del perfil por defecto y activar botón
document.addEventListener('DOMContentLoaded', function() {
    // Verificar si hay un hash en la URL
    const hash = window.location.hash;
    
    if (hash === '#notificaciones') {
        // Mostrar sección de notificaciones si viene desde el navbar
        ocultarTodasLasSecciones();
        activarBoton(btn_notificaciones, 'btn-primary');
        mostrar(notificaciones_section);
    } else {
        // Mostrar perfil por defecto
        mostrar(detalles_perfil);
        activarBoton(btn_perfil, 'btn-primary');
    }
});