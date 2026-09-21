import { createContext, useContext, useEffect, useState } from "react";

import {
    getCurrentStaff,
    getToken,
    login as apiLogin,
    setToken,
} from "../services/api";

const AuthContext = createContext(null);

const STAFF_KEY = "mk_staff";

function loadCachedStaff() {
    try {
        const raw = localStorage.getItem(STAFF_KEY);
        return raw ? JSON.parse(raw) : null;
    } catch {
        return null;
    }
}

function cacheStaff(staff) {
    try {
        if (staff) {
            localStorage.setItem(STAFF_KEY, JSON.stringify(staff));
        } else {
            localStorage.removeItem(STAFF_KEY);
        }
    } catch {
        // ignore storage errors
    }
}

export function AuthProvider({ children }) {
    // Restore optimistically from cache so a refresh doesn't bounce to login.
    const [staff, setStaff] = useState(() =>
        getToken() ? loadCachedStaff() : null
    );
    const [loading, setLoading] = useState(true);

    // On mount, refresh the profile in the background. Only log out if the
    // token is actually rejected (401) — not on transient/network errors.
    useEffect(() => {
        const token = getToken();

        if (!token) {
            setLoading(false);
            return;
        }

        getCurrentStaff()
            .then((data) => {
                setStaff(data);
                cacheStaff(data);
            })
            .catch((err) => {
                if (err?.status === 401) {
                    setToken(null);
                    cacheStaff(null);
                    setStaff(null);
                }
                // Other errors: keep the cached session as-is.
            })
            .finally(() => setLoading(false));
    }, []);

    async function login(username, password) {
        const data = await apiLogin(username, password);
        setToken(data.access_token);
        const profile = await getCurrentStaff();
        setStaff(profile);
        cacheStaff(profile);
        return profile;
    }

    function logout() {
        setToken(null);
        cacheStaff(null);
        setStaff(null);
    }

    const value = {
        staff,
        loading,
        isAuthenticated: Boolean(staff),
        isAdmin: staff?.role === "admin",
        login,
        logout,
    };

    return (
        <AuthContext.Provider value={value}>
            {children}
        </AuthContext.Provider>
    );
}

export function useAuth() {
    const ctx = useContext(AuthContext);
    if (!ctx) {
        throw new Error("useAuth must be used within an AuthProvider");
    }
    return ctx;
}
