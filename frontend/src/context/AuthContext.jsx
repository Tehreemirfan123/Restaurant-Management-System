import { createContext, useContext, useEffect, useState } from "react";

import {
    getCurrentStaff,
    getToken,
    login as apiLogin,
    setToken,
} from "../services/api";

const AuthContext = createContext(null);

export function AuthProvider({ children }) {
    const [staff, setStaff] = useState(null);
    const [loading, setLoading] = useState(true);

    // On mount, if a token exists, try to restore the session.
    useEffect(() => {
        const token = getToken();

        if (!token) {
            setLoading(false);
            return;
        }

        getCurrentStaff()
            .then((data) => setStaff(data))
            .catch(() => {
                setToken(null);
                setStaff(null);
            })
            .finally(() => setLoading(false));
    }, []);

    async function login(username, password) {
        const data = await apiLogin(username, password);
        setToken(data.access_token);
        const profile = await getCurrentStaff();
        setStaff(profile);
        return profile;
    }

    function logout() {
        setToken(null);
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
