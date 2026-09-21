import { useCallback, useEffect, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import { cancelOrder, getOrders, updateOrderStatus } from "../services/api";

const STATUSES = ["received", "preparing", "ready", "delivered"];

const STATUS_BADGE = {
    received: "bg-blue-100 text-blue-800",
    preparing: "bg-gold-100 text-maroon-800",
    ready: "bg-green-100 text-green-800",
    delivered: "bg-gray-100 text-gray-600",
    cancelled: "bg-red-100 text-red-700",
};

const PAY_BADGE = {
    paid: "text-green-700",
    refunded: "text-red-600",
    pending: "text-gray-500",
    failed: "text-red-600",
};

export default function AdminOrders() {
    const [orders, setOrders] = useState([]);
    const [filter, setFilter] = useState("active");
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    const load = useCallback(() => {
        getOrders()
            .then((data) => setOrders(data || []))
            .catch((err) => setError(err.message || "Failed to load orders"))
            .finally(() => setLoading(false));
    }, []);

    useEffect(load, [load]);

    async function changeStatus(order, status) {
        try {
            await updateOrderStatus(order.id, status);
            load();
        } catch (err) {
            setError(err.message || "Could not update order");
        }
    }

    async function handleCancel(order) {
        if (!window.confirm("Cancel this order? A paid order will be refunded."))
            return;
        try {
            await cancelOrder(order.id);
            load();
        } catch (err) {
            setError(err.message || "Could not cancel order");
        }
    }

    const visible = orders.filter((o) => {
        if (filter === "all") return true;
        if (filter === "active")
            return o.status !== "delivered" && o.status !== "cancelled";
        return o.status === filter;
    });

    function fmt(iso) {
        return new Date(iso).toLocaleString();
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Orders" />

            <main className="max-w-5xl mx-auto p-6">
                <div className="flex gap-2 mb-4 flex-wrap">
                    {["active", "all", "delivered", "cancelled"].map((f) => (
                        <button
                            key={f}
                            onClick={() => setFilter(f)}
                            className={`px-3 py-1.5 rounded-full text-sm capitalize ${
                                filter === f
                                    ? "bg-maroon-700 text-white"
                                    : "bg-gold-100 text-maroon-800"
                            }`}
                        >
                            {f}
                        </button>
                    ))}
                </div>

                {error && <p className="text-red-600 mb-4">{error}</p>}
                {loading && <p className="text-gray-500">Loading...</p>}
                {!loading && visible.length === 0 && (
                    <p className="text-gray-500">No orders here.</p>
                )}

                <div className="space-y-2">
                    {visible.map((order) => (
                        <div
                            key={order.id}
                            className="bg-white rounded-xl shadow-sm p-4"
                        >
                            <div className="flex items-center justify-between flex-wrap gap-2">
                                <div>
                                    <span className="font-mono text-sm text-gray-600">
                                        #{order.id.slice(0, 8)}
                                    </span>
                                    <span
                                        className={`ml-2 text-xs px-2 py-0.5 rounded-full capitalize ${
                                            STATUS_BADGE[order.status] || ""
                                        }`}
                                    >
                                        {order.status}
                                    </span>
                                    <span className="ml-2 text-xs text-gray-400 capitalize">
                                        {order.order_type}
                                    </span>
                                </div>
                                <div className="text-right">
                                    <p className="font-semibold text-gray-800">
                                        Rs.{" "}
                                        {Number(order.total_amount).toFixed(0)}
                                    </p>
                                    <p
                                        className={`text-xs ${
                                            PAY_BADGE[order.payment_status] ||
                                            "text-gray-400"
                                        }`}
                                    >
                                        {order.payment_status || "unpaid"}
                                    </p>
                                </div>
                            </div>

                            <p className="text-sm text-gray-500 mt-1">
                                {order.customer_name || "Guest"}
                                {order.delivery_address
                                    ? ` · ${order.delivery_address}`
                                    : ""}
                            </p>
                            <p className="text-xs text-gray-400">
                                {fmt(order.created_at)}
                            </p>

                            {order.status !== "cancelled" && (
                                <div className="flex items-center gap-2 mt-3 flex-wrap">
                                    <select
                                        value={
                                            STATUSES.includes(order.status)
                                                ? order.status
                                                : ""
                                        }
                                        onChange={(e) =>
                                            changeStatus(order, e.target.value)
                                        }
                                        className="border border-gray-300 rounded-lg px-2 py-1 text-sm capitalize"
                                    >
                                        {STATUSES.map((s) => (
                                            <option key={s} value={s}>
                                                {s}
                                            </option>
                                        ))}
                                    </select>
                                    <button
                                        onClick={() => handleCancel(order)}
                                        className="text-sm text-red-600 hover:underline"
                                    >
                                        Cancel
                                    </button>
                                </div>
                            )}
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
