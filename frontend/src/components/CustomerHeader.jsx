import { Link } from "react-router-dom";

import { useCart } from "../context/CartContext";

export default function CustomerHeader() {
    const { totalItems } = useCart();

    return (
        <header className="bg-amber-600 text-white px-6 py-4 flex items-center justify-between sticky top-0 z-10">
            <Link to="/" className="flex flex-col">
                <span className="text-xl font-bold leading-tight">
                    Mehak&apos;s Kitchen
                </span>
                <span className="text-amber-100 text-xs">Order online</span>
            </Link>

            <div className="flex items-center gap-4">
                <Link
                    to="/cart"
                    className="relative bg-white/20 hover:bg-white/30 px-4 py-2 rounded-lg text-sm font-medium"
                >
                    Cart
                    {totalItems > 0 && (
                        <span className="absolute -top-2 -right-2 bg-white text-amber-700 text-xs font-bold rounded-full h-5 min-w-5 px-1 flex items-center justify-center">
                            {totalItems}
                        </span>
                    )}
                </Link>
                <Link
                    to="/login"
                    className="text-sm text-amber-100 hover:text-white"
                >
                    Staff
                </Link>
            </div>
        </header>
    );
}
