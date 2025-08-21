document.addEventListener("DOMContentLoaded", () => {
  const form = document.getElementById("track-form");
  const input = document.getElementById("ticker-input");
  const tbody = document.querySelector("#stock-table tbody");
  const errorDiv = document.getElementById("error");
  const ctxPrice = document.getElementById("stockChart").getContext("2d");
  const ctxVolume = document.getElementById("volumeChart").getContext("2d");

  let priceChart;
  let volumeChart;

  form.addEventListener("submit", async (e) => {
    e.preventDefault();

    const tickers = input.value.trim();
    if (!tickers) return;

    try {
      const response = await fetch(`/stocks?tickers=${tickers}`);
      const data = await response.json();

      tbody.innerHTML = "";
      errorDiv.textContent = "";

      let datasetsPrice = [];
      let datasetsVolume = [];
      let chartLabels = [];

      data.forEach((stock, idx) => {
        if (stock.error) {
          errorDiv.textContent += `${stock.ticker}: ${stock.error}\n`;
          return;
        }

        // Add to table
        const row = document.createElement("tr");
        row.innerHTML = `
          <td>${stock.ticker}</td>
          <td>${stock.price}</td>
          <td>${stock.high}</td>
          <td>${stock.low}</td>
          <td>${stock.previous_close}</td>
          <td>${stock.source}</td>
        `;
        tbody.appendChild(row);

        // Chart labels from first stock
        if (chartLabels.length === 0) {
          chartLabels = stock.history.map(day => day.date);
        }

        const prices = stock.history.map(day => day.price);
        const volumes = stock.history.map(day => day.volume);

        const color = `hsl(${(idx * 120) % 360}, 70%, 50%)`;

        // Price dataset
        datasetsPrice.push({
          label: stock.ticker,
          data: prices,
          borderColor: color,
          fill: false,
          tension: 0.1
        });

        // Volume dataset (bar chart for each stock)
        datasetsVolume.push({
          label: stock.ticker,
          data: volumes,
          backgroundColor: color,
        });
      });

      // Destroy old charts
      if (priceChart) priceChart.destroy();
      if (volumeChart) volumeChart.destroy();

      // Price line chart
      priceChart = new Chart(ctxPrice, {
        type: "line",
        data: {
          labels: chartLabels,
          datasets: datasetsPrice
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" }
          },
          scales: {
            x: { title: { display: true, text: "Date" } },
            y: { title: { display: true, text: "Price ($)" } }
          }
        }
      });

      // Volume bar chart
      volumeChart = new Chart(ctxVolume, {
        type: "bar",
        data: {
          labels: chartLabels,
          datasets: datasetsVolume
        },
        options: {
          responsive: true,
          plugins: {
            legend: { position: "top" }
          },
          scales: {
            x: { stacked: true, title: { display: true, text: "Date" } },
            y: { stacked: true, title: { display: true, text: "Volume" } }
          }
        }
      });

    } catch (err) {
      errorDiv.textContent = `Error fetching data: ${err}`;
    }
  });
});