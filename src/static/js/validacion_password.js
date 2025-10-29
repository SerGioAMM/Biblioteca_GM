/* ========================================
   VALIDACIÓN DE CONTRASEÑAS
   Valida requisitos de seguridad
   ======================================== */

(function() {
    'use strict';
    
    /**
     * Valida que la contraseña cumpla con los requisitos:
     * - Mínimo 8 caracteres
     * - Al menos una mayúscula
     * - Al menos una minúscula
     * - Al menos un número
     */
    function validarPassword(password) {
        const requisitos = {
            longitud: password.length >= 8,
            mayuscula: /[A-Z]/.test(password),
            minuscula: /[a-z]/.test(password),
            numero: /[0-9]/.test(password)
        };
        
        const valido = requisitos.longitud && requisitos.mayuscula && 
                      requisitos.minuscula && requisitos.numero;
        
        return {
            valido: valido,
            requisitos: requisitos
        };
    }
    
    /**
     * Muestra feedback visual de los requisitos de contraseña
     */
    function mostrarFeedback(inputElement, contenedorFeedback) {
        const password = inputElement.value;
        const validacion = validarPassword(password);
        
        // Crear o actualizar el contenedor de feedback
        if (!contenedorFeedback) {
            contenedorFeedback = document.createElement('div');
            contenedorFeedback.className = 'password-feedback-floating';
            contenedorFeedback.id = inputElement.id + '-feedback';
            document.body.appendChild(contenedorFeedback); // Agregar al body para position fixed
        }
        
        // Solo mostrar feedback si hay algo escrito
        if (password.length === 0) {
            contenedorFeedback.classList.remove('show');
            contenedorFeedback.classList.add('hide');
            return;
        }
        
        // Calcular posición del input
        const rect = inputElement.getBoundingClientRect();
        contenedorFeedback.style.top = `${rect.bottom + window.scrollY + 5}px`;
        contenedorFeedback.style.left = `${rect.left + window.scrollX}px`;
        contenedorFeedback.style.width = `${rect.width}px`;
        
        // Mostrar con animación
        contenedorFeedback.classList.remove('hide');
        contenedorFeedback.classList.add('show');
        
        const html = `
            <small class="d-block">
                <i class="bi ${validacion.requisitos.longitud ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                Mínimo 8 caracteres
            </small>
            <small class="d-block">
                <i class="bi ${validacion.requisitos.mayuscula ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                Al menos una mayúscula
            </small>
            <small class="d-block">
                <i class="bi ${validacion.requisitos.minuscula ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                Al menos una minúscula
            </small>
            <small class="d-block">
                <i class="bi ${validacion.requisitos.numero ? 'bi-check-circle-fill text-success' : 'bi-x-circle-fill text-danger'}"></i>
                Al menos un número
            </small>
        `;
        
        contenedorFeedback.innerHTML = html;
        
        // Cambiar borde del input según validación
        if (validacion.valido) {
            inputElement.classList.remove('is-invalid');
            inputElement.classList.add('is-valid');
            
            // Si es válido, ocultar después de 3 segundos
            setTimeout(() => {
                contenedorFeedback.classList.remove('show');
                contenedorFeedback.classList.add('hide');
            }, 3000);
        } else {
            inputElement.classList.remove('is-valid');
            inputElement.classList.add('is-invalid');
        }
        
        return validacion;
    }
    
    /**
     * Inicializa la validación para un campo de contraseña
     */
    function inicializarValidacion(inputId, formId, esOpcional = false) {
        const input = document.getElementById(inputId);
        const form = document.getElementById(formId);
        
        if (!input || !form) return;
        
        let contenedorFeedback = document.getElementById(inputId + '-feedback');
        
        // Función para reposicionar el feedback
        function reposicionarFeedback() {
            if (contenedorFeedback && contenedorFeedback.classList.contains('show')) {
                const rect = input.getBoundingClientRect();
                contenedorFeedback.style.top = `${rect.bottom + window.scrollY + 5}px`;
                contenedorFeedback.style.left = `${rect.left + window.scrollX}px`;
                contenedorFeedback.style.width = `${rect.width}px`;
            }
        }
        
        // Reposicionar en scroll y resize
        window.addEventListener('scroll', reposicionarFeedback);
        window.addEventListener('resize', reposicionarFeedback);
        
        // Validar mientras escribe
        input.addEventListener('input', function() {
            mostrarFeedback(this, contenedorFeedback);
            contenedorFeedback = document.getElementById(inputId + '-feedback');
        });
        
        // Ocultar cuando pierde el foco después de 3 segundos
        input.addEventListener('blur', function() {
            setTimeout(() => {
                if (contenedorFeedback) {
                    contenedorFeedback.classList.remove('show');
                    contenedorFeedback.classList.add('hide');
                }
            }, 2000);
        });
        
        // Mostrar de nuevo cuando gana el foco
        input.addEventListener('focus', function() {
            if (this.value.length > 0 && contenedorFeedback) {
                contenedorFeedback.classList.remove('hide');
                contenedorFeedback.classList.add('show');
                reposicionarFeedback();
            }
        });
        
        // Validar al enviar el formulario
        form.addEventListener('submit', function(e) {
            const password = input.value;
            
            // Si es opcional y está vacío, permitir el envío
            if (esOpcional && password.length === 0) {
                return true;
            }
            
            // Si tiene contenido, validar
            if (password.length > 0) {
                const validacion = validarPassword(password);
                
                if (!validacion.valido) {
                    e.preventDefault();
                    e.stopPropagation();
                    
                    // Mostrar feedback si no está visible
                    mostrarFeedback(input, contenedorFeedback);
                    
                    // Mostrar alerta
                    if (window.showAlert) {
                        window.showAlert(
                            'La contraseña no cumple con los requisitos de seguridad',
                            'danger',
                            5000,
                            'bi-shield-exclamation'
                        );
                    }
                    
                    // Hacer scroll al campo
                    input.focus();
                    input.scrollIntoView({ behavior: 'smooth', block: 'center' });
                    
                    return false;
                }
            }
        });
    }
    
    // Esperar a que el DOM esté listo
    if (document.readyState === 'loading') {
        document.addEventListener('DOMContentLoaded', function() {
            inicializar();
        });
    } else {
        inicializar();
    }
    
    function inicializar() {
        // Registro de usuarios
        if (document.getElementById('form-registro-usuario')) {
            inicializarValidacion('contrasena', 'form-registro-usuario', false);
        }
        
        // Edición de perfil (contraseña opcional)
        if (document.getElementById('form-editar-perfil')) {
            inicializarValidacion('nueva_contrasena', 'form-editar-perfil', true);
        }
    }
    
    // Exportar funciones para uso global si es necesario
    window.validacionPassword = {
        validar: validarPassword,
        mostrarFeedback: mostrarFeedback,
        inicializar: inicializarValidacion
    };
})();
