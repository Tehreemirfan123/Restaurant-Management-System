import { useEffect, useMemo, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import { DELIVERY_BASE_KM, DELIVERY_FEE, DELIVERY_PER_KM } from "../config";
import {
    createOrder,
    createPayment,
    getMenu,
    getOrderingStatus,
} from "../services/api";
import { computeDeliveryFee } from "../utils/delivery";

const PAYMENT_METHODS = [
    { key: "cash", label: "Cash", digital: false },
    { key: "bank_transfer", label: "Bank", digital: true },
    { key: "jazzcash", label: "JazzCash", digital: true },
    { key: "easypaisa", label: "Easypaisa", digital: true },
    { key: "card", label: "Card", digital: true },
];

export default function POS() {
    const [menu, setMenu] = useState([]);
    const [lines, setLines] = useState([]);
    const [orderType, setOrderType] = useState("pickup");
    const [address, setAddress] = useState("");
    const [custName, setCustName] = useState("");
    const [custPhone, setCustPhone] = useState("");
    const [advance, setAdvance] = useState(false);
    const [reference, setReference] = useState("");
    const [distance, setDistance] = useState("");
    // Changes in delivery charges in the code
    const [cfg, setCfg] = useState({
        baseFee: DELIVERY_FEE,
        baseKm: DELIVERY_BASE_KM,
        perKm: DELIVERY_PER_KM,
    });
    const [error, setError] = useState("");

    // Workflow: "building" -> place order -> "payment" -> "done"
    const [stage, setStage] = useState("building");
    const [placedOrder, setPlacedOrder] = useState(null);
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        getMenu()
            .then((data) => setMenu((data || []).filter((m) => m.available)))
            .catch((err) => setError(err.message || "Failed to load menu"));
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
            })
            .catch(() => {});
    }, []);

    const subtotal = useMemo(
        () => lines.reduce((sum, l) => sum + l.price * l.quantity, 0),
        [lines]
    );

    // Changes in delivery charges in the code
    const deliveryFee =
        orderType === "delivery" ? computeDeliveryFee(distance, cfg) : 0;
    const total = subtotal + deliveryFee;

    function addLine(item) {
        setLines((current) => {
            const existing = current.find((l) => l.id === item.id);
            if (existing) {
                return current.map((l) =>
                    l.id === item.id
                        ? { ...l, quantity: l.quantity + 1 }
                        : l
                );
            }
            return [
                ...current,
                {
                    id: item.id,
                    name: item.name,
                    price: Number(item.price),
                    quantity: 1,
                },
            ];
        });
    }

    function changeQty(id, delta) {
        setLines((current) =>
            current
                .map((l) =>
                    l.id === id
                        ? { ...l, quantity: l.quantity + delta }
                        : l
                )
                .filter((l) => l.quantity > 0)
        );
    }

    function resetOrder() {
        setLines([]);
        setAddress("");
        setDistance("");
        setCustName("");
        setCustPhone("");
        setAdvance(false);
        setReference("");
        setOrderType("pickup");
        setPlacedOrder(null);
        setStage("building");
        setError("");
    }

    async function placeOrder() {
        setError("");

        if (lines.length === 0) {
            setError("Add at least one item");
            return;
        }
        if (orderType === "delivery" && !address.trim()) {
            setError("Enter a delivery address");
            return;
        }

        setBusy(true);
        try {
            const order = await createOrder({
                order_type: orderType,
                delivery_address:
                    orderType === "delivery" ? address.trim() : null,
                // Changes in delivery charges in the code
                delivery_distance_km:
                    orderType === "delivery" && distance !== ""
                        ? Number(distance)
                        : null,
                customer_name: custName.trim() || null,
                customer_phone: custPhone.trim() || null,
                items: lines.map((l) => ({
                    menu_item_id: l.id,
                    quantity: l.quantity,
                })),
            });

            setPlacedOrder(order);
            // Auto-select advance when the order rules require it.
            setAdvance(Boolean(order.advance_required));
            setStage("payment");
        } catch (err) {
            setError(err.message || "Could not place order");
        } finally {
            setBusy(false);
        }
    }

    // Advance amount comes from the backend rule (configurable percentage).
    const advanceAmount = placedOrder
        ? Number(placedOrder.advance_amount) ||
          Math.round(Number(placedOrder.total_amount) / 2)
        : 0;

    async function takePayment(method) {
        setError("");
        setBusy(true);
        try {
            const payload = { order_id: placedOrder.id, method };
            if (advance) {
                payload.amount = advanceAmount;
            }
            if (reference.trim()) {
                payload.reference = reference.trim();
            }
            await createPayment(payload);
            setStage("done");
        } catch (err) {
            setError(err.message || "Payment failed");
        } finally {
            setBusy(false);
        }
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Point of Sale" />

            <main className="max-w-6xl mx-auto p-4 grid gap-4 lg:grid-cols-3">
                {/* Menu grid */}
                <section className="lg:col-span-2">
                    <div className="grid gap-3 grid-cols-2 sm:grid-cols-3">
                        {menu.map((item) => (
                            <button
                                key={item.id}
                                onClick={() => addLine(item)}
                                disabled={stage !== "building"}
                                className="bg-white rounded-xl shadow-sm p-3 text-left hover:ring-2 hover:ring-gold-500 disabled:opacity-50"
                            >
                                <span className="block font-medium text-gray-800 text-sm">
                                    {item.name}
                                </span>
                                <span className="text-maroon-800 text-sm">
                                    Rs. {Number(item.price).toFixed(0)}
                                </span>
                            </button>
                        ))}
                    </div>
                </section>

                {/* Order panel */}
                <section className="bg-white rounded-xl shadow-sm p-4 flex flex-col h-fit lg:sticky lg:top-4">
                    {stage === "done" ? (
                        <div className="text-center py-6">
                            <p className="text-3xl mb-2">✅</p>
                            <p className="font-semibold text-gray-800">
                                Order paid
                            </p>
                            <p className="text-sm text-gray-500 mt-1">
                                Order #{placedOrder.order_number} · Rs.{" "}
                                {Number(placedOrder.total_amount).toFixed(0)}
                            </p>
                            <button
                                onClick={resetOrder}
                                className="mt-5 w-full bg-maroon-700 hover:bg-maroon-800 text-white font-semibold py-2.5 rounded-lg"
                            >
                                New order
                            </button>
                        </div>
                    ) : (
                        <>
                            {/* Order type toggle */}
                            <div className="flex gap-2 mb-3">
                                {[
                                    { key: "pickup", label: "Pickup" },
                                    { key: "delivery", label: "Delivery" },
                                ].map((t) => (
                                    <button
                                        key={t.key}
                                        disabled={stage !== "building"}
                                        onClick={() => setOrderType(t.key)}
                                        className={`flex-1 py-1.5 rounded-lg text-sm disabled:opacity-60 ${
                                            orderType === t.key
                                                ? "bg-maroon-700 text-white"
                                                : "bg-gray-100 text-gray-700"
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
                                        disabled={stage !== "building"}
                                        onChange={(e) =>
                                            setAddress(e.target.value)
                                        }
                                        placeholder="Delivery address"
                                        className="mb-2 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60"
                                    />
                                    {/* Changes in delivery charges in the code */}
                                    <input
                                        type="number"
                                        min="0"
                                        step="0.1"
                                        value={distance}
                                        disabled={stage !== "building"}
                                        onChange={(e) =>
                                            setDistance(e.target.value)
                                        }
                                        placeholder="Distance (km)"
                                        className="mb-3 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60"
                                    />
                                </>
                            )}

                            {/* Optional customer capture for repeat tracking */}
                            <div className="flex gap-2 mb-3">
                                <input
                                    type="text"
                                    value={custName}
                                    disabled={stage !== "building"}
                                    onChange={(e) => setCustName(e.target.value)}
                                    placeholder="Customer name"
                                    className="flex-1 border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60"
                                />
                                <input
                                    type="tel"
                                    value={custPhone}
                                    disabled={stage !== "building"}
                                    onChange={(e) =>
                                        setCustPhone(e.target.value)
                                    }
                                    placeholder="Phone"
                                    className="w-28 border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60"
                                />
                            </div>

                            {/* Lines */}
                            <div className="flex-1 space-y-2 min-h-24">
                                {lines.length === 0 && (
                                    <p className="text-gray-400 text-sm text-center py-6">
                                        Tap menu items to add them.
                                    </p>
                                )}
                                {lines.map((l) => (
                                    <div
                                        key={l.id}
                                        className="flex items-center gap-2 text-sm"
                                    >
                                        <span className="flex-1 text-gray-800">
                                            {l.name}
                                        </span>
                                        {stage === "building" && (
                                            <>
                                                <button
                                                    onClick={() =>
                                                        changeQty(l.id, -1)
                                                    }
                                                    className="w-6 h-6 rounded bg-gray-100 font-bold"
                                                >
                                                    −
                                                </button>
                                                <span className="w-5 text-center">
                                                    {l.quantity}
                                                </span>
                                                <button
                                                    onClick={() =>
                                                        changeQty(l.id, 1)
                                                    }
                                                    className="w-6 h-6 rounded bg-gray-100 font-bold"
                                                >
                                                    +
                                                </button>
                                            </>
                                        )}
                                        {stage !== "building" && (
                                            <span className="w-8 text-center">
                                                ×{l.quantity}
                                            </span>
                                        )}
                                        <span className="w-16 text-right text-gray-600">
                                            Rs.{" "}
                                            {(l.price * l.quantity).toFixed(0)}
                                        </span>
                                    </div>
                                ))}
                            </div>

                            {deliveryFee > 0 && (
                                <div className="flex justify-between text-sm text-gray-500 mt-3">
                                    <span>Delivery</span>
                                    <span>Rs. {deliveryFee}</span>
                                </div>
                            )}

                            <div className="border-t mt-2 pt-3 flex justify-between font-bold text-gray-800">
                                <span>Total</span>
                                <span>Rs. {total.toFixed(0)}</span>
                            </div>

                            {error && (
                                <p className="text-red-600 text-sm mt-2">
                                    {error}
                                </p>
                            )}

                            {stage === "building" && (
                                <button
                                    onClick={placeOrder}
                                    disabled={busy}
                                    className="mt-3 w-full bg-maroon-700 hover:bg-maroon-800 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg"
                                >
                                    {busy ? "Placing…" : "Place Order"}
                                </button>
                            )}

                            {stage === "payment" && (
                                <div className="mt-3">
                                    {placedOrder.advance_required && (
                                        <p className="text-xs font-medium text-maroon-900 bg-gold-100 rounded-lg px-3 py-2 mb-2">
                                            Advance required for this order.
                                        </p>
                                    )}
                                    <label className="flex items-center gap-2 text-sm text-gray-700 mb-2">
                                        <input
                                            type="checkbox"
                                            checked={advance}
                                            onChange={(e) =>
                                                setAdvance(e.target.checked)
                                            }
                                        />
                                        Take advance only (Rs. {advanceAmount})
                                    </label>
                                    <input
                                        type="text"
                                        value={reference}
                                        onChange={(e) =>
                                            setReference(e.target.value)
                                        }
                                        placeholder="Transaction ref (optional)"
                                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm mb-2"
                                    />
                                    <p className="text-sm text-gray-600 mb-2">
                                        Take payment:
                                    </p>
                                    <div className="grid grid-cols-3 gap-2">
                                        {PAYMENT_METHODS.map((m) => (
                                            <button
                                                key={m.key}
                                                onClick={() =>
                                                    takePayment(m.key)
                                                }
                                                disabled={busy}
                                                className="bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white text-sm font-medium py-2 rounded-lg"
                                            >
                                                {m.label}
                                            </button>
                                        ))}
                                    </div>
                                </div>
                            )}
                        </>
                    )}
                </section>
            </main>
        </div>
    );
}
