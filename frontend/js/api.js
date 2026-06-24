/**
 * api.js
 * -------
 * Satu-satunya tempat frontend memanggil backend. Semua file JS lain
 * (search.js, product.js, recommendations.js, analytics.js) memakai
 * fungsi-fungsi di sini, bukan memanggil fetch() langsung -- supaya kalau
 * base URL atau format error handling berubah, cukup diubah di satu
 * tempat (prinsip yang sama dengan db/ di backend, Bagian 5.4).
 */

const API_BASE_URL = "http://localhost:8000/api";

/** Ambil atau buat user_id sintetis yang konsisten per browser, disimpan
 * di localStorage. Ini menggantikan sistem login penuh (di luar scope
 * proyek ini) tapi tetap memberi identitas stabil untuk personalization
 * dan A/B testing (Bagian 9 dependencies.py, analytics_engine/ab_testing.py). */

// function getOrCreateUserId() {
//     let userId = localStorage.getItem("ecom_user_id");
//     if (!userId) {
//         userId = "U" + Math.random().toString(36).slice(2, 10);
//         localStorage.setItem("ecom_user_id", userId);
//     }
//     return userId;
// }

function getOrCreateUserId() {
    let userId = localStorage.getItem("ecom_user_id");

    if (!userId) {
        userId =
            "U_" +
            Date.now().toString(36) +
            Math.random().toString(36).substring(2, 8);

        localStorage.setItem("ecom_user_id", userId);
    }

    return userId;
}

async function apiRequest(path, { method = "GET", params = null, body = null } = {}) {
    let url = `${API_BASE_URL}${path}`;
    if (params) {
        const query = new URLSearchParams(
            Object.entries(params).filter(([, v]) => v !== null && v !== undefined)
        );
        url += `?${query.toString()}`;
    }

    const options = { method, headers: {} };
    if (body) {
        options.headers["Content-Type"] = "application/json";
        options.body = JSON.stringify(body);
    }

    const response = await fetch(url, options);
    if (!response.ok) {
        const errorBody = await response.json().catch(() => ({}));
        throw new Error(errorBody.detail || `Request gagal: ${response.status}`);
    }
    return response.json();
}

const api = {
    search(query, mode = "hybrid", topK = 10) {
        return apiRequest("/search", { params: { q: query, mode, top_k: topK } });
    },
    getProduct(productId) {
        return apiRequest(`/products/${productId}`);
    },
    listProducts(filters = {}) {
        return apiRequest("/products", { params: filters });
    },
    similarProducts(productId, topK = 8) {
        return apiRequest(`/recommendations/similar/${productId}`, { params: { top_k: topK } });
    },
    recommendationsForUser(userId, topK = 8, recentCategory = null) {
        return apiRequest(`/recommendations/user/${userId}`, {
            params: { top_k: topK, recent_category: recentCategory },
        });
    },
    logEvent(eventType, { productId = null, searchQuery = null } = {}) {
        const userId = getOrCreateUserId();
        // fire-and-forget: tracking tidak boleh memblokir interaksi user
        // (prinsip yang sama dengan alur request di Bagian 2.4).
        return apiRequest("/events", {
            method: "POST",
            body: { user_id: userId, event_type: eventType, product_id: productId, search_query: searchQuery },
        }).catch((err) => console.warn("Gagal mencatat event:", err));
    },
    analyticsSummary() {
        return apiRequest("/analytics/summary");
    },
    analyticsTimeline(days = 14) {
        return apiRequest("/analytics/timeline", { params: { days } });
    },
};

async function logEvent(eventType, payload = {}) {
    const body = {
        user_id: getOrCreateUserId(),
        event_type: eventType,
        product_id: payload.productId || null,
        search_query: payload.searchQuery || null
    };

    return fetch(`${API_BASE_URL}/events`, {
        method: "POST",
        headers: {
            "Content-Type": "application/json"
        },
        body: JSON.stringify(body)
    });
}