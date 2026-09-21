import { useEffect, useState } from "react";

import { createStaff, getStaff } from "../services/api";

const EMPTY = {
    username: "",
    full_name: "",
    password: "",
    role: "staff",
};

export default function AdminStaff() {
    const [staff, setStaff] = useState([]);
    const [form, setForm] = useState(EMPTY);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    function load() {
        getStaff()
            .then((data) => setStaff(data || []))
            .catch((err) => setError(err.message || "Failed to load staff"))
            .finally(() => setLoading(false));
    }

    useEffect(load, []);

    async function handleSubmit(e) {
        e.preventDefault();
        setError("");

        try {
            await createStaff(form);
            setForm(EMPTY);
            load();
        } catch (err) {
            setError(err.message || "Could not create staff member");
        }
    }

    return (

            <main className="max-w-4xl mx-auto p-6 grid gap-6 md:grid-cols-3">
                <form
                    onSubmit={handleSubmit}
                    className="bg-white rounded-xl shadow-sm p-5 space-y-3 h-fit"
                >
                    <h2 className="font-semibold text-gray-800">
                        Add staff member
                    </h2>

                    <input
                        type="text"
                        placeholder="Full name"
                        required
                        value={form.full_name}
                        onChange={(e) =>
                            setForm({ ...form, full_name: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <input
                        type="text"
                        placeholder="Username"
                        required
                        value={form.username}
                        onChange={(e) =>
                            setForm({ ...form, username: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <input
                        type="password"
                        placeholder="Password (min 6 chars)"
                        required
                        value={form.password}
                        onChange={(e) =>
                            setForm({ ...form, password: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    />
                    <select
                        value={form.role}
                        onChange={(e) =>
                            setForm({ ...form, role: e.target.value })
                        }
                        className="w-full border border-gray-300 rounded-lg px-3 py-2 text-sm"
                    >
                        <option value="staff">Staff</option>
                        <option value="admin">Admin</option>
                    </select>

                    {error && <p className="text-red-600 text-sm">{error}</p>}

                    <button
                        type="submit"
                        className="w-full bg-maroon-700 hover:bg-maroon-800 text-white text-sm font-medium py-2 rounded-lg"
                    >
                        Add
                    </button>
                </form>

                <div className="md:col-span-2 space-y-2">
                    {loading && <p className="text-gray-500">Loading...</p>}
                    {staff.map((member) => (
                        <div
                            key={member.id}
                            className="bg-white rounded-xl shadow-sm p-4 flex items-center justify-between"
                        >
                            <div>
                                <p className="font-medium text-gray-800">
                                    {member.full_name}
                                </p>
                                <p className="text-sm text-gray-500">
                                    @{member.username}
                                </p>
                            </div>
                            <span
                                className={`text-xs px-2 py-1 rounded-full capitalize ${
                                    member.role === "admin"
                                        ? "bg-purple-100 text-purple-800"
                                        : "bg-gray-100 text-gray-700"
                                }`}
                            >
                                {member.role}
                            </span>
                        </div>
                    ))}
                </div>
            </main>
    );
}
