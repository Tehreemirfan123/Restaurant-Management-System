import { DELIVERY_FEE, WHATSAPP_NUMBER } from "../config";

/**
 * Build a wa.me link with a pre-filled order message. This is the primary
 * ordering path per the business plan: the customer taps through to
 * WhatsApp, where the owner confirms and takes payment.
 */
export function buildWhatsappOrderUrl({
    items,
    orderType,
    address,
    name,
    phone,
}) {
    const lines = items.map(
        (i) => `- ${i.quantity} x ${i.name} (Rs. ${i.price * i.quantity})`
    );

    const subtotal = items.reduce(
        (sum, i) => sum + i.price * i.quantity,
        0
    );
    const fee = orderType === "delivery" ? DELIVERY_FEE : 0;

    const parts = [
        "Hi Mehak's Kitchen, I'd like to order:",
        "",
        ...lines,
        "",
        `Type: ${orderType === "delivery" ? "Delivery" : "Pickup"}`,
    ];

    if (name) parts.push(`Name: ${name}`);
    if (phone) parts.push(`Phone: ${phone}`);

    if (orderType === "delivery") {
        parts.push(`Address: ${address || "(to share)"}`);
        parts.push(`Delivery fee: Rs. ${fee}`);
    }

    parts.push(`Total: Rs. ${subtotal + fee}`);

    const text = encodeURIComponent(parts.join("\n"));
    return `https://wa.me/${WHATSAPP_NUMBER}?text=${text}`;
}

export function whatsappUrl(text) {
    const q = text ? `?text=${encodeURIComponent(text)}` : "";
    return `https://wa.me/${WHATSAPP_NUMBER}${q}`;
}
