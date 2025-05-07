// document.addEventListener('DOMContentLoaded', () => {
//   const form = document.getElementById('resetPasswordForm');
//   const emailInput = document.getElementById('emailInput');
//   const alertBox = document.querySelector('.alert');

//   form.addEventListener('submit', (event) => {
//     event.preventDefault();

//     const email = emailInput.value;

//     // Simple validation for email
//     if (!email || !validateEmail(email)) {
//       alertBox.textContent = 'Please enter a valid email address.';
//       alertBox.style.display = 'block';
//       return;
//     }

//     // Mock success message
//     alertBox.textContent = 'A password reset link has been sent to your email.';
//     alertBox.classList.remove('alert-danger');
//     alertBox.classList.add('alert-success');
//     alertBox.style.display = 'block';

//     // Reset form and email input
//     form.reset();
//   });

//   // Simple email validation function
//   function validateEmail(email) {
//     const re = /^[a-zA-Z0-9._-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,6}$/;
//     return re.test(email);
//   }
// });

document.addEventListener('DOMContentLoaded', () => {
  const form = document.getElementById('resetPasswordForm');
  const usernameInput = document.querySelector('input[name="username"]');
  const alertBox = document.querySelector('.alert');

  form.addEventListener('submit', (event) => {
    const username = usernameInput.value.trim();

    if (!username) {
      event.preventDefault();
      alertBox.textContent = 'Please enter your username.';
      alertBox.classList.add('alert-danger');
      alertBox.style.display = 'block';
    }
  });
});
