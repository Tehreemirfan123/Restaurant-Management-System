import { useEffect, useRef, useState } from "react";
import { Link, useParams } from "react-router-dom";

import CustomerHeader from "../components/CustomerHeader";
import {
    getMenu,
    getOrder,
    getOrderFeedback,
    submitOrderFeedback,
} from "../services/api";

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

    const [feedback, setFeedback] = useState(null);
    const [rating, setRating] = useState(0);
    const [wouldReorder, setWouldReorder] = useState(true);
    const [comment, setComment] = useState("");
    const [fbError, setFbError] = useState("");

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
        // Check whether feedback was already left for this order.
        getOrderFeedback(id)
            .then((fb) => setFeedback(fb))
            .catch(() => setFeedback(null));
    }, [id]);

    async function handleSubmitFeedback() {
        setFbError("");
        if (!rating) {
            setFbError("Please pick a rating");
            return;
        }
        try {
            const fb = await submitOrderFeedback(id, {
                rating,
                would_reorder: wouldReorder,
                comment: comment.trim() || null,
            });
            setFeedback(fb);
        } catch (err) {
            setFbError(err.message || "Could not submit feedback");
        }
    }

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
        <div className="min-h-screen bg-cream-100">
            <CustomerHeader />

            <main className="max-w-2xl mx-auto p-4">
                {loading && <p className="text-gray-500">Loading order...</p>}

                {error && (
                    <div className="bg-white rounded-xl shadow-sm p-8 text-center">
                        <p className="text-red-600 mb-4">{error}</p>
                        <Link
                            to="/"
                            className="text-maroon-800 font-medium hover:underline"
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
                                                            ? "bg-maroon-700"
                                                            : "bg-gray-200"
                                                    }`}
                                                />
                                            )}
                                            <div
                                                className={`relative z-10 w-6 h-6 rounded-full flex items-center justify-center text-xs ${
                                                    done
                                                        ? "bg-maroon-700 text-white"
                                                        : "bg-gray-200 text-gray-400"
                                                }`}
                                            >
                                                {done ? "✓" : index + 1}
                                            </div>
                                            <span
                                                className={`mt-1.5 text-xs ${
                                                    done
                                                        ? "text-maroon-800 font-medium"
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

                            {Number(order.delivery_fee) > 0 && (
                                <div className="flex justify-between text-sm text-gray-500 mt-2">
                                    <span>Delivery</span>
                                    <span>
                                        Rs.{" "}
                                        {Number(order.delivery_fee).toFixed(0)}
                                    </span>
                                </div>
                            )}

                            <div className="border-t mt-3 pt-3 flex justify-between font-bold text-gray-800">
                                <span>Total</span>
                                <span>
                                    Rs. {Number(order.total_amount).toFixed(0)}
                                </span>
                            </div>

                            <p className="text-xs text-gray-400 mt-3 capitalize">
                                {order.order_type}
                                {order.delivery_address
                                    ? ` · ${order.delivery_address}`
                                    : ""}
                            </p>
                        </div>

                        {/* Feedback */}
                        <div className="bg-white rounded-xl shadow-sm p-5 mt-4">
                            {feedback ? (
                                <div className="text-center">
                                    <p className="font-semibold text-gray-800">
                                        Thanks for your feedback!
                                    </p>
                                    <p className="text-gold-500 text-lg mt-1">
                                        {"★".repeat(feedback.rating)}
                                        <span className="text-gray-300">
                                            {"★".repeat(5 - feedback.rating)}
                                        </span>
                                    </p>
                                </div>
                            ) : (
                                <>
                                    <h2 className="font-semibold text-gray-800 mb-2">
                                        How was your order?
                                    </h2>
                                    <div className="flex gap-1 mb-3">
                                        {[1, 2, 3, 4, 5].map((n) => (
                                            <button
                                                key={n}
                                                onClick={() => setRating(n)}
                                                className={`text-2xl ${
                                                    n <= rating
                                                        ? "text-gold-500"
                                                        : "text-gray-300"
                                                }`}
                                                aria-label={`${n} stars`}
                                            >
                                                ★
                                            </button>
                                        ))}
                                    </div>
                                    <label className="flex items-center gap-2 text-sm text-gray-700 mb-3">
                                        <input
                                            type="checkbox"
                                            checked={wouldReorder}
                                            onChange={(e) =>
                                                setWouldReorder(
                                                    e.target.checked
                                                )
                                            }
                                        />
                                        I would order again
                                    </label>
                                    <textarea
                                        value={comment}
                                        onChange={(e) =>
                                            setComment(e.target.value)
                                        }
                                        placeholder="Any comments? (optional)"
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"
                                    />
                                    {fbError && (
                                        <p className="text-red-600 text-sm mb-2">
                                            {fbError}
                                        </p>
                                    )}
                                    <button
                                        onClick={handleSubmitFeedback}
                                        className="w-full bg-maroon-700 hover:bg-maroon-800 text-white font-semibold py-2.5 rounded-lg"
                                    >
                                        Submit feedback
                                    </button>
                                </>
                            )}
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
