import { useEffect, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import {
    createInventoryItem,
    deleteInventoryItem,
    getInventory,
    updateInventoryItem,
} from "../services/api";

const EMPTY = { name: "", unit: "", quantity: "", reorder_level: "" };

export default function AdminInventory() {
    const [items, setItems] = useState([]);
    const [form, setForm] = useState(EMPTY);
    const [editingId, setEditingId] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    function load() {
        getInventory()
            .then((data) => setItems(data || []))
            .catch((err) =>
                setError(err.message || "Failed to load inventory")
            )
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    function startEdit(item) {
        setEditingId(item.id);
        setForm({
            name: item.name,
            unit: item.unit,
            quantity: String(item.quantity),
            reorder_level: String(item.reorder_level),
        });
        setError("");
    }

    function cancelEdit() {
        setEditingId(null);
        setForm(EMPTY);
        setError("");
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        const payload = {
            name: form.name,
            unit: form.unit,
            quantity: Number(form.quantity),
            reorder_level: Number(form.reorder_level || 0),
        };

        try {
            if (editingId) {
                await updateInventoryItem(editingId, payload);
            } else {
                await createInventoryItem(payload);
            }
            cancelEdit();
            load();
        } catch (err) {
            setError(err.message || "Could not save item");
        }
    }

    async function handleDelete(id) {
        if (!window.confirm("Delete this item?")) return;
        try {
            await deleteInventoryItem(id);
            load();
        } catch (err) {
            setError(err.message || "Could not delete item");
        }
    }

    function isLow(item) {
        return Number(item.quantity) <= Number(item.reorder_level);
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Inventory" />

            <main className="max-w-4xl mx-auto p-6 grid gap-6 md:grid-cols-3">
                <form
                    onSubmit={handleSubmit}
                    className="bg-white rounded-xl shadow-sm p-5 space-y-3 h-fit"
                >
                    <h2 className="font-semibold text-gray-800">
                        {editingId ? "Edit item" : "Add item"}
                    </h2>

                    <input
                        type="text"
                        placeholder="Name"
                        required
                        value={form.name}
                        onChange={(e) =>
                            setForm({ ...form, name: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <input
                        type="text"
                        placeholder="Unit (kg, litre, pcs)"
                        required
                        value={form.unit}
                        onChange={(e) =>
                            setForm({ ...form, unit: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <input
                        type="number"
                        step="0.001"
                        min="0"
                        placeholder="Quantity in stock"
                        required
                        value={form.quantity}
                        onChange={(e) =>
                            setForm({ ...form, quantity: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <input
                        type="number"
                        step="0.001"
                        min="0"
                        placeholder="Reorder level"
                        value={form.reorder_level}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                reorder_level: e.target.value,
                            })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />

                    {error && <p className="text-red-600 text-sm">{error}</p>}

                    <div className="flex gap-2">
                        <button
                            type="submit"
                            className="flex-1 bg-amber-600 hover:bg-amber-700 text-white text-sm font-medium py-2 rounded-lg"
                        >
                            {editingId ? "Save" : "Add"}
                        </button>
                        {editingId && (
                            <button
                                type="button"
                                onClick={cancelEdit}
                                className="px-3 py-2 text-sm text-gray-600 border rounded-lg"
                            >
                                Cancel
                            </button>
                        )}
                    </div>
                </form>

                <div className="md:col-span-2 space-y-2">
                    {loading && <p className="text-gray-500">Loading...</p>}
                    {items.map((item) => (
                        <div
                            key={item.id}
                            className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between"
                        >
                            <div>
                                <p className="font-medium text-gray-800">
                                    {item.name}
                                    {isLow(item) && (
                                        <span className="ml-2 text-xs text-red-600">
                                            low stock
                                        </span>
                                    )}
                                </p>
                                <p className="text-sm text-gray-500">
                                    {Number(item.quantity).toFixed(0)}{" "}
                                    {item.unit} · reorder at{" "}
                                    {Number(item.reorder_level).toFixed(0)}
                                </p>
                            </div>
                            <div className="flex gap-2 shrink-0">
                                <button
                                    onClick={() => startEdit(item)}
                                    className="text-sm text-amber-700 hover:underline"
                                >
                                    Edit
                                </button>
                                <button
                                    onClick={() => handleDelete(item.id)}
                                    className="text-sm text-red-600 hover:underline"
                                >
                                    Delete
                                </button>
                            </div>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
