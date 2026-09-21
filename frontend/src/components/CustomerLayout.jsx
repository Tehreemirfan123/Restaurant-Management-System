import { useEffect, useState } from "react";
import { Link, NavLink, Outlet } from "react-router-dom";

import { DISPLAY_PHONE } from "../config";
import { useCart } from "../context/CartContext";
import { getOrderingStatus } from "../services/api";
import { whatsappUrl } from "../utils/whatsapp";

const LINKS = [
    { to: "/", label: "Home", end: true },
    { to: "/about", label: "About Us" },
    { to: "/menu", label: "Menu" },
    { to: "/contact", label: "Contact" },
];

export default function CustomerLayout() {
    const { totalItems } = useCart();
    const [info, setInfo] = useState(null);

    useEffect(() => {
        getOrderingStatus()
            .then(setInfo)
            .catch(() => {});
    }, []);

    const name = info?.restaurant_name || "Mehak's Kitchen";
    const phone = info?.contact_phone || DISPLAY_PHONE;
    const hours = info?.opening_hours || "11:00 AM – 11:00 PM";
    const address =
        info?.address ||
        "Plot #327/A, Al Hamad Road, Neelum Block, Iqbal Town, Lahore";

    return (
        <div className="min-h-screen flex flex-col bg-cream-100">
            {/* Nav */}
            <header className="bg-maroon-700 text-white sticky top-0 z-20">
                <div className="max-w-5xl mx-auto px-4 py-3 flex items-center justify-between gap-3">
                    <Link to="/" className="font-bold text-lg leading-none">
                        {name}
                        <span className="block text-[10px] font-normal text-gold-200">
                            Khanoon ki Mehak
                        </span>
                    </Link>

                    <nav className="flex items-center gap-1 text-sm overflow-x-auto">
                        {LINKS.map((l) => (
                            <NavLink
                                key={l.to}
                                to={l.to}
                                end={l.end}
                                className={({ isActive }) =>
                                    `px-3 py-1.5 rounded-lg whitespace-nowrap ${
                                        isActive
                                            ? "bg-white/15 font-medium"
                                            : "text-gold-100 hover:bg-white/10"
                                    }`
                                }
                            >
                                {l.label}
                            </NavLink>
                        ))}
                        <Link
                            to="/cart"
                            className="relative ml-1 bg-white/20 hover:bg-white/30 px-3 py-1.5 rounded-lg font-medium"
                        >
                            Cart
                            {totalItems > 0 && (
                                <span className="absolute -top-2 -right-2 bg-white text-maroon-800 text-xs font-bold rounded-full h-5 min-w-5 px-1 flex items-center justify-center">
                                    {totalItems}
                                </span>
                            )}
                        </Link>
                    </nav>
                </div>
            </header>

            {/* Page */}
            <main className="flex-1">
                <Outlet />
            </main>

            {/* Footer */}
            <footer className="bg-maroon-900 text-gold-100 mt-10">
                <div className="max-w-5xl mx-auto px-4 py-8 grid gap-6 sm:grid-cols-3 text-sm">
                    <div>
                        <p className="font-bold text-white text-base">{name}</p>
                        <p className="mt-1 text-gold-200">
                            Fresh homemade meals, prepared daily.
                        </p>
                    </div>
                    <div>
                        <p className="font-semibold text-white mb-1">Visit us</p>
                        <p>{address}</p>
                        <p className="mt-1">Open daily {hours}</p>
                    </div>
                    <div>
                        <p className="font-semibold text-white mb-1">Order</p>
                        <a
                            href={whatsappUrl(
                                "Hi Mehak's Kitchen, I'd like to order."
                            )}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="text-[#25D366] font-medium"
                        >
                            WhatsApp {phone}
                        </a>
                        <p className="mt-2">
                            <Link to="/login" className="hover:underline">
                                Staff login
                            </Link>
                        </p>
                    </div>
                </div>
                <div className="border-t border-white/10 py-3 text-center text-xs text-gold-200">
                    © {new Date().getFullYear()} {name}
                </div>
            </footer>
        </div>
    );
}
