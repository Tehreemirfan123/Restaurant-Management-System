import { Link } from "react-router-dom";

import StaffHeader from "../components/StaffHeader";

const TILES = [
    { label: "POS", to: "/staff/pos", desc: "Take orders & payments", ready: false },
    { label: "Kitchen", to: "/staff/kitchen", desc: "Live order queue", ready: false },
    { label: "Tables", to: "/staff/tables", desc: "Floor status", ready: false },
];

export default function StaffDashboard() {
    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Staff Dashboard" />
            <main className="max-w-4xl mx-auto p-6 grid gap-4 sm:grid-cols-3">
                {TILES.map((t) => (
                    <div
                        key={t.label}
                        className="bg-white rounded-xl shadow-sm p-6 flex flex-col"
                    >
                        <h2 className="text-lg font-semibold text-gray-800">
                            {t.label}
                        </h2>
                        <p className="text-sm text-gray-500 mt-1 flex-1">
                            {t.desc}
                        </p>
                        {t.ready ? (
                            <Link
                                to={t.to}
                                className="mt-4 text-amber-600 font-medium"
                            >
                                Open →
                            </Link>
                        ) : (
                            <span className="mt-4 text-xs text-gray-400">
                                Coming soon
                            </span>
                        )}
                    </div>
                ))}
            </main>
        </div>
    );
}
