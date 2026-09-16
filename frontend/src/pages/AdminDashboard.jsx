import StaffHeader from "../components/StaffHeader";

const TILES = [
    "Menu Management",
    "Inventory",
    "Staff",
    "Reports",
];

export default function AdminDashboard() {
    return (
        <div className="min-h-screen bg-gray-100">
            <StaffHeader title="Admin Dashboard" />
            <main className="max-w-4xl mx-auto p-6">
                <p className="text-gray-600 mb-4">
                    Welcome to the admin console. Feature modules are being
                    built out over the coming days.
                </p>
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {TILES.map((t) => (
                        <div
                            key={t}
                            className="bg-white rounded-xl shadow-sm p-6"
                        >
                            <h2 className="text-base font-semibold text-gray-800">
                                {t}
                            </h2>
                            <span className="mt-3 block text-xs text-gray-400">
                                Coming soon
                            </span>
                        </div>
                    ))}
                </div>
            </main>
        </div>
    );
}
