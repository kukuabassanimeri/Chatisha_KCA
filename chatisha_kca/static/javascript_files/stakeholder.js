//* FAQ
document.querySelectorAll('.faq-item').forEach(item => {
        item.addEventListener('click', () => {

            //* Close all other open FAQs
            document.querySelectorAll('.faq-item').forEach(i => {
                if (i !== item) i.classList.remove('active');
            });

            //* Toggle this one
            item.classList.toggle('active');
        });
    });

//* ALERT MESSAGE FADEOUT
setTimeout(() => {
    const alerts = document.querySelectorAll('.alert')
    alerts.forEach(alert =>{
        alert.classList.remove('show');
        alert.classList.add('fade');

        setTimeout(() => alert.remove(), 500)
    });
}, 6000) //* Fade out after 4 seconds