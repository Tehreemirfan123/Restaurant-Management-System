import { useEffect, useState } from "react";
import { Link } from "react-router-dom";

import heroImg from "../assets/hero.png";
import { getTodaysMenu } from "../services/api";
import { whatsappUrl } from "../utils/whatsapp";

const IMG = "?w=600&q=60&auto=format&fit=crop";

const HIGHLIGHTS = [
    {
        title: "Fresh Daily",
        text: "A focused daily menu keeps every meal fresh and consistent.",
        image: "https://images.unsplash.com/photo-1596797038530-2c107229654b",
    },
    {
        title: "Homemade Taste",
        text: "Comforting local favourites made for lunch and dinner.",
        image: "https://images.unsplash.com/photo-1504674900247-0877df9cc836",
    },
    {
        title: "Pickup & Delivery",
        text: "Order for pickup or local delivery.",
        image: "https://images.unsplash.com/photo-1526367790999-0150786686a2",
    },
    {
        title: "Local & Convenient",
        text: "Serving nearby offices, students, hostels and households.",
        image: "https://images.unsplash.com/photo-1568901346375-23c9450c58cd",
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

    // Advance-order specials (no set day) never show a price.
    const isSpecial = (item) => !item.day_of_week;

    return (
        <div>
            {/* Hero */}
            <section className="relative">
                <img
                    src={heroImg}
                    alt="Mehak's Kitchen"
                    className="w-full h-200 md:h-170 object-cover opacity-100"
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
                                className="bg-gold-500 hover:bg-gold-600 text-maroon-900 font-bold px-5 py-2.5 rounded-xl"
                            >
                                View Menu
                            </Link>
                            <a
                                href={whatsappUrl(
                                    "Hi Mehak's Kitchen, I'd like to order today's menu."
                                )}
                                target="_blank"
                                rel="noopener noreferrer"
                                className="bg-green-700 hover:brightness-95 text-white font-bold px-5 py-2.5 rounded-xl"
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
                            className="bg-cream-50 rounded-xl shadow-sm overflow-hidden flex flex-col"
                        >
                            <img
                                src={h.image + IMG}
                                alt={h.title}
                                loading="lazy"
                                className="w-full h-32 object-cover"
                            />
                            <div className="p-5">
                                <h3 className="font-semibold text-maroon-700">
                                    {h.title}
                                </h3>
                                <p className="text-sm text-gray-600 mt-1">
                                    {h.text}
                                </p>
                            </div>
                        </div>
                    ))}
                </div>
            </section>

            {/* Today's menu */}
            <section className="max-w-5xl mx-auto px-6 pb-12">
                <div className="text-center mb-5">
                    <p className="text-sm text-gold-600 font-medium uppercase tracking-wide">
                        {today}&apos;s Menu
                    </p>
                    <h2 className="text-2xl font-bold text-maroon-700">
                        Available Today
                    </h2>
                </div>

                {todays.length === 0 ? (
                    <p className="text-center text-gray-600">
                        Check the menu for today&apos;s dish.
                    </p>
                ) : (
                    <div className="grid gap-4 sm:grid-cols-2">
                        {todays.map((item) => (
                            <div
                                key={item.id}
                                className="bg-cream-50 rounded-xl shadow-sm p-5"
                            >
                                <h3 className="font-semibold text-gray-800">
                                    {item.name}
                                </h3>
                                {item.description && (
                                    <p className="text-sm text-gray-600 mt-1">
                                        {item.description}
                                    </p>
                                )}
                                {isSpecial(item) ? (
                                    <p className="text-sm text-gold-600 font-medium mt-2">
                                        Advance order — ask for details
                                    </p>
                                ) : (
                                    <p className="text-gold-600 font-semibold mt-2">
                                        Rs. {Number(item.price).toFixed(0)}
                                    </p>
                                )}
                            </div>
                        ))}
                    </div>
                )}

                <div className="text-center mt-6">
                    <Link
                        to="/menu"
                        className="inline-block bg-maroon-700 hover:bg-maroon-800 text-white font-semibold px-6 py-2.5 rounded-lg"
                    >
                        Order now
                    </Link>
                </div>
            </section>
        </div>
    );
}
