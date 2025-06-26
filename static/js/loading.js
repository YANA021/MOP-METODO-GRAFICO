// Show a loading spinner overlay on form submission
document.addEventListener('DOMContentLoaded', function () {
  const overlay = document.getElementById('loading-overlay');
  if (!overlay) return;
  document.querySelectorAll('form[data-loading-overlay]')
    .forEach(form => {
      form.addEventListener('submit', () => {
        overlay.classList.add('show');
      });
    });
});
