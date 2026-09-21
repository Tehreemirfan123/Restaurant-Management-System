import { useEffect, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import { getReportsSummary } from "../services/api";

function Stat({ label, value }) {
    return (
        <div className="bg-white rounded-xl shadow-sm p-5">
            <p className="text-sm text-gray-500">{label}</p>
            <p className="text-2xl font-bold text-gray-800 mt-1">{value}</p>
        </div>
    );
}

export default function AdminReports() {
    const [data, setData] = useState(null);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getReportsSummary()
            .then(setData)
            .catch((err) => setError(err.message || "Failed to load reports"))
            .finally(() => setLoading(false));
    }, []);

    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Reports" />

            <main className="max-w-4xl mx-auto p-6">
                {loading && <p className="text-gray-500">Loading reports...</p>}
                {error && <p className="text-red-600">{error}</p>}

                {data && (
                    <>
                        <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 mb-6">
                            <Stat
                                label="Today's revenue"
                                value={`Rs. ${Number(
                                    data.today_revenue
                                ).toFixed(0)}`}
                            />
                            <Stat
                                label="Today's orders"
                                value={data.today_orders}
                            />
                            <Stat
                                label="Total revenue"
                                value={`Rs. ${Number(
                                    data.total_revenue
                                ).toFixed(0)}`}
                            />
                            <Stat
                                label="Total orders"
                                value={data.total_orders}
                            />
                        </div>

                        <div className="grid gap-4 md:grid-cols-2">
                            <div className="bg-white rounded-xl shadow-sm p-5">
                                <h2 className="font-semibold text-gray-800 mb-3">
                                    Top selling items
                                </h2>
                                {data.top_items.length === 0 ? (
                                    <p className="text-sm text-gray-400">
                                        No sales yet.
                                    </p>
                                ) : (
                                    <ul className="space-y-2">
                                        {data.top_items.map((item) => (
                                            <li
                                                key={item.name}
                                                className="flex justify-between text-sm"
                                            >
                                                <span className="text-gray-700">
                                                    {item.name}
                                                </span>
                                                <span className="text-gray-500">
                                                    {item.quantity} sold
                                                </span>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>

                            <div className="bg-white rounded-xl shadow-sm p-5">
                                <h2 className="font-semibold text-gray-800 mb-3">
                                    Low stock
                                </h2>
                                {data.low_stock.length === 0 ? (
                                    <p className="text-sm text-gray-400">
                                        Everything is well stocked.
                                    </p>
                                ) : (
                                    <ul className="space-y-2">
                                        {data.low_stock.map((item) => (
                                            <li
                                                key={item.id}
                                                className="flex justify-between text-sm"
                                            >
                                                <span className="text-red-700">
                                                    {item.name}
                                                </span>
                                                <span className="text-gray-500">
                                                    {Number(
                                                        item.quantity
                                                    ).toFixed(0)}{" "}
                                                    {item.unit} left
                                                </span>
                                            </li>
                                        ))}
                                    </ul>
                                )}
                            </div>
                        </div>
                    </>
                )}
            </main>
        </div>
    );
}
