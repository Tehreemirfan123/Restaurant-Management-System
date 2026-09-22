import { Navigate, Route, Routes } from "react-router-dom";

import AdminLayout from "./components/AdminLayout";
import CustomerLayout from "./components/CustomerLayout";
import ProtectedRoute from "./components/ProtectedRoute";
import About from "./pages/About";
import Contact from "./pages/Contact";
import Home from "./pages/Home";
import AdminCustomers from "./pages/AdminCustomers";
import AdminDashboard from "./pages/AdminDashboard";
import AdminInventory from "./pages/AdminInventory";
import AdminMenu from "./pages/AdminMenu";
import AdminOrders from "./pages/AdminOrders";
import AdminPayments from "./pages/AdminPayments";
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
            {/* Public / customer website */}
            <Route element={<CustomerLayout />}>
                <Route path="/" element={<Home />} />
                <Route path="/about" element={<About />} />
                <Route path="/menu" element={<CustomerMenu />} />
                <Route path="/contact" element={<Contact />} />
                <Route path="/cart" element={<Cart />} />
                <Route path="/order/:id" element={<OrderTracking />} />
            </Route>
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

            {/* Admin console (Dashboard is the landing screen) */}
            <Route
                path="/admin"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminLayout />
                    </ProtectedRoute>
                }
            >
                <Route index element={<AdminDashboard />} />
                <Route path="reports" element={<AdminReports />} />
                <Route path="orders" element={<AdminOrders />} />
                <Route path="payments" element={<AdminPayments />} />
                <Route path="menu" element={<AdminMenu />} />
                <Route path="recipes" element={<AdminRecipesPage />} />
                <Route path="inventory" element={<AdminInventory />} />
                <Route path="waste" element={<AdminWaste />} />
                <Route path="customers" element={<AdminCustomers />} />
                <Route path="staff" element={<AdminStaff />} />
                <Route path="settings" element={<AdminSettings />} />
            </Route>

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

export default App;
