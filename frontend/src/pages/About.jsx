export default function About() {
    return (
        <div className="max-w-3xl mx-auto px-6 py-10">
            <h1 className="text-3xl font-bold text-maroon-700">About Us</h1>
            <p className="text-gray-600 mt-4 leading-relaxed">
                Mehak&apos;s Kitchen is a home-based kitchen in Iqbal Town,
                Lahore, serving fresh, homemade lunch and dinner to people who
                value familiar taste, hygiene and convenience but don&apos;t
                always have the time to cook. Every day we prepare one carefully
                chosen main dish, cooked fresh and made to feel like home food —
                because that&apos;s exactly what it is.
            </p>

            <div className="grid gap-4 sm:grid-cols-2 mt-8">
                <div className="bg-cream-50 rounded-xl shadow-sm p-5">
                    <h2 className="font-semibold text-maroon-700">
                        Our promise
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Fresh, homemade, hygienic and tasty food with dependable
                        portions — the same quality every single day.
                    </p>
                </div>
                <div className="bg-cream-50 rounded-xl shadow-sm p-5">
                    <h2 className="font-semibold text-maroon-700">Who we serve</h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Nearby offices, university students, hostel residents and
                        local households looking for reliable everyday meals.
                    </p>
                </div>
                <div className="bg-cream-50 rounded-xl shadow-sm p-5">
                    <h2 className="font-semibold text-maroon-700">
                        A rotating menu
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        One main dish each day of the week, plus Mutton Kunna on
                        advance special order — predictable variety, carefully
                        prepared.
                    </p>
                </div>
                <div className="bg-cream-50 rounded-xl shadow-sm p-5">
                    <h2 className="font-semibold text-maroon-700">
                        Easy ordering
                    </h2>
                    <p className="text-sm text-gray-600 mt-1">
                        Order directly on WhatsApp or online, and choose pickup
                        or local delivery within 3 km.
                    </p>
                </div>
            </div>
        </div>
    );
}
