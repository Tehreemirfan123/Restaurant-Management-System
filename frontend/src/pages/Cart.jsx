import { useEffect, useState } from "react";
import { Link, useNavigate } from "react-router-dom";

import {
    ADVANCE_PERCENT,
    DELIVERY_BASE_KM,
    DELIVERY_FEE,
    DELIVERY_PER_KM,
    LARGE_ORDER_THRESHOLD,
    ORDER_CATEGORIES,
    PAYMENT_GATEWAY_ENABLED,
    PAYMENT_METHODS,
} from "../config";
import { useCart } from "../context/CartContext";
import {
    createOrder,
    getOrderingStatus,
    startCheckout,
} from "../services/api";
import {
    computeDeliveryFee,
    estimateDistanceFromLocation,
} from "../utils/delivery";
import { redirectToGateway } from "../utils/gateway";
import { buildWhatsappOrderUrl } from "../utils/whatsapp";

export default function Cart() {
    const { items, setQuantity, removeItem, clearCart, totalAmount } =
        useCart();
    const navigate = useNavigate();

    const [orderType, setOrderType] = useState("pickup");
    const [address, setAddress] = useState("");
    const [name, setName] = useState("");
    const [phone, setPhone] = useState("");
    const [distance, setDistance] = useState("");
    const [locating, setLocating] = useState(false);
    const [category, setCategory] = useState("regular");
    const [payMethod, setPayMethod] = useState("cash");
    // Changes in delivery charges in the code
    const [cfg, setCfg] = useState({
        baseFee: DELIVERY_FEE,
        baseKm: DELIVERY_BASE_KM,
        perKm: DELIVERY_PER_KM,
    });
    const [pay, setPay] = useState({
        advancePercent: ADVANCE_PERCENT,
        largeThreshold: LARGE_ORDER_THRESHOLD,
        bank_name: null,
        bank_account_name: null,
        bank_account_number: null,
        jazzcash_number: null,
        easypaisa_number: null,
    });
    const [placing, setPlacing] = useState(false);
    const [error, setError] = useState("");

    useEffect(() => {
        getOrderingStatus()
            .then((s) => {
                setCfg({
                    baseFee:
                        s?.delivery_fee != null
                            ? Number(s.delivery_fee)
                            : DELIVERY_FEE,
                    baseKm:
                        s?.delivery_radius_km != null
                            ? Number(s.delivery_radius_km)
                            : DELIVERY_BASE_KM,
                    perKm:
                        s?.delivery_per_km != null
                            ? Number(s.delivery_per_km)
                            : DELIVERY_PER_KM,
                });
                setPay({
                    advancePercent:
                        s?.advance_payment_percent != null
                            ? Number(s.advance_payment_percent)
                            : ADVANCE_PERCENT,
                    largeThreshold:
                        s?.large_order_threshold != null
                            ? Number(s.large_order_threshold)
                            : LARGE_ORDER_THRESHOLD,
                    bank_name: s?.bank_name || null,
                    bank_account_name: s?.bank_account_name || null,
                    bank_account_number: s?.bank_account_number || null,
                    jazzcash_number: s?.jazzcash_number || null,
                    easypaisa_number: s?.easypaisa_number || null,
                });
            })
            .catch(() => {});
    }, []);

    // Changes in delivery charges in the code
    const deliveryFee =
        orderType === "delivery" ? computeDeliveryFee(distance, cfg) : 0;
    const grandTotal = totalAmount + deliveryFee;

    // Advance rule: custom/subscription orders, or any order at/over the
    // large-order threshold, need an advance. Regular small orders can use COD.
    const advanceRequired =
        category !== "regular" ||
        (pay.largeThreshold > 0 && grandTotal >= pay.largeThreshold);
    const advanceAmount = advanceRequired
        ? Math.round((grandTotal * pay.advancePercent) / 100)
        : 0;
    const selectedMethod = PAYMENT_METHODS.find((m) => m.key === payMethod);
    const needsDigitalForAdvance = advanceRequired && !selectedMethod?.digital;
    // Gateway is off for now, so JazzCash/Easypaisa/bank are arranged over
    // WhatsApp. Flip PAYMENT_GATEWAY_ENABLED to bring back hosted checkout.
    const onlineMethod =
        PAYMENT_GATEWAY_ENABLED &&
        (payMethod === "jazzcash" || payMethod === "easypaisa");
    // Any non-cash method is settled over WhatsApp while the gateway is off.
    const arrangeViaWhatsapp = selectedMethod?.digital && !onlineMethod;

    // Account to send a manual payment to, for the chosen method (if set up
    // in Admin -> Settings).
    const payInstructions = (() => {
        if (payMethod === "bank_transfer" && pay.bank_account_number) {
            return `${pay.bank_name || "Bank"} — ${
                pay.bank_account_name || ""
            } ${pay.bank_account_number}`.trim();
        }
        if (payMethod === "jazzcash" && pay.jazzcash_number) {
            return `JazzCash ${pay.jazzcash_number}`;
        }
        if (payMethod === "easypaisa" && pay.easypaisa_number) {
            return `Easypaisa ${pay.easypaisa_number}`;
        }
        return null;
    })();

    async function useMyLocation() {
        setError("");
        setLocating(true);
        try {
            const km = await estimateDistanceFromLocation();
            setDistance(String(km));
        } catch (err) {
            setError(err.message || "Could not detect your location");
        } finally {
            setLocating(false);
        }
    }

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
            deliveryFee,
            distance: orderType === "delivery" ? distance : null,
            category,
            paymentMethod: selectedMethod?.label,
            advanceAmount,
        });
        window.open(url, "_blank", "noopener");
    }

    async function placeOrder(online) {
        setError("");

        if (orderType === "delivery" && !address.trim()) {
            setError("Please enter a delivery address");
            return;
        }
        if (!name.trim() || !phone.trim()) {
            setError("Please enter your name and phone");
            return;
        }
        // For a manual (non-gateway) checkout, an advance order must use a
        // digital method. The online path always satisfies this.
        if (!online && needsDigitalForAdvance) {
            setError(
                `This order needs a ${pay.advancePercent}% advance (Rs. ${advanceAmount}). ` +
                    "Please choose Bank Transfer, JazzCash or Easypaisa to pay it."
            );
            return;
        }

        setPlacing(true);

        try {
            const order = await createOrder({
                order_type: orderType,
                category,
                // Online orders record the payment via the gateway callback,
                // so we don't also create a pending "intent" here.
                payment_method: online ? null : payMethod,
                delivery_address:
                    orderType === "delivery" ? address.trim() : null,
                // Changes in delivery charges in the code
                delivery_distance_km:
                    orderType === "delivery" && distance !== ""
                        ? Number(distance)
                        : null,
                customer_name: name.trim(),
                customer_phone: phone.trim(),
                items: items.map((i) => ({
                    menu_item_id: i.id,
                    quantity: i.quantity,
                })),
            });

            if (online) {
                // Hand off to the gateway; it returns the customer to the
                // order page after paying.
                const checkout = await startCheckout({
                    order_id: order.id,
                    method: payMethod,
                });
                clearCart();
                redirectToGateway(checkout);
                return;
            }

            clearCart();
            navigate(`/order/${order.id}`, { replace: true });
        } catch (err) {
            setError(err.message || "Could not place your order");
            setPlacing(false);
        }
    }

    const handleCheckout = () => placeOrder(false);
    const handlePayOnline = () => placeOrder(true);

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
                            to="/menu"
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
                                            className="w-8 h-8 rounded-full bg-gold-100 text-maroon-900 font-bold"
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
                                            className="w-8 h-8 rounded-full bg-gold-100 text-maroon-900 font-bold"
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
                                <>
                                    <textarea
                                        value={address}
                                        onChange={(e) =>
                                            setAddress(e.target.value)
                                        }
                                        placeholder="Delivery address"
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-2"
                                    />
                                    {/* Changes in delivery charges in the code */}
                                    <div className="flex gap-2 mb-1">
                                        <input
                                            type="number"
                                            min="0"
                                            step="0.1"
                                            value={distance}
                                            onChange={(e) =>
                                                setDistance(e.target.value)
                                            }
                                            placeholder="Distance from us (km)"
                                            className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm"
                                        />
                                        <button
                                            type="button"
                                            onClick={useMyLocation}
                                            disabled={locating}
                                            className="shrink-0 text-sm border border-maroon-700 text-maroon-700 rounded-lg px-3 py-2 disabled:opacity-60"
                                        >
                                            {locating ? "Locating…" : "Use my location"}
                                        </button>
                                    </div>
                                    <p className="text-xs text-gray-400 mb-3">
                                        First {cfg.baseKm} km: Rs. {cfg.baseFee}.
                                        Beyond that: Rs. {cfg.perKm}/km.
                                    </p>
                                </>
                            )}

                            {/* Order kind */}
                            <p className="text-xs font-medium text-gray-500 mb-1">
                                Order type
                            </p>
                            <div className="flex flex-wrap gap-2 mb-3">
                                {ORDER_CATEGORIES.map((c) => (
                                    <button
                                        key={c.key}
                                        onClick={() => setCategory(c.key)}
                                        className={`flex-1 min-w-24 py-2 rounded-lg text-sm font-medium ${
                                            category === c.key
                                                ? "bg-maroon-700 text-white"
                                                : "bg-cream-100 text-maroon-800"
                                        }`}
                                    >
                                        {c.label}
                                    </button>
                                ))}
                            </div>

                            {/* Payment method */}
                            <p className="text-xs font-medium text-gray-500 mb-1">
                                Payment method
                            </p>
                            <div className="grid grid-cols-2 gap-2 mb-3">
                                {PAYMENT_METHODS.map((m) => (
                                    <button
                                        key={m.key}
                                        onClick={() => setPayMethod(m.key)}
                                        className={`py-2 rounded-lg text-sm font-medium ${
                                            payMethod === m.key
                                                ? "bg-maroon-700 text-white"
                                                : "bg-cream-100 text-maroon-800"
                                        }`}
                                    >
                                        {m.label}
                                    </button>
                                ))}
                            </div>

                            {/* Advance notice */}
                            {advanceRequired && (
                                <div className="mb-3 rounded-lg bg-gold-100 text-maroon-900 text-sm p-3">
                                    <p className="font-semibold">
                                        {pay.advancePercent}% advance required:
                                        Rs. {advanceAmount}
                                    </p>
                                    <p className="mt-1 text-maroon-900">
                                        {category === "subscription"
                                            ? "Subscription orders"
                                            : category === "custom"
                                            ? "Custom orders"
                                            : "Large orders"}{" "}
                                        are confirmed once the advance is
                                        received.
                                    </p>
                                    {arrangeViaWhatsapp && payInstructions && (
                                        <p className="mt-2">
                                            Send the advance to:{" "}
                                            <span className="font-medium">
                                                {payInstructions}
                                            </span>
                                            , then share the screenshot on
                                            WhatsApp.
                                        </p>
                                    )}
                                    {arrangeViaWhatsapp && !payInstructions && (
                                        <p className="mt-2">
                                            Arrange the advance with us on
                                            WhatsApp.
                                        </p>
                                    )}
                                    {onlineMethod && (
                                        <p className="mt-2">
                                            You&apos;ll be redirected to pay the
                                            advance securely via{" "}
                                            {selectedMethod.label}.
                                        </p>
                                    )}
                                    {needsDigitalForAdvance && (
                                        <p className="mt-2 text-red-700">
                                            Choose Bank Transfer, JazzCash or
                                            Easypaisa to pay the advance.
                                        </p>
                                    )}
                                </div>
                            )}

                            {/* Payment instructions for non-advance orders */}
                            {!advanceRequired && arrangeViaWhatsapp && (
                                <p className="mb-3 text-xs text-gray-500">
                                    {payInstructions ? (
                                        <>
                                            Send Rs. {grandTotal.toFixed(0)} to{" "}
                                            <span className="font-medium">
                                                {payInstructions}
                                            </span>{" "}
                                            and share the screenshot on WhatsApp.
                                        </>
                                    ) : (
                                        <>
                                            Arrange your {selectedMethod.label}{" "}
                                            payment with us on WhatsApp.
                                        </>
                                    )}
                                </p>
                            )}
                            {!advanceRequired && onlineMethod && (
                                <p className="mb-3 text-xs text-gray-500">
                                    You&apos;ll be redirected to pay securely via{" "}
                                    {selectedMethod.label}.
                                </p>
                            )}

                            <div className="space-y-1 text-sm text-gray-600 mb-3">
                                <div className="flex justify-between">
                                    <span>Subtotal</span>
                                    <span>Rs. {totalAmount.toFixed(0)}</span>
                                </div>
                                <div className="flex justify-between">
                                    <span>
                                        Delivery
                                        {orderType === "delivery" &&
                                        distance !== ""
                                            ? ` (${distance} km)`
                                            : ""}
                                    </span>
                                    <span>
                                        {orderType === "delivery"
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
                                or place your order here
                            </p>

                            {onlineMethod ? (
                                <button
                                    onClick={handlePayOnline}
                                    disabled={placing}
                                    className="w-full bg-maroon-700 hover:bg-maroon-800 disabled:opacity-60 text-white font-semibold py-3 rounded-lg"
                                >
                                    {placing
                                        ? "Redirecting…"
                                        : `Place order & pay ${
                                              advanceRequired
                                                  ? `advance Rs. ${advanceAmount}`
                                                  : `Rs. ${grandTotal.toFixed(
                                                        0
                                                    )}`
                                          }`}
                                </button>
                            ) : (
                                <button
                                    onClick={handleCheckout}
                                    disabled={placing}
                                    className="w-full border border-maroon-700 text-maroon-700 hover:bg-cream-100 disabled:opacity-60 font-semibold py-3 rounded-lg"
                                >
                                    {placing ? "Placing order..." : "Place Order"}
                                </button>
                            )}
                        </div>
                    </>
                )}
            </main>
    );
}
