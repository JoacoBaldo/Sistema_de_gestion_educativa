document.addEventListener('DOMContentLoaded', () => {
    const form = document.getElementById('formAsistencia');
    const screenForm = document.getElementById('screen-form');
    const screenSuccess = document.getElementById('screen-success');
    const screenError = document.getElementById('screen-error');
    const errorMessage = document.getElementById('error-message');
    const btnRegistrar = document.getElementById('btn-registrar');

    let num1 = Math.floor(Math.random() * 10) + 1;
    let num2 = Math.floor(Math.random() * 10) + 1;
    let captchaResult = num1 + num2;
    document.getElementById('captcha-question').textContent = `¿Cuánto es ${num1} + ${num2}?`;

    form.addEventListener('submit', async (e) => {
        e.preventDefault();

        const padron = document.getElementById('padron').value.trim();
        const token = document.getElementById('qrToken').value;
        const captchaAnswer = document.getElementById('captcha-answer').value;

        if (!padron || !captchaAnswer) {
            alert('Por favor complete todos los campos.');
            return;
        }

        if (parseInt(captchaAnswer) !== captchaResult) {
            alert('El resultado de la verificación es incorrecto.');
            document.getElementById('captcha-answer').value = '';
            num1 = Math.floor(Math.random() * 10) + 1;
            num2 = Math.floor(Math.random() * 10) + 1;
            captchaResult = num1 + num2;
            document.getElementById('captcha-question').textContent = `¿Cuánto es ${num1} + ${num2}?`;
            return;
        }

        btnRegistrar.textContent = 'Registrando...';
        btnRegistrar.disabled = true;

        try {
            const response = await fetch('/api/v1/asistencia/registrar', {
                method: 'POST',
                headers: {
                    'Content-Type': 'application/json'
                },
                body: JSON.stringify({ token: token, padron: padron })
            });

            const data = await response.json();

            screenForm.classList.add('hidden');

            if (response.ok) {
                screenSuccess.classList.remove('hidden');
            } else {
                errorMessage.textContent = data.error || 'Ocurrió un error inesperado.';
                screenError.classList.remove('hidden');
            }

        } catch (error) {
            console.error('Error de red:', error);
            screenForm.classList.add('hidden');
            errorMessage.textContent = 'Error de conexión. Revisa tu internet e intenta de nuevo.';
            screenError.classList.remove('hidden');
        } finally {
            btnRegistrar.textContent = 'Registrar Presente';
            btnRegistrar.disabled = false;
        }
    });
});