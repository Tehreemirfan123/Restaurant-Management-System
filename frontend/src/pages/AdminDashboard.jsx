import { Link } from "react-router-dom";

import StaffHeader from "../components/StaffHeader";

const TILES = [
    { label: "Menu Management", to: "/admin/menu", desc: "Add and edit dishes" },
    { label: "Inventory", to: "/admin/inventory", desc: "Track stock levels" },
    { label: "Recipes", to: "/admin/recipes", desc: "Ingredients per dish" },
    { label: "Staff", to: "/admin/staff", desc: "Manage team accounts" },
    { label: "Customers", to: "/admin/customers", desc: "Segments & repeat orders" },
    { label: "Reports", to: "/admin/reports", desc: "Sales & performance" },
];

export default function AdminDashboard() {
    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Admin Dashboard" />
            <main className="max-w-4xl mx-auto p-6">
                <p className="text-gray-600 mb-4">
                    Welcome to the admin console.
                </p>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {TILES.map((t) => (
                        <Link
                            key={t.label}
                            to={t.to}
                            className="bg-white rounded-xl shadow-sm p-6 hover:ring-2 hover:ring-gold-500 transition"
                        >
                            <h2 className="text-base font-semibold text-gray-800">
                                {t.label}
                            </h2>
                            <span className="mt-2 block text-xs text-gray-500">
                                {t.desc}
                            </span>
                        </Link>
                    ))}
                </div>
            </main>
        </div>
    );
}
