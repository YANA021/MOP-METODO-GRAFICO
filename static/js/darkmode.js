(function () {
  function applyDarkMode(enabled) {
    const label = document.querySelector('label[for="modeSwitch"]');
    if (enabled) {
      document.body.classList.add('bg-dark', 'text-light');
      if (label) label.textContent = 'Modo oscuro';
    } else {
      document.body.classList.remove('bg-dark', 'text-light');
      if (label) label.textContent = 'Modo claro';
    }
  }

  document.addEventListener('DOMContentLoaded', function () {
    const switchInput = document.getElementById('modeSwitch');
    if (!switchInput) return;

    const savedPreference = localStorage.getItem('darkMode');
    const darkEnabled = savedPreference === 'true';

    switchInput.checked = darkEnabled;
    applyDarkMode(darkEnabled);

    switchInput.addEventListener('change', function () {
      localStorage.setItem('darkMode', this.checked);
      applyDarkMode(this.checked);
    });
  });
})();
