const API_BASE_URL =
    import.meta.env.VITE_API_BASE_URL || "http://127.0.0.1:8000";

const TOKEN_KEY = "mk_token";

export function getToken() {
    try {
        return localStorage.getItem(TOKEN_KEY);
    } catch {
        return null;
    }
}

export function setToken(token) {
    try {
        if (token) {
            localStorage.setItem(TOKEN_KEY, token);
        } else {
            localStorage.removeItem(TOKEN_KEY);
        }
    } catch {
        // localStorage unavailable (private mode) — token stays in memory only.
    }
}

/**
 * Core request helper. Attaches the bearer token, parses JSON, and throws
 * an Error carrying the backend "detail" message and status code on failure.
 */
async function request(path, { method = "GET", body, auth = true } = {}) {
    const headers = {};

    if (body !== undefined) {
        headers["Content-Type"] = "application/json";
    }

    if (auth) {
        const token = getToken();
        if (token) {
            headers["Authorization"] = `Bearer ${token}`;
        }
    }

    const response = await fetch(`${API_BASE_URL}${path}`, {
        method,
        headers,
        body: body !== undefined ? JSON.stringify(body) : undefined,
    });

    if (response.status === 204) {
        return null;
    }

    let data = null;
    try {
        data = await response.json();
    } catch {
        data = null;
    }

    if (!response.ok) {
        const detail =
            (data && (data.detail || data.message)) ||
            `Request failed (${response.status})`;
        const error = new Error(
            typeof detail === "string" ? detail : "Request failed"
        );
        error.status = response.status;
        throw error;
    }

    return data;
}

// ---- Auth ----

export async function login(username, password) {
    // Backend uses OAuth2PasswordRequestForm -> form-urlencoded body.
    const form = new URLSearchParams();
    form.append("username", username);
    form.append("password", password);

    const response = await fetch(`${API_BASE_URL}/auth/login`, {
        method: "POST",
        headers: { "Content-Type": "application/x-www-form-urlencoded" },
        body: form.toString(),
    });

    const data = await response.json().catch(() => null);

    if (!response.ok) {
        const detail = (data && data.detail) || "Login failed";
        throw new Error(detail);
    }

    return data; // { access_token, token_type, role, full_name }
}

export function getCurrentStaff() {
    return request("/auth/me");
}

// ---- Menu ----

export function getMenu() {
    return request("/menu", { auth: false });
}

export function getTodaysMenu() {
    return request("/menu/today", { auth: false });
}

export function createMenuItem(item) {
    return request("/menu", { method: "POST", body: item });
}

export function updateMenuItem(id, item) {
    return request(`/menu/${id}`, { method: "PUT", body: item });
}

export function deleteMenuItem(id) {
    return request(`/menu/${id}`, { method: "DELETE" });
}

// ---- Orders ----

export function getOrders() {
    return request("/orders");
}

export function getOrder(id) {
    return request(`/orders/${id}`, { auth: false });
}

export function createOrder(payload) {
    return request("/orders", { method: "POST", body: payload, auth: false });
}

export function updateOrderStatus(id, status) {
    return request(`/orders/${id}/status`, {
        method: "PATCH",
        body: { status },
    });
}

export function cancelOrder(id) {
    return request(`/orders/${id}/cancel`, { method: "POST" });
}

export function getOrderFeedback(id) {
    return request(`/orders/${id}/feedback`, { auth: false });
}

export function submitOrderFeedback(id, payload) {
    return request(`/orders/${id}/feedback`, {
        method: "POST",
        body: payload,
        auth: false,
    });
}

// ---- Customers ----

export function getCustomers() {
    return request("/customers");
}

export function updateCustomer(id, data) {
    return request(`/customers/${id}`, { method: "PUT", body: data });
}

// ---- Tables ----

export function getTables() {
    return request("/tables");
}

export function updateTable(id, data) {
    return request(`/tables/${id}`, { method: "PUT", body: data });
}

// ---- Inventory ----

export function getInventory() {
    return request("/inventory");
}

export function createInventoryItem(item) {
    return request("/inventory", { method: "POST", body: item });
}

export function updateInventoryItem(id, item) {
    return request(`/inventory/${id}`, { method: "PUT", body: item });
}

export function deleteInventoryItem(id) {
    return request(`/inventory/${id}`, { method: "DELETE" });
}

// ---- Waste ----

export function getWaste() {
    return request("/waste");
}

export function createWaste(payload) {
    return request("/waste", { method: "POST", body: payload });
}

// ---- Staff ----

export function getStaff() {
    return request("/auth/staff");
}

export function createStaff(payload) {
    return request("/auth/staff", { method: "POST", body: payload });
}

// ---- Recipes ----

export function getRecipes() {
    return request("/recipes");
}

export function createRecipe(payload) {
    return request("/recipes", { method: "POST", body: payload });
}

export function updateRecipe(id, payload) {
    return request(`/recipes/${id}`, { method: "PUT", body: payload });
}

export function deleteRecipe(id) {
    return request(`/recipes/${id}`, { method: "DELETE" });
}

// ---- Reports ----

export function getReportsSummary(period = "all") {
    return request(`/reports/summary?period=${period}`);
}

export function getReportsCosting() {
    return request("/reports/costing");
}

// ---- Payments ----

export function createPayment(payload) {
    return request("/payments", { method: "POST", body: payload });
}

export function getPayments({ date, orderId } = {}) {
    const params = new URLSearchParams();
    if (date) params.set("date", date);
    if (orderId) params.set("order_id", orderId);
    const qs = params.toString();
    return request(`/payments${qs ? `?${qs}` : ""}`);
}

export function getReconciliation(date) {
    const qs = date ? `?date=${date}` : "";
    return request(`/payments/reconciliation${qs}`);
}

export function updatePayment(id, payload) {
    return request(`/payments/${id}`, { method: "PATCH", body: payload });
}

// Start a gateway checkout for an order; returns where/how to send the payer.
export function startCheckout(payload) {
    return request("/payments/checkout", {
        method: "POST",
        body: payload,
        auth: false,
    });
}

export function getCheckoutStatus(txnRef) {
    return request(`/payments/checkout/${txnRef}/status`, { auth: false });
}

// ---- Settings ----

export function getOrderingStatus() {
    return request("/settings/status", { auth: false });
}

export function getSettings() {
    return request("/settings");
}

export function updateSettings(payload) {
    return request("/settings", { method: "PUT", body: payload });
}

// ---- Health ----

export async function checkBackendHealth() {
    return request("/health", { auth: false });
}
