import { useEffect, useState } from "react";

import StaffHeader from "../components/StaffHeader";
import { getReportsCosting, getReportsSummary } from "../services/api";

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
    const [costing, setCosting] = useState([]);
    const [error, setError] = useState("");
    const [loading, setLoading] = useState(true);

    useEffect(() => {
        getReportsSummary()
            .then(setData)
            .catch((err) => setError(err.message || "Failed to load reports"))
            .finally(() => setLoading(false));
        getReportsCosting()
            .then((rows) => setCosting(rows || []))
            .catch(() => {});
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
                            <Stat
                                label="Customers"
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

                        {/* Dish costing & contribution */}
                        <div className="bg-white rounded-xl shadow-sm p-5 mt-4">
                            <h2 className="font-semibold text-gray-800 mb-1">
                                Dish costing &amp; contribution
                            </h2>
                            <p className="text-xs text-gray-400 mb-3">
                                Contribution = price − ingredient cost −
                                packaging. Add recipes and ingredient costs for
                                accurate numbers.
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
                                                        <span className="ml-1 text-xs text-amber-600">
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
                                                        Number(c.contribution) <
                                                        0
                                                            ? "text-red-600"
                                                            : "text-green-700"
                                                    }`}
                                                >
                                                    {Number(
                                                        c.contribution
                                                    ).toFixed(0)}
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
        </div>
    );
}
