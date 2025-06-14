// Script to precargar datos de ejemplo desde el modal de ayuda

document.addEventListener('DOMContentLoaded', function () {
  const btn = document.getElementById('cargar-ejemplo');
  if (!btn) return;

  btn.addEventListener('click', function () {
    const objetivo = document.getElementById('id_objetivo');
    const coefX1 = document.getElementById('id_coef_x1');
    const coefX2 = document.getElementById('id_coef_x2');
    if (objetivo) objetivo.value = 'max';
    if (coefX1) coefX1.value = 3;
    if (coefX2) coefX2.value = 5;

    const container = document.getElementById('restricciones-container');
    if (container) {
      const base = container.querySelector('.restriccion-row');
      if (base) {
        container.innerHTML = '';
        const ejemplos = [
          { c1: 1, c2: 0, op: '<=', val: 4 },
          { c1: 0, c2: 2, op: '<=', val: 12 },
          { c1: 3, c2: 2, op: '<=', val: 18 }
        ];
        ejemplos.forEach(ej => {
          const row = base.cloneNode(true);
          row.querySelector('[name="coef_x1[]"]').value = ej.c1;
          row.querySelector('[name="coef_x2[]"]').value = ej.c2;
          row.querySelector('[name="operador[]"]').value = ej.op;
          row.querySelector('[name="valor[]"]').value = ej.val;
          container.appendChild(row);
        });
        if (window.updateRemoveButtons) window.updateRemoveButtons();
      }
    }

    const modalEl = document.getElementById('ayudaModal');
    if (modalEl) {
      const modal = bootstrap.Modal.getInstance(modalEl);
      if (modal) modal.hide();
    }
  });
});
