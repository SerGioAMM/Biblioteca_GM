/* ========================================
   SISTEMA DE TIMEOUT DE SESIÓN
   Detecta inactividad y redirige al login
   ======================================== */

(function() {
    'use strict';
    
    // Solo ejecutar en páginas que requieren autenticación
    // Verificar si hay un usuario en sesión (si no hay navbar de usuario, no ejecutar)
    const navbarUser = document.querySelector('.navbar .nav-item.dropdown a[href="#"]:has(i.bi-person-circle)');
    if (!navbarUser) {
        // No hay usuario logueado, no hacer nada
        return;
    }
    
    // Configuración
    const INACTIVITY_TIMEOUT = 3 * 60 * 1000; // 3 minutos en milisegundos
    const CHECK_INTERVAL = 10 * 1000; // Verificar cada 10 segundos
    const WARNING_TIME = 1 * 60 * 1000; // Advertir 1 minuto antes
    
    let lastActivity = Date.now();
    let warningShown = false;
    let checkInterval;
    let warningTimeout;
    
    // Eventos que cuentan como actividad
    const activityEvents = [
        'mousedown', 
        'mousemove', 
        'keypress', 
        'scroll', 
        'touchstart',
        'click'
    ];
    
    // Actualizar timestamp de última actividad
    function updateActivity() {
        lastActivity = Date.now();
        warningShown = false;
        
        // Limpiar advertencia si existe
        clearTimeout(warningTimeout);
        hideWarningModal();
    }
    
    // Función para mostrar advertencia antes de expirar
    function showWarningModal() {
        if (warningShown) return;
        warningShown = true;
        
        // Crear modal de advertencia si no existe
        let modal = document.getElementById('session-warning-modal');
        if (!modal) {
            const modalHTML = `
                <div class="modal fade" id="session-warning-modal" data-bs-backdrop="static" data-bs-keyboard="false" tabindex="-1">
                    <div class="modal-dialog modal-dialog-centered">
                        <div class="modal-content">
                            <div class="modal-header bg-warning text-dark">
                                <h5 class="modal-title">
                                    <i class="bi bi-exclamation-triangle-fill"></i> Sesión por expirar
                                </h5>
                            </div>
                            <div class="modal-body">
                                <p class="mb-0">Tu sesión expirará en <strong id="countdown-timer">1:00</strong> por inactividad.</p>
                                <p class="mb-0 mt-2">Mueve el puntero del ratón para mantener la sesión activa.</p>
                            </div>
                        </div>
                    </div>
                </div>
            `;
            document.body.insertAdjacentHTML('beforeend', modalHTML);
            modal = document.getElementById('session-warning-modal');
        }
        
        // Mostrar modal
        const bsModal = new bootstrap.Modal(modal);
        bsModal.show();
        
        // Iniciar countdown
        startCountdown();
    }
    
    // Ocultar modal de advertencia
    function hideWarningModal() {
        const modal = document.getElementById('session-warning-modal');
        if (modal) {
            const bsModal = bootstrap.Modal.getInstance(modal);
            if (bsModal) {
                bsModal.hide();
            }
        }
    }
    
    // Countdown en el modal
    function startCountdown() {
        const countdownElement = document.getElementById('countdown-timer');
        if (!countdownElement) return;
        
        let remainingSeconds = 60; // 1 minuto
        
        const countdownInterval = setInterval(() => {
            remainingSeconds--;
            
            const minutes = Math.floor(remainingSeconds / 60);
            const seconds = remainingSeconds % 60;
            countdownElement.textContent = `${minutes}:${seconds.toString().padStart(2, '0')}`;
            if (remainingSeconds <= 0) {
                clearInterval(countdownInterval);
                // Redirigir a login
                window.location.href = '/login?alerta=Sesión expirada por inactividad';
            }
        }, 1000);
        
        // Guardar intervalo para poder limpiarlo
        window.sessionTimeout = window.sessionTimeout || {};
        window.sessionTimeout.countdownInterval = countdownInterval;
    }
    
    // Extender sesión (llamado desde el botón del modal)
    function extendSession() {
        // Limpiar countdown
        if (window.sessionTimeout && window.sessionTimeout.countdownInterval) {
            clearInterval(window.sessionTimeout.countdownInterval);
        }
        
        // Actualizar actividad
        updateActivity();
        
        // Ocultar modal
        hideWarningModal();
        
        // Mostrar confirmación
        if (window.showAlert) {
            window.showAlert('Sesión extendida exitosamente', 'success', 3000);
        }
    }
    
    // Verificar inactividad periódicamente
    function checkInactivity() {
        const now = Date.now();
        const inactiveTime = now - lastActivity;
        console.log(`⏱️ Tiempo inactivo: ${Math.floor(inactiveTime / 1000)} segundos`); // DEBUG
        // Si quedan 1 minuto o menos, mostrar advertencia
        if (inactiveTime >= (INACTIVITY_TIMEOUT - WARNING_TIME) && !warningShown) {
            showWarningModal();
        }
        
        // Si se superó el tiempo límite, cerrar sesión
        if (inactiveTime >= INACTIVITY_TIMEOUT) {
            clearInterval(checkInterval);
            window.location.href = '/login?alerta=Sesión expirada por inactividad';
        }
    }
    
    // Registrar eventos de actividad
    activityEvents.forEach(event => {
        document.addEventListener(event, updateActivity, true);
    });
    
    // Iniciar verificación periódica
    checkInterval = setInterval(checkInactivity, CHECK_INTERVAL);
    
    // Exportar funciones para uso global
    window.sessionTimeout = {
        extendSession: extendSession,
        updateActivity: updateActivity
    };
    
})();
