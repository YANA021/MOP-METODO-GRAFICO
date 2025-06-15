// Add download buttons using Plotly
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.download-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const format = this.dataset.format;
      let gd = null;
      document.querySelectorAll('.plot-container .plotly-graph-div').forEach(div => {
        if (div.parentElement.style.display !== 'none') {
          gd = div;
        }
      });
      if (gd && Plotly.downloadImage) {
        Plotly.downloadImage(gd, {format, filename: 'grafica'});
      }
    });
  });
});
