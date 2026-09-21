import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import CustomerHeader from "../components/CustomerHeader";
import { getMenu, getOrder } from "../services/api";

const STEPS = [
    { key: "received", label: "Received" },
    { key: "preparing", label: "Preparing" },
    { key: "ready", label: "Ready" },
    { key: "delivered", label: "Delivered" },
];

export default function OrderTracking() {
    const { id } = useParams();

    const [order, setOrder] = useState(null);
    const [names, setNames] = useState({});
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    const intervalRef = useRef(null);

    useEffect(() => {
        // Menu is loaded once so we can show item names against the order lines.
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
        let active = true;

        async function load() {
            try {
                const data = await getOrder(id);
                if (active) {
                    setOrder(data);
                    setError("");
                }
            } catch (err) {
                if (active) setError(err.message || "Order not found");
            } finally {
                if (active) setLoading(false);
            }
        }

        load();

        // Poll for status changes while the order is in progress.
        intervalRef.current = setInterval(load, 5000);

        return () => {
            active = false;
            clearInterval(intervalRef.current);
        };
    }, [id]);

    // Stop polling once the order is delivered.
    useEffect(() => {
        if (order?.status === "delivered" && intervalRef.current) {
            clearInterval(intervalRef.current);
        }
    }, [order?.status]);

    const currentStep = order
        ? STEPS.findIndex((s) => s.key === order.status)
        : -1;

    return (
        <div className="min-h-screen bg-amber-50">
            <CustomerHeader />

            <main className="max-w-2xl mx-auto p-4">
                {loading && <p className="text-gray-500">Loading order...</p>}

                {error && (
                    <div className="bg-white rounded-xl shadow-sm p-8 text-center">
                        <p className="text-red-600 mb-4">{error}</p>
                        <Link
                            to="/"
                            className="text-amber-700 font-medium hover:underline"
                        >
                            Back to menu
                        </Link>
                    </div>
                )}

                {order && !error && (
                    <>
                        <div className="bg-white rounded-xl shadow-sm p-5 mb-4">
                            <p className="text-sm text-gray-500">Order</p>
                            <p className="font-mono text-sm text-gray-700 mb-4">
                                #{order.id.slice(0, 8)}
                            </p>

                            {/* Status stepper */}
                            <div className="flex items-center">
                                {STEPS.map((step, index) => {
                                    const done = index <= currentStep;
                                    return (
                                        <div
                                            key={step.key}
                                            className="flex-1 flex flex-col items-center relative"
                                        >
                                            {index > 0 && (
                                                <div
                                                    className={`absolute right-1/2 top-3 h-0.5 w-full ${
                                                        index <= currentStep
                                                            ? "bg-amber-600"
                                                            : "bg-gray-200"
                                                    }`}
                                                />
                                            )}
                                            <div
                                                className={`relative z-10 w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                                                    done
                                                        ? "bg-amber-600 text-white"
                                                        : "bg-gray-200 text-gray-400"
                                                }`}
                                            >
                                                {done ? "✓" : index + 1}
                                            </div>
                                            <span
                                                className={`mt-1.5 text-xs ${
                                                    done
                                                        ? "text-amber-700 font-medium"
                                                        : "text-gray-400"
                                                }`}
                                            >
                                                {step.label}
                                            </span>
                                        </div>
                                    );
                                })}
                            </div>
                        </div>

                        <div className="bg-white rounded-xl shadow-sm p-5">
                            <h2 className="font-semibold text-gray-800 mb-3">
                                Order summary
                            </h2>
                            <div className="space-y-2">
                                {order.items.map((line) => (
                                    <div
                                        key={line.id}
                                        className="flex justify-between text-sm"
                                    >
                                        <span className="text-gray-700">
                                            {line.quantity} ×{" "}
                                            {names[line.menu_item_id] ||
                                                "Item"}
                                        </span>
                                        <span className="text-gray-600">
                                            Rs.{" "}
                                            {(
                                                Number(line.unit_price) *
                                                line.quantity
                                            ).toFixed(0)}
                                        </span>
                                    </div>
                                ))}
                            </div>
                            <div className="border-t mt-3 pt-3 flex justify-between font-bold text-gray-800">
                                <span>Total</span>
                                <span>
                                    Rs. {Number(order.total_amount).toFixed(0)}
                                </span>
                            </div>
                        </div>

                        <p className="text-center text-xs text-gray-400 mt-4">
                            This page updates automatically.
                        </p>
                    </>
                )}
            </main>
        </div>
    );
}
