const form_editar = document.getElementById('form-editar-libro');
const btn_editar = document.getElementById('btn-editar');
const detalles_libro = document.getElementById('detalles-libro');


btn_editar.addEventListener("click", (e)=>{
    form_editar.classList.remove('d-none');
})