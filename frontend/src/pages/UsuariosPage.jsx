import { useEffect, useState } from "react";
import { useNavigate } from "react-router-dom";
import { usuarioApi } from "../api/client";
import { useAuth } from "../context/useAuth";
import { ROLES_DISPONIBLES } from "../utils/permisos";

const LABELS_ROL = {
  administrador: "Administrador",
  almacen: "Almacén",
  personal_calidad: "Personal de calidad",
  personal_sucursal: "Personal de sucursal",
  proveedor: "Proveedor",
  ente_regulador: "Ente regulador",
};

export default function UsuariosPage() {
  const { token, username, logout } = useAuth();
  const navigate = useNavigate();
  const [usuarios, setUsuarios] = useState([]);
  const [rolesSeleccionados, setRolesSeleccionados] = useState({});
  const [cargando, setCargando] = useState(true);
  const [guardandoId, setGuardandoId] = useState(null);
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  useEffect(() => {
    let activa = true;
    usuarioApi.listar(token)
      .then((data) => {
        if (!activa) return;
        setUsuarios(data);
        setRolesSeleccionados(Object.fromEntries(data.map((usuario) => [usuario.id, usuario.rol])));
      })
      .catch((err) => {
        if (activa) setError(err.message);
      })
      .finally(() => {
        if (activa) setCargando(false);
      });
    return () => {
      activa = false;
    };
  }, [token]);

  async function guardarRol(usuario) {
    const rol = rolesSeleccionados[usuario.id];
    if (!rol || rol === usuario.rol) return;

    setError(null);
    setMensaje(null);
    setGuardandoId(usuario.id);
    try {
      const actualizado = await usuarioApi.actualizarRol(usuario.id, rol, token);
      setUsuarios((actuales) => actuales.map((actual) =>
        actual.id === actualizado.id ? actualizado : actual
      ));
      setRolesSeleccionados((actuales) => ({ ...actuales, [actualizado.id]: actualizado.rol }));
      if (actualizado.username === username && actualizado.rol !== usuario.rol) {
        logout();
        navigate("/login", { replace: true });
        return;
      }
      setMensaje(`Rol de ${actualizado.username} actualizado a ${LABELS_ROL[actualizado.rol] || actualizado.rol}.`);
    } catch (err) {
      setError(err.message);
      setRolesSeleccionados((actuales) => ({ ...actuales, [usuario.id]: usuario.rol }));
    } finally {
      setGuardandoId(null);
    }
  }

  return (
    <section className="crud-page">
      <header>
        <p className="eyebrow">ADMINISTRACIÓN / ACCESOS</p>
        <h1>Usuarios y roles</h1>
        <p className="subtitle">Solo un administrador puede asignar o cambiar el rol de una cuenta.</p>
      </header>
      {error && <p className="error-msg" role="alert">{error}</p>}
      {mensaje && <p className="success-msg" role="status">{mensaje}</p>}
      {cargando && <p role="status">Cargando usuarios...</p>}
      {!cargando && !error && usuarios.length === 0 && <p>No hay usuarios registrados.</p>}
      {!cargando && usuarios.length > 0 && (
        <div className="table-wrap">
          <table className="crud-table users-table">
            <thead>
              <tr>
                <th>Usuario</th>
                <th>Rol actual</th>
                <th>Asignar rol</th>
                <th>Acción</th>
              </tr>
            </thead>
            <tbody>
              {usuarios.map((usuario) => {
                const rolSeleccionado = rolesSeleccionados[usuario.id] ?? usuario.rol;
                const propio = usuario.username === username;
                return (
                  <tr key={usuario.id}>
                    <td>{usuario.username}{propio ? " (tú)" : ""}</td>
                    <td>{LABELS_ROL[usuario.rol] || usuario.rol}</td>
                    <td>
                      <select
                        aria-label={`Asignar rol a ${usuario.username}`}
                        value={rolSeleccionado}
                        disabled={guardandoId !== null}
                        onChange={(event) => setRolesSeleccionados((actuales) => ({
                          ...actuales,
                          [usuario.id]: event.target.value,
                        }))}
                      >
                        {ROLES_DISPONIBLES.map((rol) => (
                          <option key={rol} value={rol}>{LABELS_ROL[rol] || rol}</option>
                        ))}
                      </select>
                    </td>
                    <td>
                      <button
                        type="button"
                        disabled={guardandoId !== null || rolSeleccionado === usuario.rol}
                        onClick={() => guardarRol(usuario)}
                      >
                        {guardandoId === usuario.id ? "Guardando..." : "Guardar rol"}
                      </button>
                    </td>
                  </tr>
                );
              })}
            </tbody>
          </table>
        </div>
      )}
      <p className="profile-note">
        El backend impide retirar el rol al último administrador. Si cambias tu propio rol, se cerrará tu sesión para actualizar los permisos.
      </p>
    </section>
  );
}
