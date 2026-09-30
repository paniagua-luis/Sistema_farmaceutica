import { Routes, Route, Navigate } from "react-router-dom";
import ProtectedRoute from "./components/ProtectedRoute";
import Layout from "./components/Layout";

import LoginPage from "./pages/LoginPage";
import RegisterPage from "./pages/RegisterPage";
import DashboardPage from "./pages/DashboardPage";
import AlertasPage from "./pages/AlertasPage";
import MedicamentosPage from "./pages/MedicamentosPage";
import ProveedoresPage from "./pages/ProveedoresPage";
import SucursalesPage from "./pages/SucursalesPage";
import LotesPage from "./pages/LotesPage";
import InspeccionesPage from "./pages/InspeccionesPage";
import DespachosPage from "./pages/DespachosPage";
import MonitoreoPage from "./pages/MonitoreoPage";
import TrazabilidadPage from "./pages/TrazabilidadPage";
import ReportesPage from "./pages/ReportesPage";
import PerfilPage from "./pages/PerfilPage";
import UsuariosPage from "./pages/UsuariosPage";

export default function App() {
  return (
    <Routes>
      <Route path="/login" element={<LoginPage />} />
      <Route path="/registro" element={<RegisterPage />} />

      <Route element={<ProtectedRoute />}>
        <Route element={<Layout />}>
          <Route path="/" element={<DashboardPage />} />
          <Route path="/perfil" element={<PerfilPage />} />
          <Route element={<ProtectedRoute permission="usuarios.gestionar" />}>
            <Route path="/usuarios" element={<UsuariosPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="medicamentos.gestionar" />}>
            <Route path="/medicamentos" element={<MedicamentosPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="proveedores.gestionar" />}>
            <Route path="/proveedores" element={<ProveedoresPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="sucursales.gestionar" />}>
            <Route path="/sucursales" element={<SucursalesPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="lotes.gestionar" />}>
            <Route path="/lotes" element={<LotesPage />} />
            <Route path="/alertas" element={<AlertasPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="calidad.gestionar" />}>
            <Route path="/inspecciones" element={<InspeccionesPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="despachos.gestionar" />}>
            <Route path="/despachos" element={<DespachosPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="temperatura.gestionar" />}>
            <Route path="/monitoreo" element={<MonitoreoPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="trazabilidad.consultar" />}>
            <Route path="/trazabilidad" element={<TrazabilidadPage />} />
          </Route>
          <Route element={<ProtectedRoute permission="reportes.consultar" />}>
            <Route path="/reportes" element={<ReportesPage />} />
          </Route>
        </Route>
      </Route>

      <Route path="*" element={<Navigate to="/" replace />} />
    </Routes>
  );
}
