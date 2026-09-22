import { useEffect, useState } from "react";

import { useTheme } from "../context/ThemeContext";
import { getSettings, updateSettings } from "../services/api";

const EMPTY = {
    restaurant_name: "",
    contact_phone: "",
    address: "",
    opening_hours: "",
    delivery_fee: "",
    delivery_radius_km: "",
    delivery_per_km: "",
    advance_payment_percent: "",
    large_order_threshold: "",
    bank_name: "",
    bank_account_name: "",
    bank_account_number: "",
    jazzcash_number: "",
    easypaisa_number: "",
    accepting_orders: true,
    daily_order_cap: "",
};

export default function AdminSettings() {
    const { theme, toggleTheme } = useTheme();
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
                    delivery_per_km: String(s.delivery_per_km ?? ""),
                    advance_payment_percent: String(
                        s.advance_payment_percent ?? ""
                    ),
                    large_order_threshold: String(
                        s.large_order_threshold ?? ""
                    ),
                    bank_name: s.bank_name || "",
                    bank_account_name: s.bank_account_name || "",
                    bank_account_number: s.bank_account_number || "",
                    jazzcash_number: s.jazzcash_number || "",
                    easypaisa_number: s.easypaisa_number || "",
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
                // Changes in delivery charges in the code
                delivery_per_km: Number(form.delivery_per_km || 0),
                advance_payment_percent: Number(
                    form.advance_payment_percent || 0
                ),
                large_order_threshold: Number(
                    form.large_order_threshold || 0
                ),
                bank_name: form.bank_name || null,
                bank_account_name: form.bank_account_name || null,
                bank_account_number: form.bank_account_number || null,
                jazzcash_number: form.jazzcash_number || null,
                easypaisa_number: form.easypaisa_number || null,
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
                    {/* Appearance */}
                    <section className="bg-white rounded-xl shadow-sm p-6">
                        <h2 className="font-semibold text-gray-800 mb-3">
                            Appearance
                        </h2>
                        <label className="flex items-center justify-between">
                            <span className="text-gray-800">Dark mode</span>
                            <button
                                type="button"
                                onClick={toggleTheme}
                                role="switch"
                                aria-checked={theme === "dark"}
                                className={`relative w-12 h-6 rounded-full transition ${
                                    theme === "dark"
                                        ? "bg-maroon-700"
                                        : "bg-gray-300"
                                }`}
                            >
                                <span
                                    className={`absolute top-0.5 left-0.5 h-5 w-5 rounded-full bg-white transition-transform ${
                                        theme === "dark"
                                            ? "translate-x-6"
                                            : ""
                                    }`}
                                />
                            </button>
                        </label>
                    </section>

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
                                    Base radius (km)
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
                            {/* Changes in delivery charges in the code */}
                            <div>
                                <label className={labelCls}>
                                    Extra per km beyond radius (Rs.)
                                </label>
                                <input
                                    type="number"
                                    min="0"
                                    step="0.01"
                                    className={input}
                                    value={form.delivery_per_km}
                                    onChange={(e) =>
                                        set("delivery_per_km", e.target.value)
                                    }
                                />
                            </div>
                        </div>
                        <p className="text-xs text-gray-400">
                            Delivery fee = base fee within the base radius, plus
                            the per-km charge for each km beyond it.
                        </p>
                    </section>

                    {/* Payments */}
                    <section className="bg-white rounded-xl shadow-sm p-6 space-y-4">
                        <h2 className="font-semibold text-gray-800">Payments</h2>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelCls}>
                                    Advance required (%)
                                </label>
                                <input
                                    type="number"
                                    min="0"
                                    max="100"
                                    step="1"
                                    className={input}
                                    value={form.advance_payment_percent}
                                    onChange={(e) =>
                                        set(
                                            "advance_payment_percent",
                                            e.target.value
                                        )
                                    }
                                />
                            </div>
                            <div>
                                <label className={labelCls}>
                                    Large-order threshold (Rs.)
                                </label>
                                <input
                                    type="number"
                                    min="0"
                                    step="1"
                                    className={input}
                                    value={form.large_order_threshold}
                                    onChange={(e) =>
                                        set(
                                            "large_order_threshold",
                                            e.target.value
                                        )
                                    }
                                />
                            </div>
                        </div>
                        <p className="text-xs text-gray-400">
                            Custom / subscription orders, and any order at or
                            above the threshold, require the advance.
                        </p>

                        <div>
                            <label className={labelCls}>Bank name</label>
                            <input
                                className={input}
                                value={form.bank_name}
                                onChange={(e) =>
                                    set("bank_name", e.target.value)
                                }
                            />
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelCls}>
                                    Account title
                                </label>
                                <input
                                    className={input}
                                    value={form.bank_account_name}
                                    onChange={(e) =>
                                        set("bank_account_name", e.target.value)
                                    }
                                />
                            </div>
                            <div>
                                <label className={labelCls}>
                                    Account number / IBAN
                                </label>
                                <input
                                    className={input}
                                    value={form.bank_account_number}
                                    onChange={(e) =>
                                        set(
                                            "bank_account_number",
                                            e.target.value
                                        )
                                    }
                                />
                            </div>
                        </div>
                        <div className="grid grid-cols-2 gap-4">
                            <div>
                                <label className={labelCls}>
                                    JazzCash number
                                </label>
                                <input
                                    className={input}
                                    value={form.jazzcash_number}
                                    onChange={(e) =>
                                        set("jazzcash_number", e.target.value)
                                    }
                                />
                            </div>
                            <div>
                                <label className={labelCls}>
                                    Easypaisa number
                                </label>
                                <input
                                    className={input}
                                    value={form.easypaisa_number}
                                    onChange={(e) =>
                                        set("easypaisa_number", e.target.value)
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
