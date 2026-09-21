import { useEffect, useMemo, useState } from "react";

import CustomerHeader from "../components/CustomerHeader";
import { useCart } from "../context/CartContext";
import { getMenu } from "../services/api";

const CATEGORIES = [
    { key: "all", label: "All" },
    { key: "starters", label: "Starters" },
    { key: "mains", label: "Mains" },
    { key: "desserts", label: "Desserts" },
    { key: "drinks", label: "Drinks" },
];

export default function CustomerMenu() {
    const { addItem, items } = useCart();

    const [menu, setMenu] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [activeCategory, setActiveCategory] = useState("all");

    useEffect(() => {
        getMenu()
            .then((data) => setMenu(data || []))
            .catch((err) => setError(err.message || "Failed to load menu"))
            .finally(() => setLoading(false));
    }, []);

    const available = useMemo(
        () => menu.filter((i) => i.available),
        [menu]
    );

    const visible = useMemo(() => {
        if (activeCategory === "all") return available;
        return available.filter((i) => i.category === activeCategory);
    }, [available, activeCategory]);

    function quantityInCart(id) {
        return items.find((i) => i.id === id)?.quantity ?? 0;
    }

    return (
        <div className="min-h-screen bg-amber-50">
            <CustomerHeader />

            {/* Category filter */}
            <div className="bg-white border-b sticky top-[72px] z-10">
                <div className="max-w-3xl mx-auto px-4 py-3 flex gap-2 overflow-x-auto">
                    {CATEGORIES.map((cat) => (
                        <button
                            key={cat.key}
                            onClick={() => setActiveCategory(cat.key)}
                            className={`px-4 py-1.5 rounded-full text-sm whitespace-nowrap transition ${
                                activeCategory === cat.key
                                    ? "bg-amber-600 text-white"
                                    : "bg-amber-100 text-amber-800 hover:bg-amber-200"
                            }`}
                        >
                            {cat.label}
                        </button>
                    ))}
                </div>
            </div>

            <main className="max-w-3xl mx-auto p-4">
                {loading && <p className="text-gray-500">Loading menu...</p>}
                {error && <p className="text-red-600">{error}</p>}

                {!loading && !error && visible.length === 0 && (
                    <p className="text-gray-500 py-8 text-center">
                        Nothing here right now.
                    </p>
                )}

                <div className="space-y-3">
                    {visible.map((item) => {
                        const qty = quantityInCart(item.id);
                        return (
                            <div
                                key={item.id}
                                className="bg-white rounded-xl shadow-sm p-4 flex justify-between items-center gap-4"
                            >
                                <div className="min-w-0">
                                    <h3 className="font-semibold text-gray-800">
                                        {item.name}
                                    </h3>
                                    {item.description && (
                                        <p className="text-sm text-gray-500 mt-0.5 line-clamp-2">
                                            {item.description}
                                        </p>
                                    )}
                                    <span className="text-amber-700 font-semibold text-sm mt-1 inline-block">
                                        Rs. {Number(item.price).toFixed(0)}
                                    </span>
                                </div>

                                <button
                                    onClick={() => addItem(item)}
                                    className="shrink-0 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium px-4 py-2 rounded-lg"
                                >
                                    {qty > 0 ? `Add (${qty})` : "Add"}
                                </button>
                            </div>
                        );
                    })}
                </div>
            </main>
        </div>
    );
}
