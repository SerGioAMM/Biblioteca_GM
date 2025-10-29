/**
 * Inicializa un contador de caracteres para un input/textarea
 * @param {string} inputId - El ID del elemento input/textarea
 * @param {string} counterId - El ID del elemento donde mostrar el contador
 * @param {number} maxLength - Longitud máxima de caracteres (por defecto 200)
 */
function inicializarContador(inputId, counterId, maxLength = 200) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    
    if (!input || !counter) {
        console.warn(`No se encontró el input "${inputId}" o el contador "${counterId}"`);
        return;
    }
    
    // Establecer maxlength si no está definido
    if (!input.hasAttribute('maxlength')) {
        input.setAttribute('maxlength', maxLength);
    }
    
    // Actualizar contador
    function actualizarContador() {
        const currentLength = input.value.length;
        counter.textContent = currentLength;
        
        // Cambiar color según el límite
        const parentElement = counter.parentElement;
        
        if (currentLength >= maxLength) {
            parentElement.classList.remove('text-muted', 'text-warning');
            parentElement.classList.add('text-danger', 'fw-bold');
        } else if (currentLength >= maxLength * 0.9) {
            parentElement.classList.remove('text-muted', 'text-danger');
            parentElement.classList.add('text-warning', 'fw-bold');
        } else {
            parentElement.classList.remove('text-danger', 'text-warning', 'fw-bold');
            parentElement.classList.add('text-muted');
        }
    }
    
    // Event listeners
    input.addEventListener('input', actualizarContador);
    input.addEventListener('change', actualizarContador);
    
    // Inicializar con el valor actual (por si hay contenido pre-cargado)
    actualizarContador();
}

/**
 * Inicializa múltiples contadores de caracteres
 * @param {Array} contadores - Array de objetos con {inputId, counterId, maxLength}
 */
function inicializarMultiplesContadores(contadores) {
    contadores.forEach(config => {
        inicializarContador(config.inputId, config.counterId, config.maxLength || 200);
    });
}

/**
 * Resetea un contador de caracteres
 * @param {string} inputId - El ID del elemento input/textarea
 * @param {string} counterId - El ID del elemento donde mostrar el contador
 */
function resetearContador(inputId, counterId) {
    const input = document.getElementById(inputId);
    const counter = document.getElementById(counterId);
    
    if (input && counter) {
        input.value = '';
        counter.textContent = '0';
        counter.parentElement.classList.remove('text-danger', 'text-warning', 'fw-bold');
        counter.parentElement.classList.add('text-muted');
    }
}
