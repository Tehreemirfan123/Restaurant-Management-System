import { useEffect, useMemo, useState } from "react";

import {
    createRecipe,
    deleteRecipe,
    getInventory,
    getMenu,
    getRecipes,
    updateRecipe,
} from "../services/api";

export default function AdminRecipes() {
    const [menu, setMenu] = useState([]);
    const [inventory, setInventory] = useState([]);
    const [recipes, setRecipes] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    const [menuItemId, setMenuItemId] = useState("");
    const [rows, setRows] = useState([{ inventory_item_id: "", quantity: "" }]);
    const [editingId, setEditingId] = useState(null);

    function load() {
        Promise.all([getMenu(), getInventory(), getRecipes()])
            .then(([m, inv, r]) => {
                setMenu(m || []);
                setInventory(inv || []);
                setRecipes(r || []);
            })
            .catch((err) => setError(err.message || "Failed to load"))
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    const menuById = useMemo(() => {
        const map = {};
        menu.forEach((m) => (map[m.id] = m));
        return map;
    }, [menu]);

    const invById = useMemo(() => {
        const map = {};
        inventory.forEach((i) => (map[i.id] = i));
        return map;
    }, [inventory]);

    const dishesWithRecipe = useMemo(
        () => new Set(recipes.map((r) => r.menu_item_id)),
        [recipes]
    );

    function resetForm() {
        setEditingId(null);
        setMenuItemId("");
        setRows([{ inventory_item_id: "", quantity: "" }]);
        setError("");
    }

    function startEdit(recipe) {
        setEditingId(recipe.id);
        setMenuItemId(recipe.menu_item_id);
        setRows(
            recipe.ingredients.length
                ? recipe.ingredients.map((i) => ({
                      inventory_item_id: i.inventory_item_id,
                      quantity: String(i.quantity),
                  }))
                : [{ inventory_item_id: "", quantity: "" }]
        );
        setError("");
    }

    function updateRow(idx, field, value) {
        setRows((cur) =>
            cur.map((r, i) => (i === idx ? { ...r, [field]: value } : r))
        );
    }

    function addRow() {
        setRows((cur) => [...cur, { inventory_item_id: "", quantity: "" }]);
    }

    function removeRow(idx) {
        setRows((cur) => cur.filter((_, i) => i !== idx));
    }

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        if (!menuItemId) {
            setError("Pick a dish");
            return;
        }

        const ingredients = rows
            .filter((r) => r.inventory_item_id && Number(r.quantity) > 0)
            .map((r) => ({
                inventory_item_id: r.inventory_item_id,
                quantity: Number(r.quantity),
            }));

        try {
            if (editingId) {
                await updateRecipe(editingId, { ingredients });
            } else {
                await createRecipe({ menu_item_id: menuItemId, ingredients });
            }
            resetForm();
            load();
        } catch (err) {
            setError(err.message || "Could not save recipe");
        }
    }

    async function handleDelete(id) {
        if (!window.confirm("Delete this recipe?")) return;
        try {
            await deleteRecipe(id);
            if (editingId === id) resetForm();
            load();
        } catch (err) {
            setError(err.message || "Could not delete recipe");
        }
    }

    return (

            <main className="max-w-4xl mx-auto p-6 grid gap-6 md:grid-cols-2">
                {/* Form */}
                <form
                    onSubmit={handleSubmit}
                    className="bg-white rounded-xl shadow-sm p-5 space-y-3 h-fit"
                >
                    <h2 className="font-semibold text-gray-800">
                        {editingId ? "Edit recipe" : "New recipe"}
                    </h2>

                    <select
                        value={menuItemId}
                        disabled={Boolean(editingId)}
                        onChange={(e) => setMenuItemId(e.target.value)}
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm disabled:bg-gray-100"
                    >
                        <option value="">Select dish…</option>
                        {menu
                            .filter(
                                (m) =>
                                    editingId ||
                                    !dishesWithRecipe.has(m.id)
                            )
                            .map((m) => (
                                <option key={m.id} value={m.id}>
                                    {m.name}
                                </option>
                            ))}
                    </select>

                    <p className="text-sm font-medium text-gray-600">
                        Ingredients (per portion)
                    </p>

                    {rows.map((row, idx) => (
                        <div key={idx} className="flex gap-2">
                            <select
                                value={row.inventory_item_id}
                                onChange={(e) =>
                                    updateRow(
                                        idx,
                                        "inventory_item_id",
                                        e.target.value
                                    )
                                }
                                className="flex-1 border border-gray-300 rounded-lg px-2 py-2 text-sm"
                            >
                                <option value="">Ingredient…</option>
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
                                placeholder="Qty"
                                value={row.quantity}
                                onChange={(e) =>
                                    updateRow(idx, "quantity", e.target.value)
                                }
                                className="w-20 border border-gray-300 rounded-lg px-2 py-2 text-sm"
                            />
                            <button
                                type="button"
                                onClick={() => removeRow(idx)}
                                className="text-red-500 text-sm px-1"
                            >
                                ✕
                            </button>
                        </div>
                    ))}

                    <button
                        type="button"
                        onClick={addRow}
                        className="text-sm text-maroon-800 hover:underline"
                    >
                        + Add ingredient
                    </button>

                    {error && <p className="text-red-600 text-sm">{error}</p>}

                    <div className="flex gap-2 pt-1">
                        <button
                            type="submit"
                            className="flex-1 bg-maroon-700 hover:bg-maroon-800 text-white text-sm font-medium py-2 rounded-lg"
                        >
                            {editingId ? "Save" : "Create"}
                        </button>
                        {editingId && (
                            <button
                                type="button"
                                onClick={resetForm}
                                className="px-3 py-2 text-sm text-gray-600 border rounded-lg"
                            >
                                Cancel
                            </button>
                        )}
                    </div>
                </form>

                {/* List */}
                <div className="space-y-2">
                    {loading && <p className="text-gray-500">Loading...</p>}
                    {!loading && recipes.length === 0 && (
                        <p className="text-gray-500">
                            No recipes yet. Add one so dish costs can be
                            calculated.
                        </p>
                    )}
                    {recipes.map((r) => (
                        <div
                            key={r.id}
                            className="bg-white rounded-xl shadow-sm p-4"
                        >
                            <div className="flex items-center justify-between">
                                <p className="font-medium text-gray-800">
                                    {menuById[r.menu_item_id]?.name || "Dish"}
                                </p>
                                <div className="flex gap-2 text-sm">
                                    <button
                                        onClick={() => startEdit(r)}
                                        className="text-maroon-800 hover:underline"
                                    >
                                        Edit
                                    </button>
                                    <button
                                        onClick={() => handleDelete(r.id)}
                                        className="text-red-600 hover:underline"
                                    >
                                        Delete
                                    </button>
                                </div>
                            </div>
                            <ul className="text-sm text-gray-500 mt-1">
                                {r.ingredients.length === 0 && (
                                    <li>No ingredients</li>
                                )}
                                {r.ingredients.map((ing) => (
                                    <li key={ing.id}>
                                        {Number(ing.quantity)}{" "}
                                        {invById[ing.inventory_item_id]?.unit ||
                                            ""}{" "}
                                        {invById[ing.inventory_item_id]?.name ||
                                            "ingredient"}
                                    </li>
                                ))}
                            </ul>
                        </div>
                    ))}
                </div>
            </main>
    );
}
