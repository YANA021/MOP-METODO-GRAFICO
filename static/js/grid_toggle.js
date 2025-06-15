document.addEventListener('DOMContentLoaded', function () {
  const chk = document.getElementById('chk-grid');
  if (!chk) return;
  chk.addEventListener('change', function () {
    const show = this.checked;
    document.querySelectorAll('.plot-container .plotly-graph-div').forEach(gd => {
      Plotly.relayout(gd, {
        'xaxis.showgrid': show,
        'yaxis.showgrid': show
      });
    });
  });
});
