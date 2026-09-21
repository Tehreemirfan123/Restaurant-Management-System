import { useEffect, useState } from "react";

import { createWaste, getInventory, getWaste } from "../services/api";

export default function AdminWaste() {
    const [inventory, setInventory] = useState([]);
    const [logs, setLogs] = useState([]);
    const [form, setForm] = useState({
        inventory_item_id: "",
        quantity: "",
        description: "",
    });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    function load() {
        Promise.all([getInventory(), getWaste()])
            .then(([inv, w]) => {
                setInventory(inv || []);
                setLogs(w || []);
            })
            .catch((err) => setError(err.message || "Failed to load"))
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        if (!Number(form.quantity)) {
            setError("Enter a quantity");
            return;
        }

        try {
            await createWaste({
                inventory_item_id: form.inventory_item_id || null,
                quantity: Number(form.quantity),
                description: form.description || null,
            });
            setForm({ inventory_item_id: "", quantity: "", description: "" });
            load();
        } catch (err) {
            setError(err.message || "Could not log waste");
        }
    }

    const totalValue = logs.reduce((sum, l) => sum + Number(l.cost || 0), 0);

    function fmtDate(iso) {
        return new Date(iso).toLocaleDateString();
    }

    return (

            <main className="max-w-4xl mx-auto p-6 grid gap-6 md:grid-cols-3">
                <form
                    onSubmit={handleSubmit}
                    className="bg-white rounded-xl shadow-sm p-5 space-y-3 h-fit"
                >
                    <h2 className="font-semibold text-gray-800">Log waste</h2>

                    <select
                        value={form.inventory_item_id}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                inventory_item_id: e.target.value,
                            })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    >
                        <option value="">Ingredient (optional)…</option>
                        {inventory.map((i) => (
                            <option key={i.id} value={i.id}>
                                {i.name} ({i.unit})
                            </option>
                        ))}
                    </select>
                    <input
                        type="number"
                        step="0.001"
                        min="0"
                        placeholder="Quantity wasted"
                        value={form.quantity}
                        onChange={(e) =>
                            setForm({ ...form, quantity: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <input
                        type="text"
                        placeholder="Reason / note"
                        value={form.description}
                        onChange={(e) =>
                            setForm({ ...form, description: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />

                    {error && <p className="text-red-600 text-sm">{error}</p>}

                    <button
                        type="submit"
                        className="w-full bg-maroon-700 hover:bg-maroon-800 text-white text-sm font-medium py-2 rounded-lg"
                    >
                        Log
                    </button>
                </form>

                <div className="md:col-span-2">
                    <div className="bg-white rounded-xl shadow-sm p-4 mb-3 flex justify-between">
                        <span className="text-gray-600 text-sm">
                            Total waste value
                        </span>
                        <span className="font-bold text-gray-800">
                            Rs. {totalValue.toFixed(0)}
                        </span>
                    </div>

                    <div className="space-y-2">
                        {loading && <p className="text-gray-500">Loading...</p>}
                        {!loading && logs.length === 0 && (
                            <p className="text-gray-500">
                                No waste logged yet.
                            </p>
                        )}
                        {logs.map((log) => (
                            <div
                                key={log.id}
                                className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between"
                            >
                                <div>
                                    <p className="font-medium text-gray-800">
                                        {log.item_name || "General waste"}
                                    </p>
                                    <p className="text-sm text-gray-500">
                                        {Number(log.quantity)}{" "}
                                        {log.description
                                            ? `· ${log.description}`
                                            : ""}
                                    </p>
                                </div>
                                <div className="text-right text-sm">
                                    <p className="text-gray-800">
                                        Rs. {Number(log.cost).toFixed(0)}
                                    </p>
                                    <p className="text-gray-400">
                                        {fmtDate(log.created_at)}
                                    </p>
                                </div>
                            </div>
                        ))}
                    </div>
                </div>
            </main>
    );
}
