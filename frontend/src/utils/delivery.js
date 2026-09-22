import {
    DELIVERY_BASE_KM,
    DELIVERY_FEE,
    DELIVERY_PER_KM,
    KITCHEN_LAT,
    KITCHEN_LNG,
} from "../config";

// Changes in delivery charges in the code
// Delivery fee = base fee (within baseKm) + per-km charge for every km beyond.
export function computeDeliveryFee(distanceKm, cfg = {}) {
    const base = Number(cfg.baseFee ?? DELIVERY_FEE);
    const baseKm = Number(cfg.baseKm ?? DELIVERY_BASE_KM);
    const perKm = Number(cfg.perKm ?? DELIVERY_PER_KM);

    if (distanceKm == null || distanceKm === "" || isNaN(Number(distanceKm))) {
        return base;
    }
    const d = Number(distanceKm);
    if (d <= baseKm) return base;
    // Keep this linear so the quoted fee matches the backend charge exactly.
    return Math.round(base + (d - baseKm) * perKm);
}

// Straight-line (haversine) distance in km between two lat/lng points.
export function haversineKm(lat1, lng1, lat2, lng2) {
    const R = 6371;
    const toRad = (x) => (x * Math.PI) / 180;
    const dLat = toRad(lat2 - lat1);
    const dLng = toRad(lng2 - lng1);
    const a =
        Math.sin(dLat / 2) ** 2 +
        Math.cos(toRad(lat1)) *
            Math.cos(toRad(lat2)) *
            Math.sin(dLng / 2) ** 2;
    return R * 2 * Math.atan2(Math.sqrt(a), Math.sqrt(1 - a));
}

// Estimate distance from the kitchen using the browser's geolocation.
export function estimateDistanceFromLocation() {
    return new Promise((resolve, reject) => {
        if (!navigator.geolocation) {
            reject(new Error("Location is not available on this device"));
            return;
        }
        navigator.geolocation.getCurrentPosition(
            (pos) => {
                const km = haversineKm(
                    KITCHEN_LAT,
                    KITCHEN_LNG,
                    pos.coords.latitude,
                    pos.coords.longitude
                );
                resolve(Math.round(km * 10) / 10);
            },
            () => reject(new Error("Could not get your location")),
            { enableHighAccuracy: true, timeout: 10000 }
        );
    });
}
