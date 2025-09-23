document.addEventListener("DOMContentLoaded", function() {
  function initTomSelect(selector) {
    let select = new TomSelect(selector, {
      maxItems: 1,
      valueField: 'value',
      labelField: 'text',
      searchField: 'text',
      
      // NUEVO: Habilita creación de opciones con texto libre 
      create: function(input) {
        return {
          value: input.trim(),
          text: input.trim()
        };
      },

      load: function(query, callback) {
        if (!query.length) return callback();  // si no hay texto, no buscar
        
        let sugerencia = "";
        if (document.getElementById("form-busqueda") == null) {
          sugerencia = '/' + (document.getElementById(selector.replace('#', '')).classList[0]);
        } else {
          sugerencia = document.getElementById("form-busqueda").getAttribute("action");
        }

        let filtro = "";
        if (document.getElementById("filtro-busqueda") == null) {
          filtro = "";
        } else {
          filtro = document.getElementById("filtro-busqueda").value;
        }

        let categoria = "";
        if (document.getElementById("filtro-categorias")) {
          categoria = '/' + (document.getElementById("filtro-categorias").value);
        }
        
        console.log("Sugerencia: " + sugerencia);
        console.log("Filtro: " + filtro);
        console.log("Categoria: " + categoria);
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
      render: {
        no_results: function() {
          return '<div class="no-results text-muted">No se encontraron resultados.</div>';
        }
      }
    });

    select.on('keydown', function(e) {
      if (e.keyCode === 13 || e.key === 'Enter') {  
        e.preventDefault(); 
        e.stopPropagation(); 

        const searchTerm = this.control_input.value.trim(); 
        if (searchTerm) {
          this.createItem(searchTerm); 
          this.close();
          
          const form = document.getElementById("form-busqueda");
          if (form) {
            form.submit();
          }
        } else {
          return false;
        }
      }
    });

    const form = document.getElementById("form-busqueda");
    if (form) {
      form.addEventListener('submit', function(e) {
        const searchTerm = select.control_input.value.trim();
        if (searchTerm) {
          // Asegura que el input original tenga el valor (por si no usó Enter)
          const originalInput = document.querySelector(selector);
          originalInput.value = searchTerm;
        } 
      });
    }

    return select;
  }

  // Inicializa para el primer input
  initTomSelect("#cuadro-busqueda");

  // Inicializa para el segundo input si existe
  if (document.getElementById("cuadro-busqueda2")) {
    initTomSelect("#cuadro-busqueda2");
  }
});