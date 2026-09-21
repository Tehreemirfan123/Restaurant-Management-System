import { useEffect, useState } from "react";

import { getCustomers, updateCustomer } from "../services/api";

const SEGMENTS = ["office", "student", "hostel", "household", "other"];

export default function AdminCustomers() {
    const [customers, setCustomers] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");

    function load() {
        getCustomers()
            .then((data) => setCustomers(data || []))
            .catch((err) =>
                setError(err.message || "Failed to load customers")
            )
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    async function changeSegment(customer, segment) {
        try {
            await updateCustomer(customer.id, { segment: segment || null });
            setCustomers((current) =>
                current.map((c) =>
                    c.id === customer.id ? { ...c, segment } : c
                )
            );
        } catch (err) {
            setError(err.message || "Could not update segment");
        }
    }

    function fmtDate(iso) {
        if (!iso) return "—";
        return new Date(iso).toLocaleDateString();
    }

    return (

            <main className="max-w-4xl mx-auto p-6">
                {loading && <p className="text-gray-500">Loading...</p>}
                {error && <p className="text-red-600 mb-4">{error}</p>}

                {!loading && customers.length === 0 && (
                    <p className="text-gray-500">No customers yet.</p>
                )}

                <div className="space-y-2">
                    {customers.map((c) => (
                        <div
                            key={c.id}
                            className="bg-white rounded-xl shadow-sm p-4 flex flex-wrap items-center gap-3 justify-between"
                        >
                            <div className="min-w-0">
                                <p className="font-medium text-gray-800">
                                    {c.name}
                                </p>
                                <p className="text-sm text-gray-500">
                                    {c.phone || "no phone"}
                                    {c.address ? ` · ${c.address}` : ""}
                                </p>
                            </div>

                            <div className="flex items-center gap-4 text-sm">
                                <span className="text-gray-600">
                                    {c.order_count} order
                                    {c.order_count === 1 ? "" : "s"}
                                    {c.order_count >= 2 && (
                                        <span className="ml-1 text-green-600 font-medium">
                                            repeat
                                        </span>
                                    )}
                                </span>
                                <span className="text-gray-400">
                                    last: {fmtDate(c.last_order_at)}
                                </span>
                                <select
                                    value={c.segment || ""}
                                    onChange={(e) =>
                                        changeSegment(c, e.target.value)
                                    }
                                    className="border border-gray-300 rounded-lg px-2 py-1 text-sm capitalize"
                                >
                                    <option value="">segment…</option>
                                    {SEGMENTS.map((s) => (
                                        <option key={s} value={s}>
                                            {s}
                                        </option>
                                    ))}
                                </select>
                            </div>
                        </div>
                    ))}
                </div>
            </main>
    );
}
