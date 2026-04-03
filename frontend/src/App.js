import "@/App.css";
import { BrowserRouter, Routes, Route, Navigate } from "react-router-dom";
import { AuthProvider, useAuth } from "@/contexts/AuthContext";
import { Toaster } from "@/components/ui/sonner";
import Landing from "@/pages/Landing";
import Login from "@/pages/Login";
import Register from "@/pages/Register";
import SMEDashboard from "@/pages/SMEDashboard";
import SubmitRFP from "@/pages/SubmitRFP";
import RFPDetail from "@/pages/RFPDetail";
import ClientPortal from "@/pages/ClientPortal";

function ProtectedRoute({ children, allowedRoles }) {
  const { user, loading } = useAuth();
  if (loading) return <div className="min-h-screen flex items-center justify-center text-muted-foreground">Loading...</div>;
  if (!user) return <Navigate to="/login" replace />;
  if (allowedRoles && !allowedRoles.includes(user.role)) return <Navigate to="/" replace />;
  return children;
}

function AppRoutes() {
  const { user, loading } = useAuth();

  if (loading) return <div className="min-h-screen flex items-center justify-center text-muted-foreground">Loading...</div>;

  return (
    <Routes>
      <Route path="/" element={user ? <Navigate to={user.role === "client" ? "/client" : "/dashboard"} replace /> : <Landing />} />
      <Route path="/login" element={user ? <Navigate to={user.role === "client" ? "/client" : "/dashboard"} replace /> : <Login />} />
      <Route path="/register" element={user ? <Navigate to={user.role === "client" ? "/client" : "/dashboard"} replace /> : <Register />} />
      <Route path="/dashboard" element={<ProtectedRoute allowedRoles={["admin", "owner", "sales"]}><SMEDashboard /></ProtectedRoute>} />
      <Route path="/submit-rfp" element={<ProtectedRoute><SubmitRFP /></ProtectedRoute>} />
      <Route path="/rfp/:rfpId" element={<ProtectedRoute><RFPDetail /></ProtectedRoute>} />
      <Route path="/client" element={<ProtectedRoute allowedRoles={["client"]}><ClientPortal /></ProtectedRoute>} />
    </Routes>
  );
}

function App() {
  return (
    <BrowserRouter>
      <AuthProvider>
        <AppRoutes />
        <Toaster />
      </AuthProvider>
    </BrowserRouter>
  );
}

export default App;
