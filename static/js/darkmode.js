document.addEventListener('DOMContentLoaded', function () {
  const switchInput = document.getElementById('modeSwitch');
  if (!switchInput) return;
  switchInput.addEventListener('change', function () {
    const label = document.querySelector('label[for="modeSwitch"]');
    if (this.checked) {
      document.body.classList.add('bg-dark', 'text-light');
      if (label) label.textContent = 'Modo oscuro';
    } else {
      document.body.classList.remove('bg-dark', 'text-light');
      if (label) label.textContent = 'Modo claro';
    }
  });
});
