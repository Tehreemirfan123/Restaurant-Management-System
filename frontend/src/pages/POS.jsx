import { useEffect, useMemo, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import {
    createOrder,
    createPayment,
    getMenu,
    getTables,
    updateTable,
} from "../services/api";

const PAYMENT_METHODS = [
    { key: "cash", label: "Cash" },
    { key: "card", label: "Card" },
    { key: "online", label: "Online" },
];

export default function POS() {
    const [menu, setMenu] = useState([]);
    const [tables, setTables] = useState([]);
    const [lines, setLines] = useState([]);
    const [orderType, setOrderType] = useState("dine_in");
    const [tableId, setTableId] = useState("");
    const [error, setError] = useState("");

    // Workflow: "building" -> place order -> "payment" -> "done"
    const [stage, setStage] = useState("building");
    const [placedOrder, setPlacedOrder] = useState(null);
    const [busy, setBusy] = useState(false);

    useEffect(() => {
        getMenu()
            .then((data) => setMenu((data || []).filter((m) => m.available)))
            .catch((err) => setError(err.message || "Failed to load menu"));
        getTables()
            .then((data) => setTables(data || []))
            .catch(() => {});
    }, []);

    const total = useMemo(
        () => lines.reduce((sum, l) => sum + l.price * l.quantity, 0),
        [lines]
    );

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
        setTableId("");
        setOrderType("dine_in");
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
        if (orderType === "dine_in" && !tableId) {
            setError("Pick a table for a dine-in order");
            return;
        }

        setBusy(true);
        try {
            const order = await createOrder({
                order_type: orderType,
                table_id: orderType === "dine_in" ? tableId : null,
                items: lines.map((l) => ({
                    menu_item_id: l.id,
                    quantity: l.quantity,
                })),
            });

            // Keep the floor view in sync for dine-in orders.
            if (orderType === "dine_in" && tableId) {
                try {
                    await updateTable(tableId, { status: "occupied" });
                } catch {
                    // Non-fatal; the order itself succeeded.
                }
            }

            setPlacedOrder(order);
            setStage("payment");
        } catch (err) {
            setError(err.message || "Could not place order");
        } finally {
            setBusy(false);
        }
    }

    async function takePayment(method) {
        setError("");
        setBusy(true);
        try {
            await createPayment({ order_id: placedOrder.id, method });
            setStage("done");
        } catch (err) {
            setError(err.message || "Payment failed");
        } finally {
            setBusy(false);
        }
    }

    const availableTables = tables.filter(
        (t) => t.status !== "occupied" || t.id === tableId
    );

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
                                className="bg-white rounded-xl shadow-sm p-3 text-left hover:ring-2 hover:ring-amber-400 disabled:opacity-50"
                            >
                                <span className="block font-medium text-gray-800 text-sm">
                                    {item.name}
                                </span>
                                <span className="text-amber-700 text-sm">
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
                                #{placedOrder.id.slice(0, 8)} · Rs.{" "}
                                {Number(placedOrder.total_amount).toFixed(0)}
                            </p>
                            <button
                                onClick={resetOrder}
                                className="mt-5 w-full bg-amber-600 hover:bg-amber-700 text-white font-semibold py-2.5 rounded-lg"
                            >
                                New order
                            </button>
                        </div>
                    ) : (
                        <>
                            {/* Order type toggle */}
                            <div className="flex gap-2 mb-3">
                                {["dine_in", "takeaway"].map((t) => (
                                    <button
                                        key={t}
                                        disabled={stage !== "building"}
                                        onClick={() => setOrderType(t)}
                                        className={`flex-1 py-1.5 rounded-lg text-sm capitalize disabled:opacity-60 ${
                                            orderType === t
                                                ? "bg-amber-600 text-white"
                                                : "bg-gray-100 text-gray-700"
                                        }`}
                                    >
                                        {t.replace("_", "-")}
                                    </button>
                                ))}
                            </div>

                            {orderType === "dine_in" && (
                                <select
                                    value={tableId}
                                    disabled={stage !== "building"}
                                    onChange={(e) => setTableId(e.target.value)}
                                    className="mb-3 w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:opacity-60"
                                >
                                    <option value="">Select table…</option>
                                    {availableTables.map((t) => (
                                        <option key={t.id} value={t.id}>
                                            Table {t.number} ({t.capacity} seats)
                                        </option>
                                    ))}
                                </select>
                            )}

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

                            <div className="border-t mt-3 pt-3 flex justify-between font-bold text-gray-800">
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
                                    className="mt-3 w-full bg-amber-600 hover:bg-amber-700 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg"
                                >
                                    {busy ? "Placing…" : "Place Order"}
                                </button>
                            )}

                            {stage === "payment" && (
                                <div className="mt-3">
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
