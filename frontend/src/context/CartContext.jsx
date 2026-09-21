import { createContext, useContext, useEffect, useMemo, useState } from "react";

const CartContext = createContext(null);

const STORAGE_KEY = "mk_cart";

function loadCart() {
    try {
        const raw = localStorage.getItem(STORAGE_KEY);
        return raw ? JSON.parse(raw) : [];
    } catch {
        return [];
    }
}

export function CartProvider({ children }) {
    // Each cart line: { id, name, price, quantity }
    const [items, setItems] = useState(loadCart);

    useEffect(() => {
        try {
            localStorage.setItem(STORAGE_KEY, JSON.stringify(items));
        } catch {
            // Ignore storage failures (private mode etc.) — cart stays in memory.
        }
    }, [items]);

    function addItem(menuItem) {
        setItems((current) => {
            const existing = current.find((i) => i.id === menuItem.id);

            if (existing) {
                return current.map((i) =>
                    i.id === menuItem.id
                        ? { ...i, quantity: i.quantity + 1 }
                        : i
                );
            }

            return [
                ...current,
                {
                    id: menuItem.id,
                    name: menuItem.name,
                    price: Number(menuItem.price),
                    quantity: 1,
                },
            ];
        });
    }

    function setQuantity(id, quantity) {
        setItems((current) => {
            if (quantity <= 0) {
                return current.filter((i) => i.id !== id);
            }
            return current.map((i) =>
                i.id === id ? { ...i, quantity } : i
            );
        });
    }

    function removeItem(id) {
        setItems((current) => current.filter((i) => i.id !== id));
    }

    function clearCart() {
        setItems([]);
    }

    const totalItems = useMemo(
        () => items.reduce((sum, i) => sum + i.quantity, 0),
        [items]
    );

    const totalAmount = useMemo(
        () => items.reduce((sum, i) => sum + i.price * i.quantity, 0),
        [items]
    );

    const value = {
        items,
        addItem,
        setQuantity,
        removeItem,
        clearCart,
        totalItems,
        totalAmount,
    };

    return (
        <CartContext.Provider value={value}>
            {children}
        </CartContext.Provider>
    );
}

export function useCart() {
    const ctx = useContext(CartContext);
    if (!ctx) {
        throw new Error("useCart must be used within a CartProvider");
    }
    return ctx;
}
