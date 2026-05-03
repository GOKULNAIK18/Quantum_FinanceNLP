import Chart from 'chart.js/auto'

let sentimentChart = null

export function renderSentimentChart(canvas, data) {
  if (sentimentChart) sentimentChart.destroy()
  sentimentChart = new Chart(canvas, {
    type: 'bar',
    data: {
      labels: ['Positive', 'Negative', 'Neutral'],
      datasets: [{
        data: [data.positive, data.negative, data.neutral],
        backgroundColor: ['#1db95422', '#e0525222', '#8b8bff22'],
        borderColor:     ['#1db954',   '#e05252',   '#8b8bff'],
        borderWidth: 1,
        borderRadius: 4,
      }],
    },
    options: {
      responsive: true,
      maintainAspectRatio: false,
      plugins: { legend: { display: false } },
      scales: {
        x: {
          grid: { display: false },
          ticks: { color: '#6b6b6b', font: { size: 11, family: 'Inter' } },
          border: { display: false },
        },
        y: {
          grid: { color: '#2a2a2a' },
          ticks: { color: '#6b6b6b', font: { size: 11, family: 'Inter' } },
          border: { display: false },
        },
      },
    },
  })
}
