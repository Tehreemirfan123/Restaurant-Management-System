import { useEffect, useState } from "react";

import {
    createMenuItem,
    deleteMenuItem,
    getMenu,
    updateMenuItem,
} from "../services/api";

const CATEGORIES = ["starters", "mains", "desserts", "drinks"];

const DAYS = [
    "monday",
    "tuesday",
    "wednesday",
    "thursday",
    "friday",
    "saturday",
    "sunday",
];

const EMPTY = {
    name: "",
    description: "",
    price: "",
    category: "mains",
    day_of_week: "",
    packaging_cost: "",
    available: true,
};

export default function AdminMenu() {
    const [items, setItems] = useState([]);
    const [form, setForm] = useState(EMPTY);
    const [editingId, setEditingId] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    function load() {
        getMenu()
            .then((data) => setItems(data || []))
            .catch((err) => setError(err.message || "Failed to load menu"))
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    function startEdit(item) {
        setEditingId(item.id);
        setForm({
            name: item.name,
            description: item.description || "",
            price: String(item.price),
            category: item.category,
            day_of_week: item.day_of_week || "",
            packaging_cost: String(item.packaging_cost ?? ""),
            available: item.available,
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
            description: form.description || null,
            price: Number(form.price),
            category: form.category,
            day_of_week: form.day_of_week || null,
            packaging_cost: Number(form.packaging_cost || 0),
            available: form.available,
        };

        try {
            if (editingId) {
                await updateMenuItem(editingId, payload);
            } else {
                await createMenuItem(payload);
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
            await deleteMenuItem(id);
            load();
        } catch (err) {
            setError(err.message || "Could not delete item");
        }
    }

    return (

            <main className="max-w-4xl mx-auto p-6 grid gap-6 md:grid-cols-3">
                {/* Form */}
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
                    <textarea
                        placeholder="Description"
                        value={form.description}
                        onChange={(e) =>
                            setForm({ ...form, description: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <input
                        type="number"
                        step="0.01"
                        min="0.01"
                        placeholder="Price"
                        required
                        value={form.price}
                        onChange={(e) =>
                            setForm({ ...form, price: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <select
                        value={form.category}
                        onChange={(e) =>
                            setForm({ ...form, category: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm capitalize"
                    >
                        {CATEGORIES.map((c) => (
                            <option key={c} value={c}>
                                {c}
                            </option>
                        ))}
                    </select>
                    <select
                        value={form.day_of_week}
                        onChange={(e) =>
                            setForm({ ...form, day_of_week: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm capitalize"
                    >
                        <option value="">Any day (special)</option>
                        {DAYS.map((d) => (
                            <option key={d} value={d}>
                                {d}
                            </option>
                        ))}
                    </select>
                    <input
                        type="number"
                        step="0.01"
                        min="0"
                        placeholder="Packaging cost (Rs.)"
                        value={form.packaging_cost}
                        onChange={(e) =>
                            setForm({
                                ...form,
                                packaging_cost: e.target.value,
                            })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <label className="flex items-center gap-2 text-sm text-gray-700">
                        <input
                            type="checkbox"
                            checked={form.available}
                            onChange={(e) =>
                                setForm({
                                    ...form,
                                    available: e.target.checked,
                                })
                            }
                        />
                        Available
                    </label>

                    {error && <p className="text-red-600 text-sm">{error}</p>}

                    <div className="flex gap-2">
                        <button
                            type="submit"
                            className="flex-1 bg-maroon-700 hover:bg-maroon-800 text-white text-sm font-medium py-2 rounded-lg"
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

                {/* List */}
                <div className="md:col-span-2 space-y-2">
                    {loading && <p className="text-gray-500">Loading...</p>}
                    {items.map((item) => (
                        <div
                            key={item.id}
                            className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between"
                        >
                            <div className="min-w-0">
                                <p className="font-medium text-gray-800">
                                    {item.name}{" "}
                                    {!item.available && (
                                        <span className="text-xs text-red-500">
                                            (unavailable)
                                        </span>
                                    )}
                                </p>
                                <p className="text-sm text-gray-500 capitalize">
                                    {item.day_of_week || "any day"} · Rs.{" "}
                                    {Number(item.price).toFixed(0)}
                                </p>
                            </div>
                            <div className="flex gap-2 shrink-0">
                                <button
                                    onClick={() => startEdit(item)}
                                    className="text-sm text-maroon-800 hover:underline"
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
    );
}
