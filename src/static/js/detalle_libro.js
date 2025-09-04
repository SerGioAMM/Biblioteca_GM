const form_editar = document.getElementById('form-editar-libro');
const btn_editar = document.getElementById('btn-editar');
const btn_texto = btn_editar.querySelector('span');
const btn_guardar = document.getElementById('btn-guardar');
const btn_resena = document.getElementById('btn-resena');
const detalles_libro = document.querySelector('.detalles-libro');

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
        btn_texto.textContent = 'Editar';
        btn_editar.querySelector('i').className = "bi bi-pencil-square";
        btn_editar.classList.remove('btn-outline-danger');
        btn_editar.classList.add('btn-outline-primary');
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

for(let i=0;i<editables.length;i++){
    original.push(campos[i].value);
    campos[i].addEventListener("keyup",()=>{
        if(campos[i].value != original[i]){
            btn_guardar.removeAttribute('disabled');
            motivo.removeAttribute('disabled');
        }
        else{
            btn_guardar.setAttribute('disabled',"");
            motivo.setAttribute('disabled',"");
        }
        
    })
}




