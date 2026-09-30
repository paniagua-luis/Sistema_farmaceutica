import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function LoginPage() {
  const { login, error, cargando } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    const ok = await login(username, password);
    if (ok) navigate("/");
  }

  return (
    <div className="auth-page">
      <aside className="auth-aside">
        <div className="auth-brand-lockup">
          <span className="auth-brand-symbol" aria-hidden="true">+</span>
          <span>FarmaControl</span>
        </div>
        <div className="auth-aside-copy">
          <p className="eyebrow">FARMACIA · OPERACIONES</p>
          <h2>Gestión diaria.<br />Un solo sistema.</h2>
          <p>Portal de gestión farmacéutica</p>
        </div>
        <div className="auth-aside-status"><span />Acceso para personal autorizado</div>
      </aside>
      <form className="auth-form" onSubmit={handleSubmit}>
        <h1>Iniciar sesión</h1>
        <p className="subtitle">Ingresa tus credenciales para continuar.</p>
        {error && <p className="error-msg">{error}</p>}
        <label>
          Usuario
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button type="submit" disabled={cargando}>
          {cargando ? "Ingresando..." : "Ingresar"}
        </button>
        <p>
          ¿No tenés cuenta? <Link to="/registro">Registrate</Link>
        </p>
      </form>
    </div>
  );
}
