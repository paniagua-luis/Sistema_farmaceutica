import { Link } from "react-router-dom";
import { useAuth } from "../context/useAuth";
import { tienePermiso } from "../utils/permisos";

const TARJETAS = [
  { to: "/medicamentos", label: "Medicamentos", permiso: "medicamentos.gestionar", desc: "Ficha técnica y rangos de temperatura." },
  { to: "/proveedores", label: "Proveedores", permiso: "proveedores.gestionar", desc: "Catálogo de proveedores." },
  { to: "/sucursales", label: "Sucursales", permiso: "sucursales.gestionar", desc: "Puntos de destino de la distribución." },
  { to: "/lotes", label: "Lotes", permiso: "lotes.gestionar", desc: "Recepción, stock y estado de cada lote." },
  { to: "/alertas", label: "Alertas de stock", permiso: "lotes.gestionar", desc: "Medicamentos por debajo del mínimo de existencias." },
  { to: "/inspecciones", label: "Inspecciones", permiso: "calidad.gestionar", desc: "Aprobación o rechazo de calidad." },
  { to: "/despachos", label: "Despachos", permiso: "despachos.gestionar", desc: "Distribución a sucursales." },
  { to: "/monitoreo", label: "Monitoreo Temp.", permiso: "temperatura.gestionar", desc: "Cadena de frío." },
  { to: "/trazabilidad", label: "Trazabilidad", permiso: "trazabilidad.consultar", desc: "Historial de eventos por lote." },
  { to: "/reportes", label: "Reportes", permiso: "reportes.consultar", desc: "Informes regulatorios y consolidados." },
];

export default function DashboardPage() {
  const { username, rol } = useAuth();
  const disponibles = TARJETAS.filter((t) => tienePermiso(rol, t.permiso));

  return (
    <section className="dashboard-page">
      <header className="dashboard-heading">
        <div>
          <p className="eyebrow">FARMACONTROL / OPERACIONES</p>
          <h1>Hola, {username}</h1>
          <p className="subtitle">Panel de gestión farmacéutica</p>
        </div>
        <div className="dashboard-role">
          <span className="session-status"><span /></span>
          <div>
            <small>SESIÓN ACTIVA</small>
            <strong>{rol}</strong>
          </div>
        </div>
      </header>
      <div className="dashboard-section-heading">
        <h2>Áreas de trabajo</h2>
        <span>{String(disponibles.length).padStart(2, "0")} MÓDULOS</span>
      </div>
      <div className="dashboard-grid">
        {disponibles.map((t, index) => (
          <Link key={t.to} to={t.to} className="dashboard-card">
            <div className="dashboard-card-top">
              <span className="dashboard-card-index">{String(index + 1).padStart(2, "0")}</span>
              <span className="dashboard-card-arrow" aria-hidden="true">↗</span>
            </div>
            <h3>{t.label}</h3>
            <p>{t.desc}</p>
          </Link>
        ))}
        {disponibles.length === 0 && <p>Tu rol no tiene módulos asignados todavía.</p>}
      </div>
    </section>
  );
}
