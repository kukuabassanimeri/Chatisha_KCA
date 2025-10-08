//* LOGIN MESSAGE FADE OUT
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert')
    alerts.forEach(alert =>{
        alert.classList.remove('show');
        alert.classList.add('fade');

        setTimeout(() => alert.remove(), 500)
    });
}, 6000) //* Fade out after 4 seconds

//* TOGGLE PASSWORD
  const toggleIcon = document.querySelector('#toggleIcon');
  const passwordInput = document.querySelector('input[name="password"]');

  toggleIcon.addEventListener('click', () => {
    const isPassword = passwordInput.type === 'password';
    passwordInput.type = isPassword ? 'text' : 'password';
    toggleIcon.classList.toggle('bi-eye');
    toggleIcon.classList.toggle('bi-eye-slash');
  });