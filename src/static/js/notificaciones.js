// JavaScript para manejar notificaciones en el navbar
document.addEventListener('DOMContentLoaded', function() {
    const dropdownNotificaciones = document.getElementById('notificaciones-dropdown');
    const badgeNotificaciones = document.getElementById('badge-notificaciones');
    const contenedorNotificaciones = document.getElementById('notificaciones-container');
    const btnMarcarLeidasNavbar = document.getElementById('btn-marcar-leidas-navbar');
    
    // Cargar notificaciones al hacer clic en el dropdown
    if (dropdownNotificaciones) {
        dropdownNotificaciones.addEventListener('click', function() {
            cargarNotificaciones();
        });
    }
    
    // Marcar notificaciones como leídas desde navbar
    if (btnMarcarLeidasNavbar) {
        btnMarcarLeidasNavbar.addEventListener('click', function() {
            marcarNotificacionesLeidas();
        });
    }
    
    // Cargar notificaciones inicialmente
    cargarNotificaciones();
    
    // Actualizar notificaciones cada 30 segundos
    setInterval(cargarNotificaciones, 30000);
    
    function cargarNotificaciones() {
        fetch('/api/notificaciones')
            .then(response => response.json())
            .then(data => {
                if (data.success) {
                    actualizarBadge(data.no_vistas);
                    mostrarNotificaciones(data.notificaciones, data.no_vistas);
                }
            })
            .catch(error => {
                console.error('Error al cargar notificaciones:', error);
            });
    }
    
    function actualizarBadge(cantidad) {
        if (cantidad > 0) {
            badgeNotificaciones.classList.remove('d-none');
        } else {
            badgeNotificaciones.classList.add('d-none');
        }
    }
    
    function mostrarNotificaciones(notificaciones, noVistas) {
        if (notificaciones.length === 0) {
            contenedorNotificaciones.innerHTML = '<li><span class="dropdown-item-text text-muted small">No tienes notificaciones</span></li>';
            btnMarcarLeidasNavbar.classList.add('d-none');
            return;
        }
        
        let html = '';
        notificaciones.forEach(notificacion => {
            const iconoVisto = notificacion.visto ? 
                '<i class="bi bi-circle text-muted me-2" style="font-size: 0.5rem;"></i>' : 
                '<i class="bi bi-circle-fill text-primary me-2" style="font-size: 0.5rem;"></i>';
            
            const claseVisto = notificacion.visto ? '' : 'fw-bold';
            
            html += `
                <li>
                    <div class="dropdown-item-text ${claseVisto} small" style="white-space: normal; max-width: 320px; font-size: 0.875rem; line-height: 1.25;">
                        <div class="d-flex align-items-start">
                            ${iconoVisto}
                            <div class="flex-grow-1">
                                <div style="font-size: 0.875rem;">${notificacion.detalle}</div>
                                <small class="text-muted" style="font-size: 0.75rem;">${notificacion.fecha_formateada}</small>
                            </div>
                        </div>
                    </div>
                </li>
            `;
        });
        
        contenedorNotificaciones.innerHTML = html;
        
        // Mostrar/ocultar botón de marcar como leídas
        if (noVistas > 0) {
            btnMarcarLeidasNavbar.classList.remove('d-none');
        } else {
            btnMarcarLeidasNavbar.classList.add('d-none');
        }
    }
    
    function marcarNotificacionesLeidas() {
        fetch('/marcar_notificaciones_leidas', {
            method: 'POST',
            headers: {
                'Content-Type': 'application/json',
            }
        })
        .then(response => response.json())
        .then(data => {
            if (data.success) {
                cargarNotificaciones(); // Recargar notificaciones
            }
        })
        .catch(error => {
            console.error('Error al marcar notificaciones como leídas:', error);
        });
    }
});