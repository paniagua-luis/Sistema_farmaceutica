import { NavLink, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { tienePermiso } from "../utils/permisos";

const MODULOS = [
  { to: "/medicamentos", label: "Medicamentos", permiso: "medicamentos.gestionar" },
  { to: "/proveedores", label: "Proveedores", permiso: "proveedores.gestionar" },
  { to: "/sucursales", label: "Sucursales", permiso: "sucursales.gestionar" },
  { to: "/lotes", label: "Lotes", permiso: "lotes.gestionar" },
  { to: "/alertas", label: "Alertas", permiso: "lotes.gestionar" },
  { to: "/inspecciones", label: "Inspecciones", permiso: "calidad.gestionar" },
  { to: "/despachos", label: "Despachos", permiso: "despachos.gestionar" },
  { to: "/monitoreo", label: "Monitoreo Temp.", permiso: "temperatura.gestionar" },
  { to: "/trazabilidad", label: "Trazabilidad", permiso: "trazabilidad.consultar" },
  { to: "/reportes", label: "Reportes", permiso: "reportes.consultar" },
  { to: "/perfil", label: "Mi perfil" },
  { to: "/usuarios", label: "Usuarios", permiso: "usuarios.gestionar" },
];

export default function Navbar() {
  const { username, rol, logout } = useAuth();
  const navigate = useNavigate();

  function handleLogout() {
    logout();
    navigate("/login");
  }

  return (
    <header className="navbar">
      <div className="navbar-top">
        <NavLink to="/" className="navbar-brand" aria-label="FarmaControl, inicio">
          <span className="brand-symbol" aria-hidden="true">+</span>
          <span className="brand-copy">
            <strong>FarmaControl</strong>
            <small>FARMACIA · OPERACIONES</small>
          </span>
        </NavLink>
        <p className="navbar-status"><span />Sistema conectado</p>
        <div className="navbar-user">
          <span className="user-avatar" aria-hidden="true">{username?.trim().slice(0, 1).toUpperCase() || "U"}</span>
          <span className="user-copy">
            <strong>{username}</strong>
            <small>{rol}</small>
          </span>
          <button className="logout-button" onClick={handleLogout}>Salir</button>
        </div>
      </div>
      <nav className="navbar-links" aria-label="Módulos">
        {MODULOS.filter((m) => !m.permiso || tienePermiso(rol, m.permiso)).map((m) => (
          <NavLink key={m.to} to={m.to} className={({ isActive }) => (isActive ? "active" : "")}>
            {m.label}
          </NavLink>
        ))}
      </nav>
    </header>
  );
}
