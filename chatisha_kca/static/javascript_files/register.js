//* FADE OUT ERROR MESSAGE
document.addEventListener("DOMContentLoaded", function() {
    setTimeout(() => {
        const dangerMessages = document.querySelectorAll('.text-danger');
        dangerMessages.forEach(danger => {

            //* Add fade-out effect smoothly
            danger.style.transition = "opacity 0.5s ease";
            
            setTimeout(() => {
                danger.style.opacity = "0";
                setTimeout(() => danger.remove(), 500); //* remove after fade

            }, 5000); //* fade after 2 seconds
        });
    }, 100);
});

//* TOGGLE PASSWORD
document.querySelectorAll('.toggle-password').forEach(icon => {
  icon.addEventListener('click', () => {
    const input = document.getElementById(icon.getAttribute('data-target'));
    const isPassword = input.type === 'password';
    input.type = isPassword ? 'text' : 'password';
    icon.classList.toggle('bi-eye');
    icon.classList.toggle('bi-eye-slash');
  });
});