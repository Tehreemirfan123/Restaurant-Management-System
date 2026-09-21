import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import { DELIVERY_FEE } from "../config";
import { useCart } from "../context/CartContext";
import { createOrder, getOrderingStatus } from "../services/api";
import { buildWhatsappOrderUrl } from "../utils/whatsapp";

export default function Cart() {
    const { items, setQuantity, removeItem, clearCart, totalAmount } =
        useCart();
    const navigate = useNavigate();

    const [orderType, setOrderType] = useState("pickup");
    const [address, setAddress] = useState("");
    const [name, setName] = useState("");
    const [phone, setPhone] = useState("");
    const [feeConfig, setFeeConfig] = useState(DELIVERY_FEE);
    const [placing, setPlacing] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        getOrderingStatus()
            .then((s) => {
                if (s?.delivery_fee != null) setFeeConfig(Number(s.delivery_fee));
            })
            .catch(() => {});
    }, []);

    const deliveryFee = orderType === "delivery" ? feeConfig : 0;
    const grandTotal = totalAmount + deliveryFee;

    function handleWhatsappOrder() {
        if (orderType === "delivery" && !address.trim()) {
            setError("Please enter a delivery address");
            return;
        }
        const url = buildWhatsappOrderUrl({
            items,
            orderType,
            address: address.trim(),
            name: name.trim(),
            phone: phone.trim(),
            deliveryFee: feeConfig,
        });
        window.open(url, "_blank", "noopener");
    }

    async function handleCheckout() {
        setError("");

        if (orderType === "delivery" && !address.trim()) {
            setError("Please enter a delivery address");
            return;
        }
        if (!name.trim() || !phone.trim()) {
            setError("Please enter your name and phone");
            return;
        }

        setPlacing(true);

        try {
            const order = await createOrder({
                order_type: orderType,
                delivery_address:
                    orderType === "delivery" ? address.trim() : null,
                customer_name: name.trim(),
                customer_phone: phone.trim(),
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
            <main className="max-w-2xl mx-auto p-4 py-8">
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
                            {/* Contact details */}
                            <div className="flex flex-col sm:flex-row gap-2 mb-3">
                                <input
                                    type="text"
                                    value={name}
                                    onChange={(e) => setName(e.target.value)}
                                    placeholder="Your name"
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                                />
                                <input
                                    type="tel"
                                    value={phone}
                                    onChange={(e) => setPhone(e.target.value)}
                                    placeholder="Phone"
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                                />
                            </div>

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
                                onClick={handleWhatsappOrder}
                                className="w-full bg-[#25D366] hover:brightness-95 text-white font-semibold py-3 rounded-lg flex items-center justify-center gap-2"
                            >
                                Order on WhatsApp
                            </button>

                            <p className="text-center text-xs text-gray-400 my-2">
                                or place it online
                            </p>

                            <button
                                onClick={handleCheckout}
                                disabled={placing}
                                className="w-full border border-maroon-700 text-maroon-700 hover:bg-cream-100 disabled:opacity-60 font-semibold py-3 rounded-lg"
                            >
                                {placing ? "Placing order..." : "Place Order"}
                            </button>
                        </div>
                    </>
                )}
            </main>
    );
}
