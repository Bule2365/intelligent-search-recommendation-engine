/**
 * search.js
 * ----------
 * Logika halaman pencarian (index.html). Bertanggung jawab: menangani
 * input pencarian, memanggil API, merender hasil, dan mencatat event
 * search_performed & product_click untuk dipakai analytics dan
 * collaborative filtering (Bagian 8.2).
 */

const searchInput = document.getElementById("search-input");
const searchModeSelect = document.getElementById("search-mode");
const searchButton = document.getElementById("search-button");
const resultsContainer = document.getElementById("results-container");
const resultsMeta = document.getElementById("results-meta");

function renderProductCard(item) {
    const p = item.product;
    if (!p) return "";

    const scoreDetail =
        item.bm25_score != null && item.semantic_score != null
            ? `<span class="score-detail">bm25=${item.bm25_score.toFixed(2)} semantic=${item.semantic_score.toFixed(2)}</span>`
            : "";

    return `
    <a class="product-card" href="product.html?id=${p.product_id}" data-product-id="${p.product_id}">
      <div class="product-card__category">${p.category}</div>
      <h3 class="product-card__title">${p.title}</h3>
      <p class="product-card__brand">${p.brand}</p>
      <p class="product-card__price">Rp ${p.price.toLocaleString("id-ID")}</p>
      <div class="product-card__rating">⭐ ${p.rating} (${p.num_reviews} ulasan)</div>
      <div class="product-card__score">score: ${item.score.toFixed(3)} ${scoreDetail}</div>
    </a>
  `;
}

async function runSearch() {
    const query = searchInput.value.trim();
    if (!query) return;

    const mode = searchModeSelect.value;
    resultsMeta.textContent = "Mencari...";
    resultsContainer.innerHTML = "";

    try {
        const data = await api.search(query, mode, 12);
        resultsMeta.textContent = `${data.total_results} hasil untuk "${data.query}" (mode: ${data.mode}, ${data.took_ms}ms)`;
        resultsContainer.innerHTML = data.results.map(renderProductCard).join("");

        // Catat event search, lalu pasang listener klik per kartu hasil.
        // api.logEvent("search_performed", { searchQuery: query });
        api.logEvent(
            "search_performed",
            {
                userId: getOrCreateUserId(),
                searchQuery: query
            }
        );
        attachClickTracking();
    } catch (err) {
        resultsMeta.textContent = `Gagal mencari: ${err.message}`;
    }
}

function attachClickTracking() {
    document.querySelectorAll(".product-card").forEach((card) => {
        card.addEventListener("click", () => {
            api.logEvent("product_click", { productId: card.dataset.productId });
        });
    });
}

searchButton.addEventListener("click", runSearch);
searchInput.addEventListener("keydown", (e) => {
    if (e.key === "Enter") runSearch();
});

// Muat beberapa produk populer saat halaman pertama dibuka, supaya halaman
// tidak kosong sebelum user mengetik apapun.
(async function loadInitialProducts() {
    try {
        const data = await api.listProducts({ page_size: 12 });
        resultsMeta.textContent = `Menampilkan ${data.items.length} dari ${data.total} produk`;
        resultsContainer.innerHTML = data.items
            .map((p) => renderProductCard({ product: p, score: p.rating }))
            .join("");
        attachClickTracking();
    } catch (err) {
        resultsMeta.textContent = `Tidak bisa memuat produk awal: ${err.message}`;
    }
})();
