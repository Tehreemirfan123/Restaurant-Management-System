import { useEffect, useMemo, useState } from "react";

import { useCart } from "../context/CartContext";
import { getMenu, getOrderingStatus } from "../services/api";
import { whatsappUrl } from "../utils/whatsapp";

const DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
];

export default function CustomerMenu() {
    const { addItem, items } = useCart();

    const [menu, setMenu] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [accepting, setAccepting] = useState(true);

    const todayKey = new Date()
        .toLocaleDateString("en-US", { weekday: "long" })
        .toLowerCase();

    useEffect(() => {
        getMenu()
            .then((data) => setMenu((data || []).filter((i) => i.available)))
            .catch((err) => setError(err.message || "Failed to load menu"))
            .finally(() => setLoading(false));
        getOrderingStatus()
            .then((s) => setAccepting(s.accepting_orders))
            .catch(() => {});
    }, []);

    const byDay = useMemo(() => {
        const map = {};
        DAYS.forEach((d) => (map[d] = []));
        const specials = [];
        menu.forEach((item) => {
            if (item.day_of_week && map[item.day_of_week]) {
                map[item.day_of_week].push(item);
            } else if (!item.day_of_week) {
                specials.push(item);
            }
        });
        return { map, specials };
    }, [menu]);

    function qtyInCart(id) {
        return items.find((i) => i.id === id)?.quantity ?? 0;
    }

    function Dish({ item, orderable, special }) {
        const qty = qtyInCart(item.id);
        return (
            <div className="bg-cream-50 rounded-xl shadow-sm p-4 flex justify-between items-center gap-4">
                <div className="min-w-0">
                    <h3 className="font-semibold text-gray-800">{item.name}</h3>
                    {item.description && (
                        <p className="text-sm text-gray-500 mt-0.5">
                            {item.description}
                        </p>
                    )}
                    {/* Advance-order specials never show a price. */}
                    {special ? (
                        <span className="text-gold-600 font-medium text-sm mt-1 inline-block">
                            Advance order — ask for details
                        </span>
                    ) : (
                        <span className="text-gold-600 font-semibold text-sm mt-1 inline-block">
                            Rs. {Number(item.price).toFixed(0)}
                        </span>
                    )}
                </div>
                {special ? (
                    <a
                        href={whatsappUrl(
                            `Hi Mehak's Kitchen, I'd like to ask about ${item.name} (advance order).`
                        )}
                        target="_blank"
                        rel="noopener noreferrer"
                        className="shrink-0 bg-[#25D366] hover:brightness-95 text-white text-sm font-medium px-4 py-2 rounded-lg"
                    >
                        Ask on WhatsApp
                    </a>
                ) : orderable && accepting ? (
                    <button
                        onClick={() => addItem(item)}
                        className="shrink-0 bg-maroon-700 hover:bg-maroon-800 text-white text-sm font-medium px-4 py-2 rounded-lg"
                    >
                        {qty > 0 ? `Add (${qty})` : "Add"}
                    </button>
                ) : (
                    <span className="shrink-0 text-xs text-gray-400">
                        {orderable ? "Closed" : "Not today"}
                    </span>
                )}
            </div>
        );
    }

    return (
        <div className="max-w-3xl mx-auto px-4 py-8">
            <div className="text-center mb-6">
                <h1 className="text-2xl font-bold text-maroon-700">
                    Our Weekly Menu
                </h1>
                <p className="text-sm text-gray-500 mt-1">
                    One fresh main dish for every day of the week. Today&apos;s
                    dish is ready to order.
                </p>
            </div>

            {!accepting && (
                <div className="bg-red-50 border border-red-200 text-red-700 rounded-xl p-4 mb-4 text-center text-sm">
                    We&apos;re not taking orders right now. Please check back
                    later.
                </div>
            )}

            {loading && <p className="text-gray-500">Loading menu...</p>}
            {error && <p className="text-red-600">{error}</p>}

            {!loading && !error && menu.length === 0 && (
                <p className="text-gray-500 text-center py-8">
                    Our menu is being updated — please check back soon.
                </p>
            )}

            {!loading &&
                DAYS.map((day) => {
                    const dishes = byDay.map[day];
                    if (!dishes.length) return null;
                    const isToday = day === todayKey;
                    return (
                        <section key={day} className="mb-6">
                            <div className="flex items-center gap-2 mb-2">
                                <h2 className="text-lg font-bold text-maroon-700 capitalize">
                                    {day}
                                </h2>
                                {isToday && (
                                    <span className="text-xs bg-gold-500 text-maroon-900 font-semibold px-2 py-0.5 rounded-full">
                                        Today
                                    </span>
                                )}
                            </div>
                            <div className="space-y-3">
                                {dishes.map((item) => (
                                    <Dish
                                        key={item.id}
                                        item={item}
                                        orderable={isToday}
                                    />
                                ))}
                            </div>
                        </section>
                    );
                })}

            {byDay.specials.length > 0 && (
                <section className="mb-6">
                    <h2 className="text-lg font-bold text-maroon-700 mb-2">
                        Specials (advance order)
                    </h2>
                    <div className="space-y-3">
                        {byDay.specials.map((item) => (
                            <Dish key={item.id} item={item} special />
                        ))}
                    </div>
                </section>
            )}
        </div>
    );
}
