/* ========================================
   APLICADOR DE ANIMACIONES
   ======================================== */

// REHABILITADO - Aplicar animaciones a tarjetas al cargar
function animateCards() {
    // Animar tarjetas de libros
    const bookCards = document.querySelectorAll('.contenedor-libros .card, .row-cols-md-6 .card');
    bookCards.forEach(card => {
        if (!card.classList.contains('card-animate')) {
            card.classList.add('card-animate');
        }
    });
    
    // Animar tarjetas de préstamos
    const loanCards = document.querySelectorAll('.contenedor-prestamos .card');
    loanCards.forEach(card => {
        if (!card.classList.contains('card-animate')) {
            card.classList.add('card-animate');
        }
    });
}

// DESHABILITADO - El usuario no quiere animaciones de carga
// Aplicar animaciones a tablas
function animateTables() {
    // DESHABILITADO
    /*
    const tables = document.querySelectorAll('.table');
    tables.forEach(table => {
        if (!table.classList.contains('table-animate')) {
            table.classList.add('table-animate');
        }
    });
    */
}

// DESHABILITADO - El usuario no quiere animaciones de carga
// Animar elementos al hacer scroll (Intersection Observer)
function setupScrollAnimations() {
    // DESHABILITADO
    /*
    const observer = new IntersectionObserver((entries) => {
        entries.forEach(entry => {
            if (entry.isIntersecting) {
                entry.target.classList.add('fade-in');
                observer.unobserve(entry.target);
            }
        });
    }, {
        threshold: 0.1,
        rootMargin: '0px 0px -50px 0px'
    });
    
    const elementsToAnimate = document.querySelectorAll(
        '.fondo-principal, .contenedor-actividades, .seccion-principal'
    );
    
    elementsToAnimate.forEach(el => {
        observer.observe(el);
    });
    */
}

// SIMPLIFICADO - Sin animaciones de dropdown, Bootstrap maneja todo por defecto
function enhanceNavbarDropdowns() {
    // No hacemos nada, dejamos que Bootstrap maneje los dropdowns normalmente
    // Solo el CSS aplica hover suave a los nav-items
}

// Agregar efecto hover lift a elementos específicos
function addHoverEffects() {
    // Agregar a botones importantes
    const buttons = document.querySelectorAll(
        '.btn-primary, .btn-success, .btn-info, .btn-warning'
    );
    
    buttons.forEach(btn => {
        if (!btn.classList.contains('btn-sm')) { // Excluir botones pequeños
            btn.classList.add('hover-lift');
        }
    });
}

// Animar badges con pulse si tienen contenido importante
function animateImportantBadges() {
    // Badge de notificaciones
    const notificationBadge = document.getElementById('badge-notificaciones');
    if (notificationBadge && notificationBadge.textContent.trim() !== '0') {
        notificationBadge.classList.add('badge-pulse');
    }
    
    // Badge de opiniones
    const opinionsBadge = document.getElementById('badge-opiniones');
    if (opinionsBadge && opinionsBadge.textContent.trim() !== '0') {
        opinionsBadge.classList.add('badge-pulse');
    }
}

// Inicializar todas las animaciones
function initAnimations() {
    // Solo inicializar animaciones que el usuario quiere mantener
    setTimeout(() => {
        animateCards(); // REHABILITADO - El usuario dice que están bien
        // animateTables(); // DESHABILITADO
        // setupScrollAnimations(); // DESHABILITADO
        enhanceNavbarDropdowns(); // Simplificado - solo CSS
        addHoverEffects();
        animateImportantBadges();
    }, 100);
}

// Ejecutar cuando el DOM esté listo
if (document.readyState === 'loading') {
    document.addEventListener('DOMContentLoaded', initAnimations);
} else {
    initAnimations();
}

// Re-aplicar animaciones después de búsquedas o filtros
// DESHABILITADO - Ya no aplicamos animaciones de carga
function reapplyAnimations() {
    // Función vacía para mantener compatibilidad
}

// Exportar para uso global
window.reapplyAnimations = reapplyAnimations;
