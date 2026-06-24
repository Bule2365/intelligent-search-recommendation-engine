/**
 * analytics.js
 * --------------
 * Logika dashboard analytics (analytics.html). Sengaja dirender dengan
 * bar chart CSS sederhana (div dengan width dinamis), BUKAN library
 * charting eksternal -- konsisten dengan filosofi frontend tanpa
 * framework (Bagian 2.3.1) dan menghindari beban load tambahan untuk
 * kebutuhan visualisasi yang sebenarnya sederhana (beberapa bar chart).
 */

function renderBarChart(container, data, labelKey, valueKey) {
  if (!data || data.length === 0) {
    container.innerHTML = "<p class='empty-state'>Belum ada data.</p>";
    return;
  }
  const max = Math.max(...data.map((d) => d[valueKey]));
  container.innerHTML = data
    .map((d) => {
      const pct = max > 0 ? (d[valueKey] / max) * 100 : 0;
      return `
        <div class="bar-row">
          <div class="bar-row__label">${d[labelKey]}</div>
          <div class="bar-row__track">
            <div class="bar-row__fill" style="width:${pct}%"></div>
          </div>
          <div class="bar-row__value">${d[valueKey]}</div>
        </div>
      `;
    })
    .join("");
}

function renderFunnel(container, funnel) {
  const order = ["search_performed", "product_view", "product_click", "add_to_cart", "purchase"];
  const labels = {
    search_performed: "Search",
    product_view: "View",
    product_click: "Click",
    add_to_cart: "Add to Cart",
    purchase: "Purchase",
  };
  const data = order.map((key) => ({ label: labels[key], value: funnel[key] || 0 }));
  renderBarChart(container, data, "label", "value");
}

async function loadDashboard() {
  const summaryEl = document.getElementById("ctr-value");
  const funnelEl = document.getElementById("funnel-chart");
  const queriesEl = document.getElementById("top-queries-chart");
  const categoriesEl = document.getElementById("top-categories-chart");

  try {
    const summary = await api.analyticsSummary();
    summaryEl.textContent = `${(summary.click_through_rate * 100).toFixed(1)}%`;
    renderFunnel(funnelEl, summary.funnel);
    renderBarChart(queriesEl, summary.top_queries, "search_query", "count");
    renderBarChart(categoriesEl, summary.top_categories, "category", "interactions");
  } catch (err) {
    document.getElementById("dashboard-error").textContent = `Gagal memuat dashboard: ${err.message}`;
  }
}

loadDashboard();
