/* ========================================
   SISTEMA DE ALERTAS DINÁMICO
   ======================================== */

// Crear contenedor de alertas si no existe
function createAlertContainer() {
    let container = document.querySelector('.alert-container');
    if (!container) {
        container = document.createElement('div');
        container.className = 'alert-container';
        document.body.appendChild(container);
    }
    return container;
}

// Función para mostrar alertas con Bootstrap 5
function showAlert(message, type = 'info', duration = 4000, customIcon = null) {
    console.log('🔔 showAlert llamado:', {message, type, duration, customIcon}); // DEBUG
    
    const container = createAlertContainer();
    console.log('📦 Contenedor:', container); // DEBUG
    
    // Determinar icono según el tipo - MEJORADO con más opciones
    const icons = {
        'success': 'bi-check-circle-fill',
        'danger': 'bi-x-circle-fill',
        'warning': 'bi-exclamation-triangle-fill',
        'info': 'bi-info-circle-fill',
        // Iconos personalizados para acciones específicas
        'delete': 'bi-trash-fill',
        'reject': 'bi-x-octagon-fill',
        'create': 'bi-plus-circle-fill',
        'edit': 'bi-pencil-square',
        'return': 'bi-arrow-return-left'
    };
    
    // Usar icono personalizado si se proporciona, sino usar el del tipo
    const icon = customIcon || icons[type] || icons['info'];
    
    // Crear elemento de alerta
    const alertId = 'alert-' + Date.now();
    const progressClass = duration === 10000 ? 'duration-10s' : '';
    const alertHTML = `
        <div id="${alertId}" class="alert alert-${type === 'delete' || type === 'reject' ? 'danger' : type === 'create' ? 'warning' : type === 'return' ? 'info' : type} alert-dismissible fade show alert-animated" role="alert">
            <i class="bi ${icon} alert-icon"></i>
            <strong>${message}</strong>
            <button type="button" class="btn-close" data-bs-dismiss="alert" aria-label="Close"></button>
            <div class="alert-progress ${progressClass}"></div>
        </div>
    `;
    
    container.insertAdjacentHTML('beforeend', alertHTML);
    
    const alertElement = document.getElementById(alertId);
    console.log('✅ Alerta creada:', alertElement); // DEBUG
    
    // Auto-cerrar después del duration
    setTimeout(() => {
        hideAlert(alertElement);
    }, duration);
    
    // Permitir cerrar manualmente
    const closeButton = alertElement.querySelector('.btn-close');
    closeButton.addEventListener('click', () => {
        hideAlert(alertElement);
    });
}

// Función para ocultar alerta con animación
function hideAlert(alertElement) {
    if (!alertElement) return;
    
    alertElement.classList.add('alert-hiding');
    
    setTimeout(() => {
        alertElement.remove();
    }, 400);
}

