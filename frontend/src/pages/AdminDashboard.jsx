import { useEffect, useState } from "react";

import { getReportsCosting, getReportsSummary } from "../services/api";

const PERIODS = [
    { key: "today", label: "Today" },
    { key: "week", label: "This week" },
    { key: "month", label: "This month" },
    { key: "all", label: "All time" },
];

function Stat({ label, value, accent }) {
    return (
        <div className="bg-white rounded-xl shadow-sm p-5">
            <p className="text-sm text-gray-500">{label}</p>
            <p
                className={`text-2xl font-bold mt-1 ${
                    accent || "text-gray-800"
                }`}
            >
                {value}
            </p>
        </div>
    );
}

const rs = (v) => `Rs. ${Number(v || 0).toFixed(0)}`;

export default function AdminDashboard() {
    const [period, setPeriod] = useState("week");
    const [data, setData] = useState(null);
    const [costing, setCosting] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        setLoading(true);
        getReportsSummary(period)
            .then(setData)
            .catch((err) => setError(err.message || "Failed to load reports"))
            .finally(() => setLoading(false));
    }, [period]);

    useEffect(() => {
        getReportsCosting()
            .then((rows) => setCosting(rows || []))
            .catch(() => {});
    }, []);

    return (
        <main className="max-w-5xl mx-auto p-6">
            {/* Period selector */}
            <div className="flex gap-2 mb-5 flex-wrap">
                {PERIODS.map((p) => (
                    <button
                        key={p.key}
                        onClick={() => setPeriod(p.key)}
                        className={`px-4 py-1.5 rounded-full text-sm ${
                            period === p.key
                                ? "bg-maroon-700 text-white"
                                : "bg-white text-maroon-800 border border-gray-200"
                        }`}
                    >
                        {p.label}
                    </button>
                ))}
            </div>

            {loading && <p className="text-gray-500">Loading reports...</p>}
            {error && <p className="text-red-600">{error}</p>}

            {data && (
                <>
                    {/* Headline period metrics */}
                    <div className="grid gap-4 grid-cols-2 lg:grid-cols-3 mb-6">
                        <Stat label="Revenue" value={rs(data.period_revenue)} />
                        <Stat label="Orders" value={data.period_orders} />
                        <Stat
                            label="New customers"
                            value={data.period_new_customers}
                        />
                        <Stat
                            label="Avg order value"
                            value={rs(data.period_avg_order_value)}
                        />
                        <Stat
                            label="Est. cost"
                            value={rs(data.period_cost)}
                            accent="text-gray-700"
                        />
                        <Stat
                            label="Est. profit"
                            value={rs(data.period_profit)}
                            accent={
                                Number(data.period_profit) < 0
                                    ? "text-red-600"
                                    : "text-green-700"
                            }
                        />
                    </div>

                    {/* Standing indicators */}
                    <h2 className="text-sm font-semibold text-gray-500 uppercase tracking-wide mb-2">
                        Overall
                    </h2>
                    <div className="grid gap-4 grid-cols-2 lg:grid-cols-4 mb-6">
                        <Stat
                            label="Total customers"
                            value={data.total_customers}
                        />
                        <Stat
                            label="Repeat customers"
                            value={data.repeat_customers}
                        />
                        <Stat
                            label="Second-order rate"
                            value={`${data.second_order_rate}%`}
                        />
                        <Stat
                            label="Avg rating"
                            value={
                                data.feedback_count
                                    ? `${data.average_rating}★ (${data.feedback_count})`
                                    : "—"
                            }
                        />
                    </div>

                    <div className="grid gap-4 md:grid-cols-2 mb-6">
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
                                                {Number(item.quantity).toFixed(
                                                    0
                                                )}{" "}
                                                {item.unit} left
                                            </span>
                                        </li>
                                    ))}
                                </ul>
                            )}
                        </div>
                    </div>

                    {/* Dish costing & contribution */}
                    <div className="bg-white rounded-xl shadow-sm p-5">
                        <h2 className="font-semibold text-gray-800 mb-1">
                            Dish costing &amp; contribution
                        </h2>
                        <p className="text-xs text-gray-400 mb-3">
                            Contribution = price − ingredient cost − packaging.
                            Add recipes and ingredient costs for accurate
                            numbers.
                        </p>
                        <div className="overflow-x-auto">
                            <table className="w-full text-sm">
                                <thead>
                                    <tr className="text-left text-gray-500 border-b">
                                        <th className="py-2 pr-2">Dish</th>
                                        <th className="py-2 px-2 text-right">
                                            Price
                                        </th>
                                        <th className="py-2 px-2 text-right">
                                            Cost
                                        </th>
                                        <th className="py-2 px-2 text-right">
                                            Contribution
                                        </th>
                                        <th className="py-2 pl-2 text-right">
                                            Margin
                                        </th>
                                    </tr>
                                </thead>
                                <tbody>
                                    {costing.map((c) => (
                                        <tr
                                            key={c.menu_item_id}
                                            className="border-b last:border-0"
                                        >
                                            <td className="py-2 pr-2 text-gray-800">
                                                {c.name}
                                                {!c.has_recipe && (
                                                    <span className="ml-1 text-xs text-gold-600">
                                                        (no recipe)
                                                    </span>
                                                )}
                                            </td>
                                            <td className="py-2 px-2 text-right text-gray-600">
                                                {Number(c.price).toFixed(0)}
                                            </td>
                                            <td className="py-2 px-2 text-right text-gray-600">
                                                {Number(
                                                    c.variable_cost
                                                ).toFixed(0)}
                                            </td>
                                            <td
                                                className={`py-2 px-2 text-right font-medium ${
                                                    Number(c.contribution) < 0
                                                        ? "text-red-600"
                                                        : "text-green-700"
                                                }`}
                                            >
                                                {Number(c.contribution).toFixed(
                                                    0
                                                )}
                                            </td>
                                            <td className="py-2 pl-2 text-right text-gray-500">
                                                {c.margin_percent}%
                                            </td>
                                        </tr>
                                    ))}
                                </tbody>
                            </table>
                        </div>
                    </div>
                </>
            )}
        </main>
    );
}
