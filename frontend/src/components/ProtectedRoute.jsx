import { Navigate, Outlet } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { tienePermiso } from "../utils/permisos";

export default function ProtectedRoute({ permission }) {
  const { token, rol } = useAuth();
  if (!token) return <Navigate to="/login" replace />;
  if (permission && !tienePermiso(rol, permission)) return <Navigate to="/" replace />;
  return <Outlet />;
}
