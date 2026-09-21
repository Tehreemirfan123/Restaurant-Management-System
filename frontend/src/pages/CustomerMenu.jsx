import { useEffect, useState } from "react";

import CustomerHeader from "../components/CustomerHeader";
import { DISPLAY_PHONE } from "../config";
import { useCart } from "../context/CartContext";
import { getOrderingStatus, getTodaysMenu } from "../services/api";
import { whatsappUrl } from "../utils/whatsapp";

export default function CustomerMenu() {
    const { addItem, items } = useCart();

    const [menu, setMenu] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [accepting, setAccepting] = useState(true);

    const today = new Date().toLocaleDateString(undefined, {
        weekday: "long",
    });

    useEffect(() => {
        getTodaysMenu()
            .then((data) => setMenu(data || []))
            .catch((err) => setError(err.message || "Failed to load menu"))
            .finally(() => setLoading(false));
        getOrderingStatus()
            .then((s) => setAccepting(s.accepting_orders))
            .catch(() => {});
    }, []);

    function quantityInCart(id) {
        return items.find((i) => i.id === id)?.quantity ?? 0;
    }

    return (
        <div className="min-h-screen bg-cream-100">
            <CustomerHeader />

            <main className="max-w-3xl mx-auto p-4">
                <div className="text-center my-6">
                    <p className="text-sm text-gold-600 font-medium uppercase tracking-wide">
                        {today}&apos;s Menu
                    </p>
                    <h1 className="text-2xl font-bold text-maroon-700">
                        Fresh Homemade Meals
                    </h1>
                    <p className="text-sm text-gray-500 mt-1">
                        One day, one main dish — prepared fresh daily.
                    </p>
                </div>

                {!accepting && (
                    <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-4 text-center text-sm">
                        We&apos;re not taking orders right now. Please check
                        back later.
                    </div>
                )}

                {loading && <p className="text-gray-500">Loading menu...</p>}
                {error && <p className="text-red-600">{error}</p>}

                {!loading && !error && menu.length === 0 && (
                    <p className="text-gray-500 py-8 text-center">
                        Nothing on the menu right now — check back soon.
                    </p>
                )}

                <div className="space-y-3">
                    {menu.map((item) => {
                        const qty = quantityInCart(item.id);
                        return (
                            <div
                                key={item.id}
                                className="bg-cream-50 rounded-xl shadow-sm p-4 flex justify-between items-center gap-4"
                            >
                                <div className="min-w-0">
                                    <h3 className="font-semibold text-gray-800">
                                        {item.name}
                                    </h3>
                                    {item.description && (
                                        <p className="text-sm text-gray-500 mt-0.5">
                                            {item.description}
                                        </p>
                                    )}
                                    <span className="text-gold-600 font-semibold text-sm mt-1 inline-block">
                                        Rs. {Number(item.price).toFixed(0)}
                                    </span>
                                </div>

                                <button
                                    onClick={() => addItem(item)}
                                    className="shrink-0 bg-maroon-700 hover:bg-maroon-800 text-white text-sm font-medium px-4 py-2 rounded-lg"
                                >
                                    {qty > 0 ? `Add (${qty})` : "Add"}
                                </button>
                            </div>
                        );
                    })}
                </div>

                {/* Contact / info */}
                <footer className="mt-10 border-t border-cream-200 pt-6 text-center text-sm text-gray-500 space-y-1">
                    <p className="font-semibold text-maroon-700">
                        Mehak&apos;s Kitchen
                    </p>
                    <p>Open daily 11:00 AM – 11:00 PM · Pickup &amp; delivery</p>
                    <p>Delivery Rs. 80 within 3 km</p>
                    <a
                        href={whatsappUrl("Hi Mehak's Kitchen, I'd like to order today's menu.")}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="inline-block mt-2 text-[#25D366] font-semibold"
                    >
                        Order on WhatsApp · {DISPLAY_PHONE}
                    </a>
                </footer>
            </main>
        </div>
    );
}
