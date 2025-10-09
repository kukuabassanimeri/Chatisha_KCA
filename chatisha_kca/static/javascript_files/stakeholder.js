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

document.addEventListener('DOMContentLoaded', () => {
  const toggle = document.getElementById('concernToggle');
  const icon = toggle.querySelector('.toggle-icon');
  const submenu = document.getElementById('allConcernsSubmenu');

  submenu.addEventListener('show.bs.collapse', () => icon.textContent = '−');
  submenu.addEventListener('hide.bs.collapse', () => icon.textContent = '+');
});

//* DELETE ISSUE POP UP BUTTON
document.addEventListener("DOMContentLoaded", function () {
  const deleteButtons = document.querySelectorAll(".delete-btn");
  const issueTitle = document.getElementById("issueTitle");
  const deleteForm = document.getElementById("deleteForm");

  deleteButtons.forEach(button => {
    button.addEventListener("click", function () {
      issueTitle.textContent = this.getAttribute("data-issue-title");
      deleteForm.action = this.getAttribute("data-delete-url");
    });
  });
});

//* SUBMIT ISSUE POP UP FORM
document.addEventListener("DOMContentLoaded", function () {
  //* Submit Issue modal
  const submitLink = document.getElementById("openSubmitModal");
  const submitForm = document.getElementById("submitIssueForm");

  if (submitLink && submitForm) {
    const submitUrl = submitLink.getAttribute("data-submit-url");

    submitLink.addEventListener("click", function (e) {
      //* Open modal instead of navigating
      e.preventDefault();

      //* Reset the form each time
      submitForm.reset();

      submitForm.setAttribute("action", submitUrl);

      //* Show modal
      const modal = new bootstrap.Modal(document.getElementById("submitIssueModal"));
      modal.show();
    });
  }
});