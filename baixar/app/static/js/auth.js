/* app/static/js/auth.js */
document.addEventListener('DOMContentLoaded', function() {
    const cpfInput = document.getElementById('cpf');
    
    if (cpfInput) {
        cpfInput.addEventListener('input', (e) => {
            // Remove tudo que não é número
            let value = e.target.value.replace(/\D/g, '');
            
            // Limita a 11 caracteres
            if (value.length > 11) value = value.slice(0, 11);
            
            // Aplica a formatação visual (opcional, mas aqui deixamos apenas números para o backend)
            e.target.value = value;
        });
    }
});