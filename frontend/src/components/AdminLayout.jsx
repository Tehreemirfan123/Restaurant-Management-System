import { NavLink, Outlet, useLocation, useNavigate } from "react-router-dom";

import { useAuth } from "../context/AuthContext";

const NAV = [
    { to: "/admin", label: "Dashboard", end: true },
    { to: "/admin/orders", label: "Orders" },
    { to: "/admin/payments", label: "Payments" },
    { to: "/admin/reports", label: "Reports" },
    { to: "/admin/menu", label: "Menu" },
    { to: "/admin/recipes", label: "Recipes" },
    { to: "/admin/inventory", label: "Inventory" },
    { to: "/admin/waste", label: "Waste" },
    { to: "/admin/customers", label: "Customers" },
    { to: "/admin/staff", label: "Staff" },
    { to: "/admin/settings", label: "Settings" },
];

function currentLabel(pathname) {
    // Longest matching nav path wins (so /admin/orders beats /admin).
    let match = NAV[0];
    for (const item of NAV) {
        if (item.to === "/admin") {
            if (pathname === "/admin") match = item;
        } else if (pathname.startsWith(item.to)) {
            match = item;
        }
    }
    return match.label;
}

export default function AdminLayout() {
    const { staff, logout } = useAuth();
    const navigate = useNavigate();
    const location = useLocation();

    function handleLogout() {
        logout();
        navigate("/login", { replace: true });
    }

    const title = currentLabel(location.pathname);

    return (
        <div className="min-h-screen bg-gray-100 flex flex-col md:flex-row">
            {/* Sidebar */}
            <aside className="no-print bg-maroon-800 text-white md:w-52 md:min-h-screen shrink-0">
                <div className="px-4 py-4 border-b border-white/10">
                    <p className="font-bold leading-tight">Mehak&apos;s Kitchen</p>
                    <p className="text-xs text-gold-200">Admin Console</p>
                </div>
                <nav className="flex md:flex-col gap-1 overflow-x-auto p-2">
                    {NAV.map((item) => (
                        <NavLink
                            key={item.to}
                            to={item.to}
                            end={item.end}
                            className={({ isActive }) =>
                                `px-3 py-2 rounded-lg text-sm whitespace-nowrap ${
                                    isActive
                                        ? "bg-white/15 text-white font-medium"
                                        : "text-gold-100 hover:bg-white/10"
                                }`
                            }
                        >
                            {item.label}
                        </NavLink>
                    ))}
                </nav>
            </aside>

            {/* Content */}
            <div className="flex-1 flex flex-col min-w-0">
                <header className="no-print flex items-center justify-between bg-white border-b px-4 md:px-6 py-3">
                    <div className="flex items-center gap-3">
                        <button
                            onClick={() => navigate(-1)}
                            aria-label="Back"
                            className="text-gray-500 hover:text-maroon-700 text-xl leading-none"
                        >
                            ←
                        </button>
                        <h1 className="text-lg font-semibold text-gray-800">
                            {title}
                        </h1>
                    </div>
                    <div className="flex items-center gap-4 text-sm">
                        <span className="text-gray-600 hidden sm:inline">
                            {staff?.full_name}{" "}
                            <span className="text-gray-400">
                                ({staff?.role})
                            </span>
                        </span>
                        <button
                            onClick={handleLogout}
                            className="text-red-600 hover:text-red-700 font-medium"
                        >
                            Logout
                        </button>
                    </div>
                </header>

                <div className="flex-1">
                    <Outlet />
                </div>
            </div>
        </div>
    );
}
