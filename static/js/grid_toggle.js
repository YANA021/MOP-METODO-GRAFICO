document.addEventListener('DOMContentLoaded', function () {
  const gd = document.querySelector('#plot-container .plotly-graph-div');
  const chk = document.getElementById('chk-grid');
  if (!gd || !chk) return;
  chk.addEventListener('change', function () {
    const show = this.checked;
    Plotly.relayout(gd, {
      'xaxis.showgrid': show,
      'yaxis.showgrid': show
    });
  });
});
