import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import { getMenu } from "../services/api";

const CATEGORY_ORDER = ["starters", "mains", "desserts", "drinks"];

export default function CustomerMenu() {
    const [items, setItems] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    useEffect(() => {
        getMenu()
            .then((data) => setItems(data || []))
            .catch((err) => setError(err.message || "Failed to load menu"))
            .finally(() => setLoading(false));
    }, []);

    const grouped = CATEGORY_ORDER.map((cat) => ({
        category: cat,
        items: items.filter((i) => i.category === cat && i.available),
    })).filter((g) => g.items.length > 0);

    return (
        <div className="min-h-screen bg-amber-50">
            <header className="bg-amber-600 text-white px-6 py-5 flex items-center justify-between">
                <div>
                    <h1 className="text-2xl font-bold">Mehak&apos;s Kitchen</h1>
                    <p className="text-amber-100 text-sm">Our Menu</p>
                </div>
                <Link
                    to="/login"
                    className="text-sm bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg"
                >
                    Staff Login
                </Link>
            </header>

            <main className="max-w-3xl mx-auto p-6">
                {loading && <p className="text-gray-500">Loading menu...</p>}
                {error && <p className="text-red-600">{error}</p>}

                {!loading && !error && grouped.length === 0 && (
                    <p className="text-gray-500">No menu items available yet.</p>
                )}

                {grouped.map((group) => (
                    <section key={group.category} className="mb-8">
                        <h2 className="text-lg font-bold text-amber-800 capitalize mb-3 border-b border-amber-200 pb-1">
                            {group.category}
                        </h2>
                        <div className="space-y-3">
                            {group.items.map((item) => (
                                <div
                                    key={item.id}
                                    className="bg-white rounded-xl shadow-sm p-4 flex justify-between items-start"
                                >
                                    <div className="pr-4">
                                        <h3 className="font-semibold text-gray-800">
                                            {item.name}
                                        </h3>
                                        {item.description && (
                                            <p className="text-sm text-gray-500 mt-0.5">
                                                {item.description}
                                            </p>
                                        )}
                                    </div>
                                    <span className="font-semibold text-amber-700 whitespace-nowrap">
                                        Rs. {Number(item.price).toFixed(0)}
                                    </span>
                                </div>
                            ))}
                        </div>
                    </section>
                ))}
            </main>
        </div>
    );
}
