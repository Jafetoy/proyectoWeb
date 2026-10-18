// Password visibility toggle script
document.addEventListener('DOMContentLoaded', function () {
  document.addEventListener('click', function (e) {
    var btn = e.target.closest('.toggle-password-btn');
    if (!btn) return;
    e.preventDefault();

    var wrapper = btn.closest('.password-wrapper');
    if (!wrapper) return;

    var input = wrapper.querySelector('input');
    if (!input) return;

    var icon = btn.querySelector('i');
    if (input.type === 'password') {
      input.type = 'text';
      if (icon) {
        icon.classList.remove('bi-eye');
        icon.classList.add('bi-eye-slash');
      }
    } else {
      input.type = 'password';
      if (icon) {
        icon.classList.remove('bi-eye-slash');
        icon.classList.add('bi-eye');
      }
    }
  });
});
