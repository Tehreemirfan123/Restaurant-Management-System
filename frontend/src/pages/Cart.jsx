import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import CustomerHeader from "../components/CustomerHeader";
import { useCart } from "../context/CartContext";
import { createOrder } from "../services/api";

const DELIVERY_FEE = 80;

export default function Cart() {
    const { items, setQuantity, removeItem, clearCart, totalAmount } =
        useCart();
    const navigate = useNavigate();

    const [orderType, setOrderType] = useState("pickup");
    const [address, setAddress] = useState("");
    const [placing, setPlacing] = useState(false);
    const [error, setError] = useState("");

    const deliveryFee = orderType === "delivery" ? DELIVERY_FEE : 0;
    const grandTotal = totalAmount + deliveryFee;

    async function handleCheckout() {
        setError("");

        if (orderType === "delivery" && !address.trim()) {
            setError("Please enter a delivery address");
            return;
        }

        setPlacing(true);

        try {
            const order = await createOrder({
                order_type: orderType,
                delivery_address:
                    orderType === "delivery" ? address.trim() : null,
                items: items.map((i) => ({
                    menu_item_id: i.id,
                    quantity: i.quantity,
                })),
            });

            clearCart();
            navigate(`/order/${order.id}`, { replace: true });
        } catch (err) {
            setError(err.message || "Could not place your order");
        } finally {
            setPlacing(false);
        }
    }

    return (
        <div className="min-h-screen bg-cream-100">
            <CustomerHeader />

            <main className="max-w-2xl mx-auto p-4">
                <h1 className="text-xl font-bold text-gray-800 mb-4">
                    Your Cart
                </h1>

                {items.length === 0 ? (
                    <div className="bg-white rounded-xl shadow-sm p-8 text-center">
                        <p className="text-gray-500 mb-4">
                            Your cart is empty.
                        </p>
                        <Link
                            to="/"
                            className="text-maroon-800 font-medium hover:underline"
                        >
                            Browse the menu
                        </Link>
                    </div>
                ) : (
                    <>
                        <div className="space-y-3">
                            {items.map((item) => (
                                <div
                                    key={item.id}
                                    className="bg-white rounded-xl shadow-sm p-4 flex items-center gap-3"
                                >
                                    <div className="flex-1 min-w-0">
                                        <h3 className="font-semibold text-gray-800">
                                            {item.name}
                                        </h3>
                                        <span className="text-sm text-gray-500">
                                            Rs. {item.price.toFixed(0)} each
                                        </span>
                                    </div>

                                    <div className="flex items-center gap-2">
                                        <button
                                            onClick={() =>
                                                setQuantity(
                                                    item.id,
                                                    item.quantity - 1
                                                )
                                            }
                                            className="w-8 h-8 rounded-full bg-gold-100 text-maroon-800 font-bold"
                                            aria-label="Decrease"
                                        >
                                            −
                                        </button>
                                        <span className="w-6 text-center font-medium">
                                            {item.quantity}
                                        </span>
                                        <button
                                            onClick={() =>
                                                setQuantity(
                                                    item.id,
                                                    item.quantity + 1
                                                )
                                            }
                                            className="w-8 h-8 rounded-full bg-gold-100 text-maroon-800 font-bold"
                                            aria-label="Increase"
                                        >
                                            +
                                        </button>
                                    </div>

                                    <div className="w-20 text-right font-semibold text-gray-800">
                                        Rs.{" "}
                                        {(item.price * item.quantity).toFixed(0)}
                                    </div>

                                    <button
                                        onClick={() => removeItem(item.id)}
                                        className="text-red-500 hover:text-red-600 text-sm"
                                        aria-label="Remove"
                                    >
                                        ✕
                                    </button>
                                </div>
                            ))}
                        </div>

                        <div className="bg-white rounded-xl shadow-sm p-4 mt-4">
                            {/* Pickup / delivery choice */}
                            <div className="flex gap-2 mb-3">
                                {[
                                    { key: "pickup", label: "Pickup" },
                                    { key: "delivery", label: "Delivery" },
                                ].map((t) => (
                                    <button
                                        key={t.key}
                                        onClick={() => setOrderType(t.key)}
                                        className={`flex-1 py-2 rounded-lg text-sm font-medium ${
                                            orderType === t.key
                                                ? "bg-maroon-700 text-white"
                                                : "bg-cream-100 text-maroon-800"
                                        }`}
                                    >
                                        {t.label}
                                    </button>
                                ))}
                            </div>

                            {orderType === "delivery" && (
                                <textarea
                                    value={address}
                                    onChange={(e) => setAddress(e.target.value)}
                                    placeholder="Delivery address (within 3 km)"
                                    className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-3"
                                />
                            )}

                            <div className="space-y-1 text-sm text-gray-600 mb-3">
                                <div className="flex justify-between">
                                    <span>Subtotal</span>
                                    <span>Rs. {totalAmount.toFixed(0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>Delivery</span>
                                    <span>
                                        {deliveryFee
                                            ? `Rs. ${deliveryFee}`
                                            : "—"}
                                    </span>
                                </div>
                            </div>

                            <div className="flex justify-between items-center text-lg font-bold text-gray-800 mb-4 border-t pt-3">
                                <span>Total</span>
                                <span>Rs. {grandTotal.toFixed(0)}</span>
                            </div>

                            {error && (
                                <p className="text-red-600 text-sm mb-3">
                                    {error}
                                </p>
                            )}

                            <button
                                onClick={handleCheckout}
                                disabled={placing}
                                className="w-full bg-maroon-700 hover:bg-maroon-800 disabled:opacity-60 text-white font-semibold py-3 rounded-lg"
                            >
                                {placing ? "Placing order..." : "Place Order"}
                            </button>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}
