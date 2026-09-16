import { useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

export default function StaffHeader({ title }) {
    const { staff, logout } = useAuth();
    const navigate = useNavigate();

    function handleLogout() {
        logout();
        navigate("/login", { replace: true });
    }

    return (
        <header className="flex items-center justify-between bg-white border-b px-6 py-3 shadow-sm">
            <h1 className="text-lg font-semibold text-gray-800">{title}</h1>
            <div className="flex items-center gap-4 text-sm">
                <span className="text-gray-600">
                    {staff?.full_name}{" "}
                    <span className="text-gray-400">({staff?.role})</span>
                </span>
                <button
                    onClick={handleLogout}
                    className="text-red-600 hover:text-red-700 font-medium"
                >
                    Logout
                </button>
            </div>
        </header>
    );
}
