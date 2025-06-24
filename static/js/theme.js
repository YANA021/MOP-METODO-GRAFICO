(function() {
  const apply = (enabled) => {
    const html = document.documentElement;
    if (enabled) {
      html.classList.add('dark');
      window.plotlyTemplate = 'plotly_dark';
    } else {
      html.classList.remove('dark');
      window.plotlyTemplate = 'plotly';
    }
  };

  const themeToggle = () => {
    const enabled = !document.documentElement.classList.contains('dark');
    localStorage.setItem('themeDark', enabled);
    apply(enabled);
  };

  document.addEventListener('DOMContentLoaded', () => {
    const stored = localStorage.getItem('themeDark') === 'true';
    apply(stored);
    const btn = document.getElementById('theme-switch');
    if (btn) btn.addEventListener('click', themeToggle);
  });
})();
