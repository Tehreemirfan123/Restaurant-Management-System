// Business contact details (from the brochure / business plan).
// WhatsApp number in international format for wa.me links (0324-7509762).
export const WHATSAPP_NUMBER = "923247509762";
export const DISPLAY_PHONE = "0324-7509762";

// Changes in delivery charges in the code
// Fallback delivery config (live values come from /settings/status).
export const DELIVERY_FEE = 80; // base fee within the base radius
export const DELIVERY_BASE_KM = 3; // base radius covered by the base fee
export const DELIVERY_PER_KM = 26; // extra charge per km beyond the base radius

// Kitchen location (Iqbal Town, Lahore) — used to estimate delivery distance.
export const KITCHEN_LAT = 31.51;
export const KITCHEN_LNG = 74.29;

// --- Payments ---
// Methods offered at checkout. Edit this list to add/remove options; each
// `key` must match a PaymentMethodEnum value on the backend.
export const PAYMENT_METHODS = [
    { key: "cash", label: "Cash on Delivery", digital: false },
    { key: "bank_transfer", label: "Bank Transfer", digital: true },
    { key: "jazzcash", label: "JazzCash", digital: true },
    { key: "easypaisa", label: "Easypaisa", digital: true },
];

// Order kinds a customer can pick. Custom/subscription always need an advance.
export const ORDER_CATEGORIES = [
    { key: "regular", label: "Regular" },
    { key: "custom", label: "Custom order" },
    { key: "subscription", label: "Subscription" },
];

// Fallback advance rule (live values come from /settings/status).
export const ADVANCE_PERCENT = 50;
export const LARGE_ORDER_THRESHOLD = 3000;
