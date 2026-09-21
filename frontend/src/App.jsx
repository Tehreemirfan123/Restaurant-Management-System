import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import AdminCustomers from "./pages/AdminCustomers";
import AdminDashboard from "./pages/AdminDashboard";
import AdminInventory from "./pages/AdminInventory";
import AdminMenu from "./pages/AdminMenu";
import AdminReports from "./pages/AdminReports";
import AdminStaff from "./pages/AdminStaff";
import Cart from "./pages/Cart";
import CustomerMenu from "./pages/CustomerMenu";
import Kitchen from "./pages/Kitchen";
import Login from "./pages/Login";
import OrderTracking from "./pages/OrderTracking";
import POS from "./pages/POS";
import StaffDashboard from "./pages/StaffDashboard";
import Tables from "./pages/Tables";

function App() {
    return (
        <Routes>
            {/* Public / customer */}
            <Route path="/" element={<CustomerMenu />} />
            <Route path="/cart" element={<Cart />} />
            <Route path="/order/:id" element={<OrderTracking />} />
            <Route path="/login" element={<Login />} />

            {/* Staff */}
            <Route
                path="/staff"
                element={
                    <ProtectedRoute>
                        <StaffDashboard />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/staff/pos"
                element={
                    <ProtectedRoute>
                        <POS />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/staff/kitchen"
                element={
                    <ProtectedRoute>
                        <Kitchen />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/staff/tables"
                element={
                    <ProtectedRoute>
                        <Tables />
                    </ProtectedRoute>
                }
            />

            {/* Admin */}
            <Route
                path="/admin"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminDashboard />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/menu"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminMenu />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/inventory"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminInventory />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/staff"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminStaff />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/customers"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminCustomers />
                    </ProtectedRoute>
                }
            />
            <Route
                path="/admin/reports"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminReports />
                    </ProtectedRoute>
                }
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

export default App;
