import { useState } from "react";
import { Link, useNavigate } from "react-router-dom";
import { useAuth } from "../context/useAuth";

export default function RegisterPage() {
  const { registrar, error, cargando } = useAuth();
  const [username, setUsername] = useState("");
  const [password, setPassword] = useState("");
  const [exito, setExito] = useState(false);
  const navigate = useNavigate();

  async function handleSubmit(e) {
    e.preventDefault();
    setExito(false);
    const ok = await registrar(username, password);
    if (ok) {
      setExito(true);
      setTimeout(() => navigate("/login"), 1200);
    }
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
        <h1>Crear cuenta</h1>
        <p className="subtitle">Registro de usuario</p>
        {error && <p className="error-msg">{error}</p>}
        {exito && <p className="success-msg">Usuario creado. Redirigiendo al login...</p>}
        <label>
          Usuario
          <input value={username} onChange={(e) => setUsername(e.target.value)} required />
        </label>
        <label>
          Contraseña
          <input type="password" value={password} onChange={(e) => setPassword(e.target.value)} required />
        </label>
        <button type="submit" disabled={cargando}>
          {cargando ? "Creando..." : "Registrarme"}
        </button>
        <p>
          ¿Ya tenés cuenta? <Link to="/login">Iniciar sesión</Link>
        </p>
      </form>
    </div>
  );
}
