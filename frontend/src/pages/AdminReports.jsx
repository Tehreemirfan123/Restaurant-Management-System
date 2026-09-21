import { useEffect, useState } from "react";

import { getReportsSummary, getSettings } from "../services/api";

const PERIODS = [
    { key: "week", label: "Weekly (last 7 days)" },
    { key: "month", label: "Monthly (last 30 days)" },
];

const rs = (v) => `Rs. ${Number(v || 0).toFixed(0)}`;

export default function AdminReports() {
    const [period, setPeriod] = useState("week");
    const [data, setData] = useState(null);
    const [business, setBusiness] = useState({ restaurant_name: "Mehak's Kitchen" });
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getSettings()
            .then(setBusiness)
            .catch(() => {});
    }, []);

    useEffect(() => {
        setLoading(true);
        getReportsSummary(period)
            .then(setData)
            .catch((err) => setError(err.message || "Failed to load report"))
            .finally(() => setLoading(false));
    }, [period]);

    const periodLabel =
        period === "week" ? "Weekly (last 7 days)" : "Monthly (last 30 days)";
    const generated = new Date().toLocaleString();

    const rows = data
        ? [
              ["Revenue", rs(data.period_revenue)],
              ["Orders", data.period_orders],
              ["New customers", data.period_new_customers],
              ["Average order value", rs(data.period_avg_order_value)],
              ["Estimated cost", rs(data.period_cost)],
              ["Estimated profit", rs(data.period_profit)],
              ["Waste value", rs(data.period_waste_value)],
          ]
        : [];

    return (
        <main className="max-w-3xl mx-auto p-6">
            {/* Controls (not printed) */}
            <div className="no-print flex flex-wrap items-center gap-3 mb-5">
                <select
                    value={period}
                    onChange={(e) => setPeriod(e.target.value)}
                    className="border border-gray-300 rounded-lg px-3 py-2 text-sm"
                >
                    {PERIODS.map((p) => (
                        <option key={p.key} value={p.key}>
                            {p.label}
                        </option>
                    ))}
                </select>
                <button
                    onClick={() => window.print()}
                    disabled={!data}
                    className="bg-maroon-700 hover:bg-maroon-800 disabled:opacity-60 text-white text-sm font-medium px-4 py-2 rounded-lg"
                >
                    Print / Download PDF
                </button>
            </div>

            {loading && <p className="text-gray-500">Loading report...</p>}
            {error && <p className="text-red-600">{error}</p>}

            {/* Printable report */}
            {data && (
                <div className="print-area bg-white rounded-xl shadow-sm p-8">
                    <div className="text-center border-b pb-4 mb-5">
                        <h1 className="text-2xl font-bold text-maroon-700">
                            {business.restaurant_name || "Mehak's Kitchen"}
                        </h1>
                        <p className="text-gray-600 mt-1">
                            {periodLabel} Performance Report
                        </p>
                        <p className="text-xs text-gray-400 mt-1">
                            Generated {generated}
                        </p>
                    </div>

                    <table className="w-full text-sm mb-6">
                        <tbody>
                            {rows.map(([label, value]) => (
                                <tr key={label} className="border-b last:border-0">
                                    <td className="py-2 text-gray-600">
                                        {label}
                                    </td>
                                    <td className="py-2 text-right font-semibold text-gray-800">
                                        {value}
                                    </td>
                                </tr>
                            ))}
                        </tbody>
                    </table>

                    <h2 className="font-semibold text-gray-800 mb-2">
                        Top selling items
                    </h2>
                    {data.top_items.length === 0 ? (
                        <p className="text-sm text-gray-400">No sales recorded.</p>
                    ) : (
                        <table className="w-full text-sm mb-6">
                            <tbody>
                                {data.top_items.map((item) => (
                                    <tr
                                        key={item.name}
                                        className="border-b last:border-0"
                                    >
                                        <td className="py-1.5 text-gray-700">
                                            {item.name}
                                        </td>
                                        <td className="py-1.5 text-right text-gray-500">
                                            {item.quantity} sold
                                        </td>
                                    </tr>
                                ))}
                            </tbody>
                        </table>
                    )}

                    <div className="grid grid-cols-2 gap-4 text-sm border-t pt-4">
                        <div>
                            <p className="text-gray-500">Total customers</p>
                            <p className="font-semibold text-gray-800">
                                {data.total_customers}
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-500">Repeat customers</p>
                            <p className="font-semibold text-gray-800">
                                {data.repeat_customers} (
                                {data.second_order_rate}%)
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-500">Average rating</p>
                            <p className="font-semibold text-gray-800">
                                {data.feedback_count
                                    ? `${data.average_rating}★`
                                    : "—"}
                            </p>
                        </div>
                        <div>
                            <p className="text-gray-500">All-time revenue</p>
                            <p className="font-semibold text-gray-800">
                                {rs(data.total_revenue)}
                            </p>
                        </div>
                    </div>

                    <p className="text-center text-xs text-gray-400 mt-8">
                        {business.restaurant_name || "Mehak's Kitchen"} ·
                        confidential
                    </p>
                </div>
            )}
        </main>
    );
}
