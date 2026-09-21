import { useCallback, useEffect, useRef, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import { getMenu, getOrders, updateOrderStatus } from "../services/api";

// The order a ticket moves through, and what the "advance" button says.
const NEXT_STATUS = {
    received: "preparing",
    preparing: "ready",
    ready: "delivered",
};

const NEXT_LABEL = {
    received: "Start preparing",
    preparing: "Mark ready",
    ready: "Mark delivered",
};

const STATUS_BADGE = {
    received: "bg-blue-100 text-blue-800",
    preparing: "bg-gold-100 text-maroon-800",
    ready: "bg-green-100 text-green-800",
};

export default function Kitchen() {
    const [orders, setOrders] = useState([]);
    const [names, setNames] = useState({});
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);
    const intervalRef = useRef(null);

    const load = useCallback(async () => {
        try {
            const data = await getOrders();
            // Only show tickets the kitchen still needs to act on.
            setOrders(
                (data || []).filter((o) => o.status !== "delivered")
            );
            setError("");
        } catch (err) {
            setError(err.message || "Failed to load orders");
        } finally {
            setLoading(false);
        }
    }, []);

    useEffect(() => {
        getMenu()
            .then((menu) => {
                const map = {};
                (menu || []).forEach((m) => {
                    map[m.id] = m.name;
                });
                setNames(map);
            })
            .catch(() => {});
    }, []);

    useEffect(() => {
        load();
        intervalRef.current = setInterval(load, 5000);
        return () => clearInterval(intervalRef.current);
    }, [load]);

    async function advance(order) {
        const next = NEXT_STATUS[order.status];
        if (!next) return;

        try {
            await updateOrderStatus(order.id, next);
            await load();
        } catch (err) {
            setError(err.message || "Could not update order");
        }
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Kitchen" />

            <main className="max-w-5xl mx-auto p-6">
                {error && <p className="text-red-600 mb-4">{error}</p>}

                {!loading && orders.length === 0 && (
                    <p className="text-gray-500 text-center py-12">
                        No active orders right now.
                    </p>
                )}

                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-3">
                    {orders.map((order) => (
                        <div
                            key={order.id}
                            className="bg-white rounded-xl shadow-sm p-4 flex flex-col"
                        >
                            <div className="flex items-center justify-between mb-2">
                                <span className="font-mono text-sm text-gray-600">
                                    #{order.id.slice(0, 8)}
                                </span>
                                <span
                                    className={`text-xs px-2 py-0.5 rounded-full capitalize ${
                                        STATUS_BADGE[order.status] || ""
                                    }`}
                                >
                                    {order.status}
                                </span>
                            </div>

                            <p className="text-xs text-gray-400 mb-2 capitalize">
                                {order.order_type.replace("_", "-")}
                            </p>

                            <ul className="text-sm text-gray-700 space-y-1 flex-1">
                                {order.items.map((line) => (
                                    <li key={line.id}>
                                        {line.quantity} ×{" "}
                                        {names[line.menu_item_id] || "Item"}
                                    </li>
                                ))}
                            </ul>

                            {NEXT_STATUS[order.status] && (
                                <button
                                    onClick={() => advance(order)}
                                    className="mt-3 bg-maroon-700 hover:bg-maroon-800 text-white text-sm font-medium py-2 rounded-lg"
                                >
                                    {NEXT_LABEL[order.status]}
                                </button>
                            )}
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
