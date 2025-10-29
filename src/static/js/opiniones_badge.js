// Script para mostrar badge de opiniones pendientes en el navbar
document.addEventListener('DOMContentLoaded', function() {
    const badgeOpiniones = document.getElementById('badge-opiniones');
    
    if (badgeOpiniones) {
        // Hacer petición al API para obtener el conteo
        fetch('/api/opiniones_pendientes_count')
            .then(response => response.json())
            .then(data => {
                if (data.count > 0) {
                    // Mostrar badge si hay opiniones pendientes
                    badgeOpiniones.classList.remove('d-none');
                }
            })
            .catch(error => {
                console.error('Error al obtener opiniones pendientes:', error);
            });
    }
});
