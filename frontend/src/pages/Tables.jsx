import { useEffect, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import { getTables, updateTable } from "../services/api";

const STATUS_STYLES = {
    available: "bg-green-100 border-green-300 text-green-800",
    occupied: "bg-red-100 border-red-300 text-red-800",
    reserved: "bg-yellow-100 border-yellow-300 text-yellow-800",
};

const STATUSES = ["available", "occupied", "reserved"];

export default function Tables() {
    const [tables, setTables] = useState([]);
    const [loading, setLoading] = useState(true);
    const [error, setError] = useState("");
    const [savingId, setSavingId] = useState(null);

    function load() {
        getTables()
            .then((data) => setTables(data || []))
            .catch((err) => setError(err.message || "Failed to load tables"))
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    async function changeStatus(table, status) {
        if (table.status === status) return;

        setSavingId(table.id);
        try {
            const updated = await updateTable(table.id, { status });
            setTables((current) =>
                current.map((t) => (t.id === updated.id ? updated : t))
            );
        } catch (err) {
            setError(err.message || "Could not update table");
        } finally {
            setSavingId(null);
        }
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Tables" />

            <main className="max-w-4xl mx-auto p-6">
                {loading && <p className="text-gray-500">Loading tables...</p>}
                {error && <p className="text-red-600 mb-4">{error}</p>}

                <div className="grid gap-4 grid-cols-2 sm:grid-cols-3 md:grid-cols-4">
                    {tables.map((table) => (
                        <div
                            key={table.id}
                            className={`rounded-xl border p-4 ${
                                STATUS_STYLES[table.status]
                            }`}
                        >
                            <div className="flex items-baseline justify-between">
                                <span className="text-lg font-bold">
                                    Table {table.number}
                                </span>
                                <span className="text-xs">
                                    {table.capacity} seats
                                </span>
                            </div>
                            <p className="text-sm capitalize mt-1 mb-3">
                                {table.status}
                            </p>

                            <div className="flex flex-wrap gap-1">
                                {STATUSES.map((s) => (
                                    <button
                                        key={s}
                                        disabled={savingId === table.id}
                                        onClick={() => changeStatus(table, s)}
                                        className={`text-xs px-2 py-1 rounded border capitalize disabled:opacity-50 ${
                                            table.status === s
                                                ? "bg-white/70 font-semibold"
                                                : "bg-white/30 hover:bg-white/50"
                                        }`}
                                    >
                                        {s}
                                    </button>
                                ))}
                            </div>
                        </div>
                    ))}
                </div>

                {!loading && tables.length === 0 && (
                    <p className="text-gray-500">
                        No tables yet. An admin can add them.
                    </p>
                )}
            </main>
        </div>
    );
}
