document.addEventListener('DOMContentLoaded', () => {
    const toggle = document.getElementById('theme-toggle');
    const label = document.getElementById('theme-toggle-label');
    const stored = localStorage.getItem('theme') || 'dark';
    setTheme(stored);
    toggle.checked = stored === 'light';

    toggle.addEventListener('change', () => {
        const theme = toggle.checked ? 'light' : 'dark';
        setTheme(theme);
        localStorage.setItem('theme', theme);
    });

    function setTheme(theme) {
        document.documentElement.setAttribute('data-bs-theme', theme);
        label.textContent = theme === 'light' ? 'Modo claro' : 'Modo oscuro';
    }
});
