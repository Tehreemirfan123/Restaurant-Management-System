import { useCallback, useEffect, useState } from "react";

import { PAYMENT_METHODS } from "../config";
import {
    createPayment,
    getPayments,
    getReconciliation,
    updatePayment,
} from "../services/api";

// Staff-facing labels for every method the backend may return.
const METHOD_LABEL = {
    cash: "Cash",
    bank_transfer: "Bank Transfer",
    jazzcash: "JazzCash",
    easypaisa: "Easypaisa",
    card: "Card",
    online: "Online",
};

function todayISO() {
    // Local (business) date in YYYY-MM-DD.
    const d = new Date();
    const off = d.getTimezoneOffset();
    return new Date(d.getTime() - off * 60000).toISOString().slice(0, 10);
}

const rs = (n) => `Rs. ${Number(n || 0).toFixed(0)}`;

export default function AdminPayments() {
    const [date, setDate] = useState(todayISO());
    const [recon, setRecon] = useState(null);
    const [pending, setPending] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [busy, setBusy] = useState(false);

    // Inline "record payment" form keyed by order id.
    const [recordFor, setRecordFor] = useState(null);
    const [form, setForm] = useState({ amount: "", method: "cash", reference: "" });

    const load = useCallback(async () => {
        setLoading(true);
        setError("");
        try {
            const [r, all] = await Promise.all([
                getReconciliation(date),
                getPayments({ date }),
            ]);
            setRecon(r);
            setPending(all.filter((p) => p.status === "pending"));
        } catch (err) {
            setError(err.message || "Could not load payments");
        } finally {
            setLoading(false);
        }
    }, [date]);

    useEffect(() => {
        load();
    }, [load]);

    function openRecord(order) {
        setRecordFor(order.order_id);
        setForm({
            amount: String(Math.round(Number(order.balance_due))),
            method: "cash",
            reference: "",
        });
    }

    async function submitRecord(order) {
        setBusy(true);
        setError("");
        try {
            await createPayment({
                order_id: order.order_id,
                method: form.method,
                amount: Number(form.amount),
                reference: form.reference.trim() || null,
            });
            setRecordFor(null);
            await load();
        } catch (err) {
            setError(err.message || "Could not record payment");
        } finally {
            setBusy(false);
        }
    }

    async function confirmPending(payment) {
        setBusy(true);
        setError("");
        try {
            await updatePayment(payment.id, { status: "paid" });
            await load();
        } catch (err) {
            setError(err.message || "Could not confirm payment");
        } finally {
            setBusy(false);
        }
    }

    return (
        <main className="max-w-5xl mx-auto p-6 space-y-5">
            {/* Date + summary */}
            <section className="bg-white rounded-xl shadow-sm p-6">
                <div className="flex flex-wrap items-center justify-between gap-3">
                    <div>
                        <h2 className="font-semibold text-gray-800">
                            Daily reconciliation
                        </h2>
                        <p className="text-sm text-gray-500">
                            Record and reconcile payments against order numbers.
                        </p>
                    </div>
                    <input
                        type="date"
                        value={date}
                        onChange={(e) => setDate(e.target.value)}
                        className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                </div>

                {recon && (
                    <div className="mt-4 grid gap-3 sm:grid-cols-3">
                        <div className="rounded-lg bg-cream-100 p-4">
                            <p className="text-xs text-gray-500">
                                Collected today
                            </p>
                            <p className="text-xl font-bold text-maroon-800">
                                {rs(recon.total_collected)}
                            </p>
                        </div>
                        <div className="rounded-lg bg-cream-100 p-4">
                            <p className="text-xs text-gray-500">Payments</p>
                            <p className="text-xl font-bold text-maroon-800">
                                {recon.payment_count}
                            </p>
                        </div>
                        <div className="rounded-lg bg-cream-100 p-4">
                            <p className="text-xs text-gray-500">
                                Outstanding orders
                            </p>
                            <p className="text-xl font-bold text-maroon-800">
                                {recon.outstanding.length}
                            </p>
                        </div>
                    </div>
                )}

                {recon && recon.by_method.length > 0 && (
                    <div className="mt-3 flex flex-wrap gap-2 text-sm">
                        {recon.by_method.map((m) => (
                            <span
                                key={m.method}
                                className="rounded-full bg-gold-100 text-maroon-900 px-3 py-1"
                            >
                                {METHOD_LABEL[m.method] || m.method}: {rs(m.amount)}{" "}
                                ({m.count})
                            </span>
                        ))}
                    </div>
                )}
            </section>

            {error && <p className="text-red-600 text-sm">{error}</p>}
            {loading && <p className="text-gray-500">Loading…</p>}

            {/* Pending (customer-intended) payments to confirm */}
            {pending.length > 0 && (
                <section className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="font-semibold text-gray-800 mb-3">
                        Pending confirmations
                    </h2>
                    <div className="space-y-2">
                        {pending.map((p) => (
                            <div
                                key={p.id}
                                className="flex flex-wrap items-center justify-between gap-2 border-b border-gray-100 pb-2 text-sm"
                            >
                                <span className="text-gray-800">
                                    Order #{p.order_number} ·{" "}
                                    {p.customer_name || "Walk-in"} ·{" "}
                                    {METHOD_LABEL[p.method] || p.method} ·{" "}
                                    {rs(p.amount)}
                                    {p.reference ? ` · ${p.reference}` : ""}
                                </span>
                                <button
                                    onClick={() => confirmPending(p)}
                                    disabled={busy}
                                    className="bg-green-600 hover:bg-green-700 disabled:opacity-60 text-white text-xs font-medium px-3 py-1.5 rounded-lg"
                                >
                                    Mark received
                                </button>
                            </div>
                        ))}
                    </div>
                </section>
            )}

            {/* Outstanding orders */}
            {recon && (
                <section className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="font-semibold text-gray-800 mb-3">
                        Orders with a balance
                    </h2>
                    {recon.outstanding.length === 0 ? (
                        <p className="text-sm text-gray-500">
                            Every active order is fully paid.
                        </p>
                    ) : (
                        <div className="space-y-3">
                            {recon.outstanding.map((o) => (
                                <div
                                    key={o.order_id}
                                    className="border border-gray-100 rounded-lg p-3"
                                >
                                    <div className="flex flex-wrap items-center justify-between gap-2 text-sm">
                                        <span className="font-medium text-gray-800">
                                            Order #{o.order_number} ·{" "}
                                            {o.customer_name || "Walk-in"}
                                            {o.advance_required && (
                                                <span className="ml-2 text-xs bg-gold-100 text-maroon-900 rounded-full px-2 py-0.5">
                                                    advance {rs(o.advance_amount)}
                                                </span>
                                            )}
                                        </span>
                                        <span className="text-gray-600">
                                            Paid {rs(o.amount_paid)} /{" "}
                                            {rs(o.total_amount)} ·{" "}
                                            <span className="text-red-600 font-medium">
                                                balance {rs(o.balance_due)}
                                            </span>
                                        </span>
                                    </div>

                                    {recordFor === o.order_id ? (
                                        <div className="mt-3 flex flex-wrap items-end gap-2">
                                            <label className="text-xs text-gray-500">
                                                Amount
                                                <input
                                                    type="number"
                                                    min="1"
                                                    value={form.amount}
                                                    onChange={(e) =>
                                                        setForm((f) => ({
                                                            ...f,
                                                            amount: e.target.value,
                                                        }))
                                                    }
                                                    className="block w-28 border border-gray-300 rounded-lg px-2 py-1.5 text-sm text-gray-800"
                                                />
                                            </label>
                                            <label className="text-xs text-gray-500">
                                                Method
                                                <select
                                                    value={form.method}
                                                    onChange={(e) =>
                                                        setForm((f) => ({
                                                            ...f,
                                                            method: e.target.value,
                                                        }))
                                                    }
                                                    className="block border border-gray-300 rounded-lg px-2 py-1.5 text-sm text-gray-800"
                                                >
                                                    {PAYMENT_METHODS.map((m) => (
                                                        <option
                                                            key={m.key}
                                                            value={m.key}
                                                        >
                                                            {m.label}
                                                        </option>
                                                    ))}
                                                    <option value="card">
                                                        Card
                                                    </option>
                                                </select>
                                            </label>
                                            <label className="text-xs text-gray-500 flex-1 min-w-32">
                                                Reference
                                                <input
                                                    type="text"
                                                    value={form.reference}
                                                    onChange={(e) =>
                                                        setForm((f) => ({
                                                            ...f,
                                                            reference:
                                                                e.target.value,
                                                        }))
                                                    }
                                                    placeholder="Txn id (optional)"
                                                    className="block w-full border border-gray-300 rounded-lg px-2 py-1.5 text-sm text-gray-800"
                                                />
                                            </label>
                                            <button
                                                onClick={() => submitRecord(o)}
                                                disabled={busy}
                                                className="bg-maroon-700 hover:bg-maroon-800 disabled:opacity-60 text-white text-sm font-medium px-3 py-2 rounded-lg"
                                            >
                                                Save
                                            </button>
                                            <button
                                                onClick={() => setRecordFor(null)}
                                                className="text-sm text-gray-500 px-2 py-2"
                                            >
                                                Cancel
                                            </button>
                                        </div>
                                    ) : (
                                        <button
                                            onClick={() => openRecord(o)}
                                            className="mt-2 text-sm text-maroon-700 font-medium hover:underline"
                                        >
                                            Record payment
                                        </button>
                                    )}
                                </div>
                            ))}
                        </div>
                    )}
                </section>
            )}

            {/* Recorded payments */}
            {recon && (
                <section className="bg-white rounded-xl shadow-sm p-6">
                    <h2 className="font-semibold text-gray-800 mb-3">
                        Payments recorded on {recon.date}
                    </h2>
                    {recon.payments.length === 0 ? (
                        <p className="text-sm text-gray-500">
                            No payments recorded for this day yet.
                        </p>
                    ) : (
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="text-left text-gray-500 border-b border-gray-200">
                                        <th className="py-2 pr-3">Order</th>
                                        <th className="py-2 pr-3">Customer</th>
                                        <th className="py-2 pr-3">Method</th>
                                        <th className="py-2 pr-3">Amount</th>
                                        <th className="py-2 pr-3">Reference</th>
                                        <th className="py-2 pr-3">By</th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {recon.payments.map((p) => (
                                        <tr
                                            key={p.id}
                                            className="border-b border-gray-100 text-gray-800"
                                        >
                                            <td className="py-2 pr-3 font-medium">
                                                #{p.order_number}
                                            </td>
                                            <td className="py-2 pr-3">
                                                {p.customer_name || "Walk-in"}
                                            </td>
                                            <td className="py-2 pr-3">
                                                {METHOD_LABEL[p.method] ||
                                                    p.method}
                                            </td>
                                            <td className="py-2 pr-3">
                                                {rs(p.amount)}
                                            </td>
                                            <td className="py-2 pr-3 text-gray-500">
                                                {p.reference || "—"}
                                            </td>
                                            <td className="py-2 pr-3 text-gray-500">
                                                {p.recorded_by || "—"}
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    )}
                </section>
            )}
        </main>
    );
}
