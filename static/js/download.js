// Add download buttons using Plotly
document.addEventListener('DOMContentLoaded', function () {
  document.querySelectorAll('.download-btn').forEach(btn => {
    btn.addEventListener('click', function () {
      const format = this.dataset.format;
      const gd = document.querySelector('.plotly-graph-div');
      if (gd && Plotly.downloadImage) {
        Plotly.downloadImage(gd, {format, filename: 'grafica'});
      }
    });
  });
});
