const form_editar = document.getElementById('form-editar-libro');
const btn_editar = document.getElementById('btn-editar');
const btn_texto = btn_editar.querySelector('span');
const btn_guardar = document.getElementById('btn-guardar');
const btn_resena = document.getElementById('btn-resena');
const detalles_libro = document.querySelector('.detalles-libro');
const btn_eliminar = document.getElementById('btn-eliminar');

// Obtener secciones de ratings, reseñas y recomendaciones
const seccion_ratings = document.getElementById('seccion-ratings');
const seccion_resenas = document.getElementById('seccion-resenas');
const seccion_recomendaciones = document.getElementById('seccion-recomendaciones');

function mostrar(elemento){
    if(elemento) elemento.classList.remove('d-none');
}
function ocultar(elemento){
    if(elemento) elemento.classList.add('d-none');
}

btn_editar.addEventListener("click", ()=>{
    if(form_editar.classList.contains('d-none'))
    {
        mostrar(form_editar);
        mostrar(btn_guardar);
        ocultar(detalles_libro);
        ocultar(btn_resena);
        ocultar(btn_eliminar);
        
        // Ocultar secciones de ratings, reseñas y recomendaciones
        ocultar(seccion_ratings);
        ocultar(seccion_resenas);
        ocultar(seccion_recomendaciones);
        
        btn_texto.textContent = 'Cancelar';
        btn_editar.querySelector('i').className = 'bi bi-x-circle';
        btn_editar.classList.remove('btn-outline-primary');
        btn_editar.classList.add('btn-outline-danger');
        
    }
    else
    {
        ocultar(form_editar);
        ocultar(btn_guardar);
        mostrar(detalles_libro);
        mostrar(btn_resena);
        mostrar(btn_eliminar);
        
        // Mostrar secciones de ratings, reseñas y recomendaciones
        mostrar(seccion_ratings);
        mostrar(seccion_resenas);
        mostrar(seccion_recomendaciones);
        
        btn_texto.textContent = 'Editar';
        btn_editar.querySelector('i').className = "bi bi-pencil-square";
        btn_editar.classList.remove('btn-outline-danger');
        btn_editar.classList.add('btn-outline-primary');

        //*Regresar valores originales cuando se cancela
        campos.forEach((campo, i) => {
            campo.value = original[i];
        });

        portadainput.value = '';
        btn_guardar.setAttribute('disabled', '');
        motivo.setAttribute('disabled', '');
    }
})

const editables = document.querySelectorAll('.editable');
const motivo = document.getElementById('motivo-editar-libro');
let original = []
let campos = []

editables.forEach((input)=>{
    input.classList.add('border-warning')
    campos.push(input);    
})

// Función para verificar si hay cambios
function verificarCambios() {
    let hayCambios = false;
    
    for(let i = 0; i < campos.length; i++){
        if(campos[i].value != original[i]){
            hayCambios = true;
            break;
        }
    }
    
    if(portadainput.value != ""){
        hayCambios = true;
    }
    
    if(hayCambios){
        btn_guardar.removeAttribute('disabled');
        motivo.removeAttribute('disabled');
    } else {
        btn_guardar.setAttribute('disabled', "");
        motivo.setAttribute('disabled', "");
    }
}

for(let i = 0; i < editables.length; i++){
    original.push(campos[i].value);
    // Agregar listeners para inputs de texto, número y select
    if(campos[i].tagName === 'SELECT'){
        campos[i].addEventListener("change", verificarCambios);
    } else {
        campos[i].addEventListener("keyup", verificarCambios);
        campos[i].addEventListener("change", verificarCambios);
    }
}

const portadainput = document.getElementById("portadainput");
portadainput.addEventListener("change", verificarCambios);

// Contador de caracteres para el textarea de reseña
const opinionTextarea = document.getElementById("opinion");
const charCountElement = document.getElementById("charCount");

if (opinionTextarea && charCountElement) {
    // Actualizar contador mientras escribe
    opinionTextarea.addEventListener("input", function() {
        const currentLength = this.value.length;
        const maxLength = this.getAttribute("maxlength");
        
        charCountElement.textContent = currentLength;
        
        // Cambiar color según el límite
        if (currentLength >= maxLength) {
            charCountElement.parentElement.classList.remove('text-muted');
            charCountElement.parentElement.classList.add('text-danger', 'fw-bold');
        } else if (currentLength >= maxLength * 0.9) {
            charCountElement.parentElement.classList.remove('text-muted');
            charCountElement.parentElement.classList.add('text-warning', 'fw-bold');
        } else {
            charCountElement.parentElement.classList.remove('text-danger', 'text-warning', 'fw-bold');
            charCountElement.parentElement.classList.add('text-muted');
        }
    });
    
    // Resetear contador cuando se cierra el modal
    const modalResena = document.getElementById('modalResena');
    if (modalResena) {
        modalResena.addEventListener('hidden.bs.modal', function () {
            opinionTextarea.value = '';
            charCountElement.textContent = '0';
            charCountElement.parentElement.classList.remove('text-danger', 'text-warning', 'fw-bold');
            charCountElement.parentElement.classList.add('text-muted');
        });
    }
}

// Inicializar contadores de caracteres para los inputs de motivo
document.addEventListener('DOMContentLoaded', function() {
    // Contador para eliminar libro
    inicializarContador('motivo-eliminar-libro', 'contador-eliminar-libro', 200);
    
    // Contador para editar libro
    inicializarContador('motivo-editar-libro', 'contador-editar-libro', 200);
    
    // Contadores para eliminar opiniones (pueden ser múltiples)
    const motivosOpiniones = document.querySelectorAll('[id^="motivo-eliminar-opinion-"]');
    motivosOpiniones.forEach(input => {
        const opinionId = input.id.replace('motivo-eliminar-opinion-', '');
        inicializarContador(`motivo-eliminar-opinion-${opinionId}`, `contador-eliminar-opinion-${opinionId}`, 200);
    });
});