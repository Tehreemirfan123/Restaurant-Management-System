import { Navigate, Route, Routes } from "react-router-dom";

import AdminLayout from "./components/AdminLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import AdminCustomers from "./pages/AdminCustomers";
import AdminInventory from "./pages/AdminInventory";
import AdminMenu from "./pages/AdminMenu";
import AdminOrders from "./pages/AdminOrders";
import AdminRecipesPage from "./pages/AdminRecipes";
import AdminReports from "./pages/AdminReports";
import AdminSettings from "./pages/AdminSettings";
import AdminStaff from "./pages/AdminStaff";
import AdminWaste from "./pages/AdminWaste";
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

            {/* Admin console (Reports is the landing screen) */}
            <Route
                path="/admin"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminLayout />
                    </ProtectedRoute>
                }
            >
                <Route index element={<AdminReports />} />
                <Route path="orders" element={<AdminOrders />} />
                <Route path="menu" element={<AdminMenu />} />
                <Route path="recipes" element={<AdminRecipesPage />} />
                <Route path="inventory" element={<AdminInventory />} />
                <Route path="waste" element={<AdminWaste />} />
                <Route path="customers" element={<AdminCustomers />} />
                <Route path="staff" element={<AdminStaff />} />
                <Route path="settings" element={<AdminSettings />} />
                {/* Legacy path kept working */}
                <Route path="reports" element={<AdminReports />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

export default App;
