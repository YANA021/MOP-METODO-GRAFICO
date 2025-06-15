// Toggle visibility of plot groups using checkboxes
document.addEventListener('DOMContentLoaded', function () {
  const graphs = document.querySelectorAll('.plot-container .plotly-graph-div');
  if (!graphs.length) return;
  document.querySelectorAll('.plot-toggle').forEach(chk => {
    chk.addEventListener('change', () => {
      const group = chk.value;
      const visible = chk.checked;
      graphs.forEach(gd => {
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
});
