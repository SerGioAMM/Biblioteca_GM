/*
const caja_sugerencias = document.querySelector('.ul-contenedor-sugerencias');
let filtro = document.querySelector('#filtro-busqueda');
let filtro_secciones = document.querySelector('#categorias');
let inputActivo = null;


function moverSugerencias(input) {
  caja_sugerencias.style.top = (input.offsetTop) + 'px';
  caja_sugerencias.style.left = input.offsetLeft + 'px';
  caja_sugerencias.style.width = (input.offsetWidth - 15 ) + 'px';
}

function mostrar_sugerencias(lista) {
  if (lista.length === 0) {
    caja_sugerencias.classList.remove('activar');
    caja_sugerencias.innerHTML = '';
  } else {
    caja_sugerencias.innerHTML = lista.join('');
    caja_sugerencias.classList.add('activar');
  }
}

function seleccionar_Sugerencia(sug) {
  if (inputActivo) inputActivo.value = sug;
  caja_sugerencias.classList.remove('activar');
  caja_sugerencias.innerHTML = '';
}

document.querySelectorAll('.input-lugar, .input-editorial, .buscar-libro, .buscar-libro-prestamo, .buscar-prestamo, .buscar-usuario, .buscar-prestamo-eliminado, .buscar-libro-eliminado').forEach(input => {
  input.addEventListener('focus', () => {
    inputActivo = input;
    moverSugerencias(input);
    caja_sugerencias.classList.remove('activar');
    caja_sugerencias.innerHTML = '';
  });

  input.addEventListener('keyup', (e) => {
    const texto = e.target.value.toLowerCase();
    if (!texto) {
      caja_sugerencias.innerHTML = '';
      caja_sugerencias.classList.remove('activar');
      return;
    }

    // Detectar el input
    let endpoint = '';
    if (input.classList.contains('input-lugar')) {
      endpoint = '/sugerencias-lugares';
    } else if (input.classList.contains('input-editorial')) {
      endpoint = '/sugerencias-editoriales';
    } 
    else if (input.classList.contains('buscar-libro')){
        if(filtro.value == "Titulo"){
          endpoint = '/sugerencias-libros';
        }else if(filtro.value == "Autor"){
          endpoint = '/sugerencias-autores';
        }
      }
    else if(input.classList.contains('buscar-libro-prestamo')){
      endpoint = '/sugerencias-libros-prestamos';
    }
    else if(input.classList.contains('buscar-prestamo')){
      if(filtro.value == "Titulo"){
        endpoint = '/sugerencias-prestamo';
      }else if(filtro.value == "Lector"){
        endpoint = '/sugerencias-lectores';
      }
    }
    else if(input.classList.contains('buscar-usuario')){
      endpoint = '/sugerencias-usuarios';
    }
    else if(input.classList.contains('buscar-prestamo-eliminado')){
      if(filtro.value == "Titulo"){
        endpoint = '/sugerencias-prestamo-eliminado-libro';
      }else if(filtro.value == "Administrador"){
        endpoint = '/sugerencias-prestamo-eliminado-administradores';
      }
    }
    else if(input.classList.contains('buscar-libro-eliminado')){
      if(filtro.value == "Titulo"){
        endpoint = '/sugerencias-libro-eliminado';
      }else if(filtro.value == "Administrador"){
        endpoint = '/sugerencias-libro-eliminado-administradores';
      }
    }

    fetch(endpoint)
      .then(r => r.json())
      .then(data => {
        const sugerencias = data
          .filter(d => d.toLowerCase().includes(texto))
          .map(s => `<li onclick="seleccionar_Sugerencia('${s}')">${s}</li>`);

        mostrar_sugerencias(sugerencias);
      });
  });
});

document.addEventListener('click', function(event) {
  const clicDentroCaja = caja_sugerencias.contains(event.target);
  const clicDentroInput = inputActivo && inputActivo.contains(event.target);

  if (!clicDentroCaja && !clicDentroInput) {
    caja_sugerencias.classList.remove('activar');
    caja_sugerencias.innerHTML = '';
  }
});*/



document.addEventListener("DOMContentLoaded", function() {
  let select = new TomSelect("#cuadro-busqueda", {
    maxItems: 1,
    valueField: 'value',
    labelField: 'text',
    searchField: 'text',

    load: function(query, callback) {
      if (!query.length) return callback();  // si no hay texto, no buscar
      
      let sugerencia = "";
      if((document.getElementById("form-busqueda")) == null){
        sugerencia = '/'+(document.getElementById("cuadro-busqueda").classList[0]);
      }else{
        sugerencia = document.getElementById("form-busqueda").getAttribute("action");
      }

      let filtro = "";
      if(document.getElementById("filtro-busqueda") == null){
        filtro = "";
      }
      else{
        filtro = document.getElementById("filtro-busqueda").value;
      }

      let categoria="";
      if(document.getElementById("filtro-categorias")){
        categoria = '/' + (document.getElementById("filtro-categorias").value);
      }
      
      console.log("Sugerencia: "+sugerencia);
      console.log("Filtro: "+filtro);
      console.log("Categoria: "+categoria);
      console.log('FETCH: /sugerencias' + sugerencia + filtro + categoria);

      select.clearOptions();

      fetch('/sugerencias' + sugerencia + filtro + categoria)
      .then(res => res.json())
      .then(data => {
          // transformar la lista en objetos { value, text }
          const resultados = data
          .filter(d => d.toLowerCase().includes(query.toLowerCase()))
          .map(d => ({ value: d, text: d }));
          callback(resultados);
        })
        .catch(() => callback());
    },
    dropdownParent: 'body',
    render:{
      no_results: function() {
        return '<div class="no-results text-muted">No se encontraron resultados.</div>';
      }
    }
  });
});



if(document.getElementById("cuadro-busqueda2")){
document.addEventListener("DOMContentLoaded", function() {
  let select = new TomSelect("#cuadro-busqueda2", {
    maxItems: 1,
    valueField: 'value',
    labelField: 'text',
    searchField: 'text',

    load: function(query, callback) {
      if (!query.length) return callback();  // si no hay texto, no buscar
      
      let sugerencia = "";
      if((document.getElementById("form-busqueda")) == null){
        sugerencia = '/'+(document.getElementById("cuadro-busqueda2").classList[0]);
      }else{
        sugerencia = document.getElementById("form-busqueda").getAttribute("action");
      }

      let filtro = "";
      if(document.getElementById("filtro-busqueda") == null){
        filtro = "";
      }
      else{
        filtro = document.getElementById("filtro-busqueda").value;
      }

      let categoria="";
      if(document.getElementById("filtro-categorias")){
        categoria = '/' + (document.getElementById("filtro-categorias").value);
      }
      
      console.log("Sugerencia: "+sugerencia);
      console.log("Filtro: "+filtro);
      console.log("Categoria: "+categoria);
      console.log('FETCH: /sugerencias' + sugerencia + filtro + categoria);

      select.clearOptions();

      fetch('/sugerencias' + sugerencia + filtro + categoria)
      .then(res => res.json())
      .then(data => {
          // transformar la lista en objetos { value, text }
          const resultados = data
          .filter(d => d.toLowerCase().includes(query.toLowerCase()))
          .map(d => ({ value: d, text: d }));
          callback(resultados);
        })
        .catch(() => callback());
    },
    dropdownParent: 'body',
    render:{
      no_results: function() {
        return '<div class="no-results text-muted">No se encontraron resultados.</div>';
      }
    }
  });
});
}
