const API_BASE_URL = "http://127.0.0.1:8000";

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

// ---- Payments ----

export function createPayment(payload) {
    return request("/payments", { method: "POST", body: payload });
}

// ---- Health ----

export async function checkBackendHealth() {
    return request("/health", { auth: false });
}
