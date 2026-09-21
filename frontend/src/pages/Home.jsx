import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import heroImg from "../assets/hero.png";
import { getTodaysMenu } from "../services/api";
import { whatsappUrl } from "../utils/whatsapp";

const HIGHLIGHTS = [
    {
        title: "Fresh Daily",
        text: "A focused daily menu keeps every meal fresh and consistent.",
    },
    {
        title: "Homemade Taste",
        text: "Comforting local favourites made for lunch and dinner.",
    },
    {
        title: "Pickup & Delivery",
        text: "Order for pickup or local delivery within 3 km.",
    },
    {
        title: "Local & Convenient",
        text: "Serving nearby offices, students, hostels and households.",
    },
];

export default function Home() {
    const today = new Date().toLocaleDateString(undefined, {
        weekday: "long",
    });
    const [todays, setTodays] = useState([]);

    useEffect(() => {
        getTodaysMenu()
            .then((d) => setTodays(d || []))
            .catch(() => {});
    }, []);

    return (
        <div>
            {/* Hero */}
            <section className="relative">
                <img
                    src={heroImg}
                    alt="Mehak's Kitchen"
                    className="w-full h-72 md:h-96 object-cover"
                />
                <div className="absolute inset-0 bg-maroon-900/60 flex items-center">
                    <div className="max-w-5xl mx-auto px-6 w-full text-white">
                        <p className="text-gold-200 uppercase tracking-wide text-sm">
                            Khanoon ki Mehak
                        </p>
                        <h1 className="text-3xl md:text-5xl font-bold mt-2 max-w-xl">
                            Fresh Homemade Meals, Prepared Daily
                        </h1>
                        <p className="mt-3 text-cream-100 max-w-lg">
                            One day, one main dish — comforting lunch and dinner
                            for pickup or delivery.
                        </p>
                        <div className="mt-6 flex flex-wrap gap-3">
                            <Link
                                to="/menu"
                                className="bg-gold-500 hover:bg-gold-600 text-maroon-900 font-semibold px-5 py-2.5 rounded-lg"
                            >
                                View Menu
                            </Link>
                            <a
                                href={whatsappUrl(
                                    "Hi Mehak's Kitchen, I'd like to order today's menu."
                                )}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="bg-[#25D366] hover:brightness-95 text-white font-semibold px-5 py-2.5 rounded-lg"
                            >
                                Order on WhatsApp
                            </a>
                        </div>
                    </div>
                </div>
            </section>

            {/* Highlights */}
            <section className="max-w-5xl mx-auto px-6 py-10">
                <div className="grid gap-4 sm:grid-cols-2 lg:grid-cols-4">
                    {HIGHLIGHTS.map((h) => (
                        <div
                            key={h.title}
                            className="bg-cream-50 rounded-xl shadow-sm p-5"
                        >
                            <h3 className="font-semibold text-maroon-700">
                                {h.title}
                            </h3>
                            <p className="text-sm text-gray-600 mt-1">
                                {h.text}
                            </p>
                        </div>
                    ))}
                </div>
            </section>

            {/* Today's dish */}
            <section className="max-w-5xl mx-auto px-6 pb-12">
                <div className="bg-cream-50 rounded-2xl shadow-sm p-6 md:p-8 text-center">
                    <p className="text-sm text-gold-600 font-medium uppercase tracking-wide">
                        {today}&apos;s Menu
                    </p>
                    {todays.length > 0 ? (
                        <>
                            <h2 className="text-2xl font-bold text-maroon-700 mt-1">
                                {todays[0].name}
                            </h2>
                            {todays[0].description && (
                                <p className="text-gray-600 mt-1">
                                    {todays[0].description}
                                </p>
                            )}
                            <p className="text-gold-600 font-semibold mt-2">
                                Rs. {Number(todays[0].price).toFixed(0)}
                            </p>
                        </>
                    ) : (
                        <h2 className="text-xl font-semibold text-gray-600 mt-2">
                            Check today&apos;s dish on the menu
                        </h2>
                    )}
                    <Link
                        to="/menu"
                        className="inline-block mt-5 bg-maroon-700 hover:bg-maroon-800 text-white font-semibold px-6 py-2.5 rounded-lg"
                    >
                        Order now
                    </Link>
                </div>
            </section>
        </div>
    );
}
