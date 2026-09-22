// Send the browser to the gateway's hosted checkout.
//
// Sandbox and some providers use a plain GET redirect; others (JazzCash,
// Easypaisa) require an HTTP POST carrying signed fields, so we build a hidden
// form and submit it. Either way the customer leaves our site to pay and the
// gateway sends them back to /payments/callback afterwards.
export function redirectToGateway(checkout) {
    if (!checkout || !checkout.checkout_url) return;

    const method = (checkout.http_method || "GET").toUpperCase();

    if (method === "POST" && checkout.fields) {
        const form = document.createElement("form");
        form.method = "POST";
        form.action = checkout.checkout_url;
        Object.entries(checkout.fields).forEach(([name, value]) => {
            const input = document.createElement("input");
            input.type = "hidden";
            input.name = name;
            input.value = value;
            form.appendChild(input);
        });
        document.body.appendChild(form);
        form.submit();
        return;
    }

    window.location.href = checkout.checkout_url;
}
