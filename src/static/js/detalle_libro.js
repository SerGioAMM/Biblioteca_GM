const form_editar = document.getElementById('form-editar-libro');
const btn_editar = document.getElementById('btn-editar');
const btn_texto = btn_editar.querySelector('span');
const btn_guardar = document.getElementById('btn-guardar');
const btn_resena = document.getElementById('btn-resena');
const detalles_libro = document.querySelector('.detalles-libro');
const btn_eliminar = document.getElementById('btn-eliminar');

function mostrar(elemento){
    elemento.classList.remove('d-none');
}
function ocultar(elemento){
    elemento.classList.add('d-none')
}

btn_editar.addEventListener("click", ()=>{
    if(form_editar.classList.contains('d-none'))
    {
        mostrar(form_editar);
        mostrar(btn_guardar);
        ocultar(detalles_libro);
        ocultar(btn_resena);
        ocultar(btn_eliminar);
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
const motivo = document.getElementById('motivo');
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
