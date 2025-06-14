// Toggle visibility of plot groups using checkboxes
document.addEventListener('DOMContentLoaded', function () {
  const gd = document.querySelector('#plot-container .plotly-graph-div');
  if (!gd) return;
  document.querySelectorAll('.plot-toggle').forEach(chk => {
    chk.addEventListener('change', () => {
      const group = chk.value;
      const visible = chk.checked;
      const indices = [];
      gd.data.forEach((trace, i) => {
        if (trace.legendgroup === group) {
          indices.push(i);
        }
      });
      if (indices.length) {
        Plotly.restyle(gd, { visible: visible }, indices);
      }
    });
  });
});
