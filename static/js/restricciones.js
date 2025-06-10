document.addEventListener('DOMContentLoaded', function () {
  const container = document.getElementById('restricciones-container');
  const addBtn = document.getElementById('add-restriccion');
  const form = document.getElementById('pl-form');

  function updateRemoveButtons() {
    const rows = container.querySelectorAll('.restriccion-row');
    rows.forEach((row, idx) => {
      const remove = row.querySelector('.remove-restriccion');
      if (idx === 0) {
        remove.classList.add('d-none');
      } else {
        remove.classList.remove('d-none');
        remove.onclick = function (e) {
          e.preventDefault();
          row.remove();
          updateRemoveButtons();
        };
      }
    });
  }

  addBtn.addEventListener('click', function (e) {
    e.preventDefault();
    const first = container.querySelector('.restriccion-row');
    const clone = first.cloneNode(true);
    clone.querySelectorAll('input').forEach(input => (input.value = ''));
    clone.querySelector('select').value = '<=';
    container.appendChild(clone);
    updateRemoveButtons();
  });

  updateRemoveButtons();

  form.addEventListener('submit', function () {
    const data = [];
    container.querySelectorAll('.restriccion-row').forEach(row => {
      const coef_x1 = row.querySelector('[name="coef_x1[]"]').value;
      const coef_x2 = row.querySelector('[name="coef_x2[]"]').value;
      const operador = row.querySelector('[name="operador[]"]').value;
      const valor = row.querySelector('[name="valor[]"]').value;
      data.push({ coef_x1, coef_x2, operador, valor });
    });
    document.getElementById('id_restricciones').value = JSON.stringify(data);
  });
});
