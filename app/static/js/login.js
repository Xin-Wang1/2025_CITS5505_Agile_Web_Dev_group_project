const togglePassword = document.getElementById('togglePassword');
const passwordField = document.getElementById('password');

if (togglePassword && passwordField) {
  togglePassword.addEventListener('click', function () {
    const type = passwordField.getAttribute('type') === 'password' ? 'text' : 'password';
    passwordField.setAttribute('type', type);
    this.classList.toggle('bi-eye');
    this.classList.toggle('bi-eye-slash');
  });
}
