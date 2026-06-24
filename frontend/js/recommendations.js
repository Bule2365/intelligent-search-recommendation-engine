/**
 * recommendations.js
 * --------------------
 * Merender section "Produk Serupa" di halaman detail produk (Bagian 8.1
 * & 8.4). Dipanggil dari product.js setelah detail produk berhasil dimuat,
 * supaya recommendation_id (produk yang sedang dilihat) sudah tersedia.
 */

function renderRecommendationCard(item) {
    const p = item.product;
    if (!p) return "";
    return `
    <a class="rec-card" href="product.html?id=${p.product_id}">
      <h4 class="rec-card__title">${p.title}</h4>
      <p class="rec-card__price">Rp ${p.price.toLocaleString("id-ID")}</p>
      <p class="rec-card__reason">${item.reason}</p>
    </a>
  `;
}

async function loadSimilarProducts(productId) {
    const container = document.getElementById("similar-products-container");
    if (!container) return;

    try {
        const data = await api.similarProducts(productId, 8);
        if (data.results.length === 0) {
            container.innerHTML = "<p class='empty-state'>Belum ada produk serupa yang cukup relevan.</p>";
            return;
        }
        container.innerHTML = data.results.map(renderRecommendationCard).join("");
    } catch (err) {
        container.innerHTML = `<p class="empty-state">Gagal memuat rekomendasi: ${err.message}</p>`;
    }
}

/** Dipakai di index.html (search page) untuk section "Rekomendasi untuk Kamu". */
async function loadRecommendationsForUser() {
    const container = document.getElementById("for-you-container");
    if (!container) return;

    const userId = getOrCreateUserId();
    try {
        const data = await api.recommendationsForUser(userId, 8);
        const label = data.source === "cold_start_fallback" ? "Sedang Populer" : "Rekomendasi untuk Kamu";
        document.getElementById("for-you-title").textContent = label;
        container.innerHTML = data.results.map(renderRecommendationCard).join("");
    } catch (err) {
        container.innerHTML = `<p class="empty-state">Gagal memuat rekomendasi: ${err.message}</p>`;
    }
}

if (document.getElementById("for-you-container")) {
    loadRecommendationsForUser();
}
