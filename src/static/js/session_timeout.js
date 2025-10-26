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
    const INACTIVITY_TIMEOUT = 3 * 60 * 1000; // 3 minutos en milisegundos //! Cambiar a 15 * 60 * 1000 para 15 minutos
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
        hideWarningAlert();
        
        // Limpiar countdown si existe
        if (window.sessionTimeout && window.sessionTimeout.countdownInterval) {
            clearInterval(window.sessionTimeout.countdownInterval);
        }
    }
    
    // Función para mostrar alerta de advertencia con diseño del sistema de alertas
    function showWarningAlert() {
        if (warningShown) return;
        warningShown = true;
        
        // Crear alerta con el mismo diseño que el sistema de alertas
        createSessionAlert();
    }
    
    // Función para crear alerta con diseño del sistema de alertas
    function createSessionAlert() {
        // Crear contenedor de alertas si no existe (igual que alertas.js)
        let container = document.querySelector('.alert-container');
        if (!container) {
            container = document.createElement('div');
            container.className = 'alert-container';
            container.style.cssText = `
                position: fixed;
                top: 80px;
                right: 20px;
                width: 350px;
                max-width: calc(100vw - 40px);
                pointer-events: none;
                z-index: 9999;
            `;
            document.body.appendChild(container);
        }
        
        // Crear elemento de alerta con el mismo diseño
        const alertId = 'session-warning-alert-' + Date.now();
        const alertHTML = `
            <div id="${alertId}" class="alert alert-warning alert-dismissible fade show" role="alert" 
                 style="pointer-events: auto; animation: slideInRight 0.5s cubic-bezier(0.68, -0.55, 0.265, 1.55); 
                        box-shadow: 0 4px 12px rgba(0, 0, 0, 0.15); border-left: 4px solid #ffc107; margin-bottom: 15px;">
                <i class="bi bi-exclamation-triangle-fill" style="font-size: 1.25rem; margin-right: 10px; vertical-align: middle;"></i>
                <strong>Sesión por expirar en <span id="session-countdown" class="fw-bold text-danger">1:00</span></strong>
                <div style="position: absolute; bottom: 0; left: 0; height: 3px; background-color: rgba(0, 0, 0, 0.2); 
                           animation: progressBar 60s linear forwards; width: 100%;"></div>
            </div>
        `;
        
        container.insertAdjacentHTML('beforeend', alertHTML);
        
        // Agregar estilos de animación si no existen
        if (!document.getElementById('session-alert-styles')) {
            const styles = document.createElement('style');
            styles.id = 'session-alert-styles';
            styles.textContent = `
                @keyframes slideInRight {
                    from { transform: translateX(120%); opacity: 0; }
                    to { transform: translateX(0); opacity: 1; }
                }
                @keyframes slideOutRight {
                    from { transform: translateX(0); opacity: 1; }
                    to { transform: translateX(120%); opacity: 0; }
                }
                @keyframes progressBar {
                    from { width: 100%; }
                    to { width: 0%; }
                }
            `;
            document.head.appendChild(styles);
        }
        
        // Iniciar countdown después de un breve delay
        setTimeout(() => {
            startCountdown();
        }, 100);
        
        // Auto-remover después de 60 segundos (por si acaso)
        setTimeout(() => {
            const alertElement = document.getElementById(alertId);
            if (alertElement) {
                alertElement.style.animation = 'slideOutRight 0.4s ease-out forwards';
                setTimeout(() => alertElement.remove(), 400);
            }
        }, 60000);
    }
    
    // Ocultar alerta de advertencia
    function hideWarningAlert() {
        
        // Limpiar countdown
        if (window.sessionTimeout && window.sessionTimeout.countdownInterval) {
            clearInterval(window.sessionTimeout.countdownInterval);
        }
        
        // Remover alertas de sesión (buscar por ID que contiene 'session-warning')
        const sessionAlerts = document.querySelectorAll('[id*="session-warning"]');
        sessionAlerts.forEach(alert => {
            alert.style.animation = 'slideOutRight 0.4s ease-out forwards';
            setTimeout(() => alert.remove(), 400);
        });
    }
    
    // Countdown actualizado para usar el sistema de alertas
    function startCountdown() {
        let remainingSeconds = 60; // 1 minuto
        
        const countdownInterval = setInterval(() => {
            remainingSeconds--;
            
            // Buscar el elemento del countdown en la alerta
            const countdownElement = document.getElementById('session-countdown');
            if (countdownElement) {
                const minutes = Math.floor(remainingSeconds / 60);
                const seconds = remainingSeconds % 60;
                const timeString = `${minutes}:${seconds.toString().padStart(2, '0')}`;
                countdownElement.textContent = timeString;
            }
            
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
    
    // Extender sesión (llamado automáticamente al detectar actividad)
    function extendSession() {
        // Limpiar countdown
        if (window.sessionTimeout && window.sessionTimeout.countdownInterval) {
            clearInterval(window.sessionTimeout.countdownInterval);
        }
        
        // Actualizar actividad
        updateActivity();
        
        // Ocultar alerta
        hideWarningAlert();
    }
    
    // Verificar inactividad periódicamente
    function checkInactivity() {
        const now = Date.now();
        const inactiveTime = now - lastActivity;
        // Si quedan 1 minuto o menos, mostrar advertencia
        if (inactiveTime >= (INACTIVITY_TIMEOUT - WARNING_TIME) && !warningShown) {
            showWarningAlert();
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
