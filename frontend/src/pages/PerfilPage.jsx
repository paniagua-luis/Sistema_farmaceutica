import { useAuth } from "../context/useAuth";

export default function PerfilPage() {
  const { username, rol } = useAuth();

  return (
    <section className="crud-page profile-page">
      <header>
        <p className="eyebrow">CUENTA / SESIÓN</p>
        <h1>Mi perfil</h1>
        <p className="subtitle">Información de la cuenta con la que iniciaste sesión.</p>
      </header>
      <div className="profile-card">
        <div className="profile-avatar" aria-hidden="true">
          {username?.trim().slice(0, 1).toUpperCase() || "U"}
        </div>
        <dl className="profile-details">
          <div>
            <dt>Usuario</dt>
            <dd>{username || "No disponible"}</dd>
          </div>
          <div>
            <dt>Rol de acceso</dt>
            <dd>{rol?.replace(/[_-]+/g, " ") || "No disponible"}</dd>
          </div>
        </dl>
        <p className="profile-note">Los permisos de acceso dependen del rol asignado a esta cuenta.</p>
      </div>
    </section>
  );
}
