import { useEffect, useState } from "react";

import { getSettings, updateSettings } from "../services/api";

const EMPTY = {
    restaurant_name: "",
    contact_phone: "",
    address: "",
    opening_hours: "",
    delivery_fee: "",
    delivery_radius_km: "",
    accepting_orders: true,
    daily_order_cap: "",
};

export default function AdminSettings() {
    const [form, setForm] = useState(EMPTY);
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        getSettings()
            .then((s) =>
                setForm({
                    restaurant_name: s.restaurant_name || "",
                    contact_phone: s.contact_phone || "",
                    address: s.address || "",
                    opening_hours: s.opening_hours || "",
                    delivery_fee: String(s.delivery_fee ?? ""),
                    delivery_radius_km: String(s.delivery_radius_km ?? ""),
                    accepting_orders: s.accepting_orders,
                    daily_order_cap: s.daily_order_cap ?? "",
                })
            )
            .catch((err) => setError(err.message || "Failed to load settings"))
            .finally(() => setLoading(false));
    }, []);

    function set(field, value) {
        setForm((f) => ({ ...f, [field]: value }));
        setSaved(false);
    }

    async function handleSave() {
        setError("");
        setSaved(false);
        setSaving(true);
        try {
            await updateSettings({
                restaurant_name: form.restaurant_name,
                contact_phone: form.contact_phone || null,
                address: form.address || null,
                opening_hours: form.opening_hours || null,
                delivery_fee: Number(form.delivery_fee || 0),
                delivery_radius_km: Number(form.delivery_radius_km || 0),
                accepting_orders: form.accepting_orders,
                daily_order_cap:
                    form.daily_order_cap === ""
                        ? null
                        : Number(form.daily_order_cap),
            });
            setSaved(true);
        } catch (err) {
            setError(err.message || "Could not save");
        } finally {
            setSaving(false);
        }
    }

    const input =
        "w-full border border-gray-300 rounded-lg px-3 py-2 text-sm";
    const labelCls = "block text-sm font-medium text-gray-700 mb-1";

    return (
        <main className="max-w-2xl mx-auto p-6 space-y-5">
            {loading && <p className="text-gray-500">Loading...</p>}

            {!loading && (
                <>
                    {/* Business info */}
                    <section className="bg-white rounded-xl shadow-sm p-6 space-y-4">
                        <h2 className="font-semibold text-gray-800">
                            Business info
                        </h2>
                        <div>
                            <label className={labelCls}>Restaurant name</label>
                            <input
                                className={input}
                                value={form.restaurant_name}
                                onChange={(e) =>
                                    set("restaurant_name", e.target.value)
                                }
                            />
                        </div>
                        <div>
                            <label className={labelCls}>Contact phone</label>
                            <input
                                className={input}
                                value={form.contact_phone}
                                onChange={(e) =>
                                    set("contact_phone", e.target.value)
                                }
                            />
                        </div>
                        <div>
                            <label className={labelCls}>Address</label>
                            <textarea
                                className={input}
                                value={form.address}
                                onChange={(e) =>
                                    set("address", e.target.value)
                                }
                            />
                        </div>
                        <div>
                            <label className={labelCls}>Opening hours</label>
                            <input
                                className={input}
                                placeholder="e.g. 11:00 AM – 11:00 PM"
                                value={form.opening_hours}
                                onChange={(e) =>
                                    set("opening_hours", e.target.value)
                                }
                            />
                        </div>
                    </section>

                    {/* Delivery */}
                    <section className="bg-white rounded-xl shadow-sm p-6 space-y-4">
                        <h2 className="font-semibold text-gray-800">Delivery</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelCls}>
                                    Delivery fee (Rs.)
                                </label>
                                <input
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    className={input}
                                    value={form.delivery_fee}
                                    onChange={(e) =>
                                        set("delivery_fee", e.target.value)
                                    }
                                />
                            </div>
                            <div>
                                <label className={labelCls}>
                                    Delivery radius (km)
                                </label>
                                <input
                                    type="number"
                                    min="0"
                                    step="0.1"
                                    className={input}
                                    value={form.delivery_radius_km}
                                    onChange={(e) =>
                                        set(
                                            "delivery_radius_km",
                                            e.target.value
                                        )
                                    }
                                />
                            </div>
                        </div>
                    </section>

                    {/* Ordering */}
                    <section className="bg-white rounded-xl shadow-sm p-6 space-y-4">
                        <h2 className="font-semibold text-gray-800">Ordering</h2>
                        <label className="flex items-center justify-between">
                            <span className="text-gray-800">
                                Accepting orders
                            </span>
                            <input
                                type="checkbox"
                                checked={form.accepting_orders}
                                onChange={(e) =>
                                    set("accepting_orders", e.target.checked)
                                }
                                className="h-5 w-5"
                            />
                        </label>
                        <div>
                            <label className={labelCls}>Daily order limit</label>
                            <input
                                type="number"
                                min="0"
                                placeholder="No limit"
                                className={input}
                                value={form.daily_order_cap}
                                onChange={(e) =>
                                    set("daily_order_cap", e.target.value)
                                }
                            />
                            <p className="text-xs text-gray-400 mt-1">
                                Blocks new orders once this many are placed
                                today. Leave blank for no limit.
                            </p>
                        </div>
                    </section>

                    {error && <p className="text-red-600 text-sm">{error}</p>}
                    {saved && <p className="text-green-600 text-sm">Saved.</p>}

                    <button
                        onClick={handleSave}
                        disabled={saving}
                        className="w-full bg-maroon-700 hover:bg-maroon-800 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg"
                    >
                        {saving ? "Saving..." : "Save settings"}
                    </button>
                </>
            )}
        </main>
    );
}
