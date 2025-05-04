document.addEventListener('DOMContentLoaded', () => {

  const togglePassword = document.getElementById('togglePassword');
  const passwordField = document.getElementById('password');
  const confirmPasswordField = document.getElementById('confirm_password');


  if (togglePassword && passwordField) {
    togglePassword.addEventListener('click', function () {
      const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
      passwordField.setAttribute('type', type);
      this.classList.toggle('bi-eye');
      this.classList.toggle('bi-eye-slash');
    });
  }


  if (togglePassword && confirmPasswordField) {
    togglePassword.addEventListener('click', function () {
      const type = confirmPasswordField.getAttribute('type') === 'password' ? 'text' : 'password';
      confirmPasswordField.setAttribute('type', type);
      this.classList.toggle('bi-eye');
      this.classList.toggle('bi-eye-slash');
    });
  }


  const form = document.querySelector('form');
  form.addEventListener('submit', function (event) {
    const password = passwordField.value;
    const confirmPassword = confirmPasswordField.value;


    if (password !== confirmPassword) {
      event.preventDefault();
      alert("Passwords do not match!");
    }
  });
});
