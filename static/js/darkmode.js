(function () {
  function applyDarkMode(enabled) {
    const label = document.querySelector('label[for="modeSwitch"]');
    if (enabled) {
      document.body.classList.add('dark-mode', 'bg-dark', 'text-light');
      window.plotlyTemplate = 'plotly_dark';
      if (label) label.textContent = 'Modo oscuro';
    } else {
      document.body.classList.remove('dark-mode', 'bg-dark', 'text-light');
      window.plotlyTemplate = 'plotly';
      if (label) label.textContent = 'Modo claro';
    }
    const template = window.plotlyTemplate;
    if (window.Plotly) {
      document.querySelectorAll('.plotly-graph-div').forEach(div => {
        Plotly.update(div, {}, { template });
      });
    }
  }

  // Apply preference as soon as the script loads
  const savedPreference = localStorage.getItem('darkMode');
  const darkEnabledInit = savedPreference === 'true';
  applyDarkMode(darkEnabledInit);

  document.addEventListener('DOMContentLoaded', function () {
    const switchInput = document.getElementById('modeSwitch');
    if (!switchInput) return;

    // ensure graphs match stored preference on first render
    applyDarkMode(darkEnabledInit);

    switchInput.checked = darkEnabledInit;

    switchInput.addEventListener('change', function () {
      localStorage.setItem('darkMode', this.checked);
      applyDarkMode(this.checked);
    });
  });
})();
