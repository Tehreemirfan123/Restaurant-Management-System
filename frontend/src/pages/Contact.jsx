import { useEffect, useState } from "react";

import { DISPLAY_PHONE } from "../config";
import { getOrderingStatus } from "../services/api";
import { whatsappUrl } from "../utils/whatsapp";

export default function Contact() {
    const [info, setInfo] = useState(null);

    useEffect(() => {
        getOrderingStatus()
            .then(setInfo)
            .catch(() => {});
    }, []);

    const phone = info?.contact_phone || DISPLAY_PHONE;
    const hours = info?.opening_hours || "11:00 AM – 11:00 PM";
    const address =
        info?.address ||
        "Plot #327/A, Al Hamad Road, Al Hamad Colony, Neelum Block, Iqbal Town, Lahore";

    const mapSrc = `https://www.google.com/maps?q=${encodeURIComponent(
        address
    )}&output=embed`;

    return (
        <div className="max-w-5xl mx-auto px-6 py-10">
            <h1 className="text-3xl font-bold text-maroon-700 mb-6">
                Contact &amp; Location
            </h1>

            <div className="grid gap-6 md:grid-cols-2">
                <div className="space-y-4">
                    <div className="bg-cream-50 rounded-xl shadow-sm p-5">
                        <h2 className="font-semibold text-maroon-700 mb-1">
                            Address
                        </h2>
                        <p className="text-gray-600 text-sm">{address}</p>
                    </div>
                    <div className="bg-cream-50 rounded-xl shadow-sm p-5">
                        <h2 className="font-semibold text-maroon-700 mb-1">
                            Hours
                        </h2>
                        <p className="text-gray-600 text-sm">
                            Open daily {hours} · Lunch &amp; dinner
                        </p>
                    </div>
                    <div className="bg-cream-50 rounded-xl shadow-sm p-5">
                        <h2 className="font-semibold text-maroon-700 mb-1">
                            Order &amp; enquiries
                        </h2>
                        <p className="text-gray-600 text-sm">
                            Phone / WhatsApp: {phone}
                        </p>
                        <a
                            href={whatsappUrl(
                                "Hi Mehak's Kitchen, I'd like to order."
                            )}
                            target="_blank"
                            rel="noopener noreferrer"
                            className="inline-block mt-3 bg-[#25D366] hover:brightness-95 text-white text-sm font-semibold px-4 py-2 rounded-lg"
                        >
                            Message on WhatsApp
                        </a>
                    </div>
                    <p className="text-xs text-gray-500">
                        Delivery available within{" "}
                        {info?.delivery_radius_km
                            ? Number(info.delivery_radius_km)
                            : 3}{" "}
                        km (Rs.{" "}
                        {info?.delivery_fee
                            ? Number(info.delivery_fee).toFixed(0)
                            : 80}
                        ).
                    </p>
                </div>

                <div className="rounded-xl overflow-hidden shadow-sm min-h-72">
                    <iframe
                        title="Mehak's Kitchen location"
                        src={mapSrc}
                        className="w-full h-full min-h-72 border-0"
                        loading="lazy"
                        referrerPolicy="no-referrer-when-downgrade"
                    />
                </div>
            </div>
        </div>
    );
}