// Función para convertir alertas antiguas a nuevas
function convertLegacyAlerts() {
    // Buscar todas las alertas con data-attributes
    const allAlerts = document.querySelectorAll('[data-alert-message]');
    allAlerts.forEach(alert => {
        const message = alert.getAttribute('data-alert-message');
        let type = alert.getAttribute('data-alert-type') || 'info';
        let customIcon = alert.getAttribute('data-alert-icon') || null;
        let duration = 4000; // Duración por defecto
        
        // Detectar tipo de acción basándose en el mensaje para usar iconos específicos
        if (message && message.trim()) {
            const messageLower = message.toLowerCase();
            
            // ========== ACCIONES EXITOSAS (VERDE) ==========
            // Eliminaciones exitosas
            if (messageLower.includes('eliminad') && messageLower.includes('exitosa')) {
                type = 'success';
                customIcon = 'bi-trash-fill';
            }
            // Eliminaciones en general (cuando sea exitosa)
            else if ((messageLower.includes('eliminad') || messageLower.includes('borrad')) && 
                     !messageLower.includes('prestado') && !messageLower.includes('error')) {
                type = 'success';
                customIcon = 'bi-trash-fill';
            }
            // Rechazo de reseñas (operación exitosa)
            else if (messageLower.includes('rechazad')) {
                type = 'success';
                customIcon = 'bi-x-octagon-fill';
            }
            // Desactivación de usuarios
            else if (messageLower.includes('desactivad')) {
                type = 'success';
                customIcon = 'bi-person-x-fill';
            }
            // Reseña enviada para revisión
            else if (messageLower.includes('reseña') && (messageLower.includes('enviad') || messageLower.includes('revisión'))) {
                type = 'success';
                customIcon = 'bi-check-circle-fill';
            }
            // Acciones de aceptación/aprobación
            else if (messageLower.includes('aceptad') || messageLower.includes('aprobad')) {
                type = 'success';
                customIcon = 'bi-check-circle-fill';
            }
            // Devolución exitosa
            else if (messageLower.includes('devuel') || messageLower.includes('retornad')) {
                type = 'success';
                customIcon = 'bi-arrow-return-left';
            }
            // Registro exitoso
            else if (messageLower.includes('registrad') && messageLower.includes('exitosa')) {
                type = 'success';
                customIcon = 'bi-plus-circle-fill';
            }
            
            // ========== ERRORES (ROJO) ==========
            // Login erróneo / Datos incorrectos
            if (messageLower.includes('datos incorrectos') || messageLower.includes('datos erroneos') || 
                messageLower.includes('usuario inactivo') || messageLower.includes('contacte al administrador')) {
                type = 'danger';
                customIcon = 'bi-x-circle-fill';
            }
            // Libro prestado no se puede eliminar
            else if (messageLower.includes('prestado') && (messageLower.includes('eliminar') || messageLower.includes('error'))) {
                type = 'danger';
                customIcon = 'bi-x-circle-fill';
            }
            // Bloqueo de usuario (AMARILLO - 10 segundos)
            else if (messageLower.includes('bloqu') || messageLower.includes('intente de nuevo en') || 
                     messageLower.includes('demasiados intentos')) {
                type = 'warning'; // Amarillo para bloqueos
                customIcon = 'bi-shield-exclamation';
                duration = 10000; // 10 segundos
            }
            // Errores generales
            else if (messageLower.includes('error') || messageLower.includes('inválid')) {
                type = 'danger';
                customIcon = 'bi-x-circle-fill';
            }
            
            // ========== OTRAS ACCIONES ==========
            // Creación/registro general
            else if (messageLower.includes('registrad') || messageLower.includes('cread') || messageLower.includes('agregad')) {
                type = 'success';
                customIcon = 'bi-plus-circle-fill';
            }
            // Edición
            else if (messageLower.includes('modificad') || messageLower.includes('editad') || messageLower.includes('actualizad')) {
                type = 'info';
                customIcon = 'bi-pencil-square';
            }
            
            showAlert(message.trim(), type, duration, customIcon);
        }
        alert.remove();
    });
    
    // FALLBACK: Buscar alertas antiguas sin data-attributes
    // Buscar alertas antiguas de error
    const errorAlerts = document.querySelectorAll('.error-eliminacion:not([data-alert-message])');
    errorAlerts.forEach(alert => {
        const message = alert.querySelector('h4 strong')?.textContent || alert.textContent;
        if (message.trim()) {
            showAlert(message.trim(), 'danger', 4000, 'bi-x-circle-fill');
        }
        alert.remove();
    });
    
    // Buscar alertas antiguas de éxito
    const successAlerts = document.querySelectorAll('.exito-ingreso:not([data-alert-message])');
    successAlerts.forEach(alert => {
        const message = alert.querySelector('h4 strong')?.textContent || alert.textContent;
        if (message.trim()) {
            showAlert(message.trim(), 'success', 4000, 'bi-check-circle-fill');
        }
        alert.remove();
    });
    
    // Buscar alertas antiguas de devuelto
    const infoAlerts = document.querySelectorAll('.devuelto:not([data-alert-message])');
    infoAlerts.forEach(alert => {
        const message = alert.querySelector('h4 strong')?.textContent || alert.textContent;
        if (message.trim()) {
            showAlert(message.trim(), 'info', 4000, 'bi-arrow-return-left');
        }
        alert.remove();
    });
}

// Ejecutar conversión cuando el DOM esté listo
document.addEventListener('DOMContentLoaded', () => {
    console.log('🚀 Sistema de alertas inicializado'); // DEBUG
    convertLegacyAlerts();
});

// También ejecutar si el DOM ya está cargado
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', () => {
        console.log('🚀 Sistema de alertas inicializado (DOMContentLoaded)'); // DEBUG
        convertLegacyAlerts();
    });
} else {
    console.log('🚀 Sistema de alertas inicializado (DOM ya cargado)'); // DEBUG
    convertLegacyAlerts();
}

// Exportar funciones para uso global
window.showAlert = showAlert;
window.hideAlert = hideAlert;
