// Script para filtros de visitantes
document.addEventListener('DOMContentLoaded', function() {
    // Validación de rango de fechas
    const fechaInicio = document.querySelector('input[name="fecha_inicio"]');
    const fechaFin = document.querySelector('input[name="fecha_fin"]');
    const form = document.querySelector('#form-busqueda');

    if (form) {
        form.addEventListener('submit', function(e) {
            if (fechaInicio.value && fechaFin.value) {
                if (fechaInicio.value > fechaFin.value) {
                    e.preventDefault();
                    alert('La fecha de inicio no puede ser mayor que la fecha final.');
                    return false;
                }
            }
        });
    }

    // Funcionalidad adicional para filtros de visitantes puede ir aquí
    // Por ejemplo: filtros dinámicos, autocompletado, etc.
});
