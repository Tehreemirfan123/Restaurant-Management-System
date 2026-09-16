import { Navigate, Route, Routes } from "react-router-dom";

import ProtectedRoute from "./components/ProtectedRoute";
import AdminDashboard from "./pages/AdminDashboard";
import CustomerMenu from "./pages/CustomerMenu";
import Login from "./pages/Login";
import StaffDashboard from "./pages/StaffDashboard";

function App() {
    return (
        <Routes>
            {/* Public / customer */}
            <Route path="/" element={<CustomerMenu />} />
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

            {/* Admin */}
            <Route
                path="/admin"
                element={
                    <ProtectedRoute adminOnly>
                        <AdminDashboard />
                    </ProtectedRoute>
                }
            />

            {/* Fallback */}
            <Route path="*" element={<Navigate to="/" replace />} />
        </Routes>
    );
}

export default App;
