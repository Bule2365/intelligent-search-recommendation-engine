/**
 * product.js
 * -----------
 * Logika halaman detail produk (product.html). Mengambil product_id dari
 * query string URL, menampilkan detail, mencatat event product_view, dan
 * memuat rekomendasi "produk serupa" lewat recommendations.js.
 */

function getProductIdFromUrl() {
    const params = new URLSearchParams(window.location.search);
    return params.get("id");
}

const productDetailContainer = document.getElementById("product-detail");

function renderProductDetail(p) {
    return `
    <div class="product-detail__category">${p.category} &middot; ${p.brand}</div>
    <h1 class="product-detail__title">${p.title}</h1>
    <p class="product-detail__price">Rp ${p.price.toLocaleString("id-ID")}</p>
    <div class="product-detail__rating">⭐ ${p.rating} (${p.num_reviews} ulasan) &middot; Stok: ${p.stock}</div>
    <p class="product-detail__description">${p.description}</p>
    <button id="add-to-cart-btn" class="btn btn--primary">+ Keranjang</button>
    <button id="buy-now-btn" class="btn btn--secondary">Beli Sekarang</button>
  `;
}

async function loadProductDetail() {
    const productId = getProductIdFromUrl();
    if (!productId) {
        productDetailContainer.innerHTML = "<p>Produk tidak ditemukan.</p>";
        return;
    }

    try {
        const data = await api.getProduct(productId);
        productDetailContainer.innerHTML = renderProductDetail(data.product);

        // api.logEvent("product_view", { productId });
        api.logEvent(
            "product_view",
            {
                userId: getOrCreateUserId(),
                productId
            }
        );

        document.getElementById("add-to-cart-btn").addEventListener("click", () => {
            // api.logEvent("add_to_cart", { productId });
            api.logEvent(
                "add_to_cart",
                {
                    userId: getOrCreateUserId(),
                    productId
                }
            );
            document.getElementById("add-to-cart-btn").textContent = "✓ Ditambahkan";
        });

        document
            .getElementById("buy-now-btn")
            .addEventListener("click", async () => {

                await api.logEvent(
                    "purchase",
                    {
                        userId: getOrCreateUserId(),
                        productId
                    }
                );

                document.getElementById("buy-now-btn").textContent = "✓ Pembelian Berhasil";
            });

        loadSimilarProducts(productId);
    } catch (err) {
        productDetailContainer.innerHTML = `<p>Gagal memuat produk: ${err.message}</p>`;
    }
}

// saveRecentlyViewed(productId);
loadProductDetail();
