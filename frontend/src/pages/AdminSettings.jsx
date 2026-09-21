import { useEffect, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import { getSettings, updateSettings } from "../services/api";

export default function AdminSettings() {
    const [accepting, setAccepting] = useState(true);
    const [cap, setCap] = useState("");
    const [loading, setLoading] = useState(true);
    const [saving, setSaving] = useState(false);
    const [error, setError] = useState("");
    const [saved, setSaved] = useState(false);

    useEffect(() => {
        getSettings()
            .then((s) => {
                setAccepting(s.accepting_orders);
                setCap(s.daily_order_cap ?? "");
            })
            .catch((err) => setError(err.message || "Failed to load settings"))
            .finally(() => setLoading(false));
    }, []);

    async function handleSave() {
        setError("");
        setSaved(false);
        setSaving(true);
        try {
            await updateSettings({
                accepting_orders: accepting,
                daily_order_cap: cap === "" ? null : Number(cap),
            });
            setSaved(true);
        } catch (err) {
            setError(err.message || "Could not save");
        } finally {
            setSaving(false);
        }
    }

    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Settings" />

            <main className="max-w-lg mx-auto p-6">
                {loading && <p className="text-gray-500">Loading...</p>}

                {!loading && (
                    <div className="bg-white rounded-xl shadow-sm p-6 space-y-5">
                        <label className="flex items-center justify-between">
                            <span className="text-gray-800 font-medium">
                                Accepting orders
                            </span>
                            <input
                                type="checkbox"
                                checked={accepting}
                                onChange={(e) =>
                                    setAccepting(e.target.checked)
                                }
                                className="h-5 w-5"
                            />
                        </label>
                        <p className="text-xs text-gray-400 -mt-3">
                            Turn off to stop taking new orders (e.g. when at
                            capacity or closed).
                        </p>

                        <div>
                            <label className="block text-sm font-medium text-gray-700 mb-1">
                                Daily order limit
                            </label>
                            <input
                                type="number"
                                min="0"
                                placeholder="No limit"
                                value={cap}
                                onChange={(e) => setCap(e.target.value)}
                                className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                            />
                            <p className="text-xs text-gray-400 mt-1">
                                Blocks new orders once this many are placed
                                today. Leave blank for no limit. (Pilot: 5)
                            </p>
                        </div>

                        {error && (
                            <p className="text-red-600 text-sm">{error}</p>
                        )}
                        {saved && (
                            <p className="text-green-600 text-sm">Saved.</p>
                        )}

                        <button
                            onClick={handleSave}
                            disabled={saving}
                            className="w-full bg-maroon-700 hover:bg-maroon-800 disabled:opacity-60 text-white font-semibold py-2.5 rounded-lg"
                        >
                            {saving ? "Saving..." : "Save"}
                        </button>
                    </div>
                )}
            </main>
        </div>
    );
}
