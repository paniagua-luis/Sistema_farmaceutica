import { useEffect, useState } from "react";
import { trazabilidadApi } from "../api/client";
import { useAuth } from "../context/useAuth";
import { sinZonaHoraria } from "../utils/fechaHora";

export default function TrazabilidadPage() {
  const { token } = useAuth();
  const [rows, setRows] = useState([]);
  const [loteId, setLoteId] = useState("");
  const [error, setError] = useState(null);

  async function cargar() {
    setError(null);
    try {
      const data = loteId ? await trazabilidadApi.historialLote(loteId, token) : await trazabilidadApi.listar(token);
      setRows(data || []);
    } catch (err) {
      setError(err.message);
    }
  }

  useEffect(() => {
    let activa = true;
    trazabilidadApi.listar(token)
      .then((data) => {
        if (activa) setRows(data || []);
      })
      .catch((err) => {
        if (activa) setError(err.message);
      });
    return () => {
      activa = false;
    };
  }, [token]);

  return (
    <section className="crud-page">
      <h1>Trazabilidad</h1>
      {error && <p className="error-msg">{error}</p>}
      <form
        className="crud-form inline-filter"
        onSubmit={(e) => {
          e.preventDefault();
          cargar();
        }}
      >
        <label>
          Filtrar por Lote ID
          <input value={loteId} onChange={(e) => setLoteId(e.target.value)} placeholder="ej: 1" />
        </label>
        <button type="submit">Buscar</button>
        {loteId && (
          <button
            type="button"
            onClick={() => {
              setLoteId("");
              cargar();
            }}
          >
            Ver todo
          </button>
        )}
      </form>

      <table className="crud-table">
        <thead>
          <tr>
            <th>Lote ID</th>
            <th>Usuario ID</th>
            <th>Tipo de evento</th>
            <th>Descripción</th>
            <th>Fecha</th>
          </tr>
        </thead>
        <tbody>
          {rows.map((r) => (
            <tr key={r.id}>
              <td>{r.lote_id}</td>
              <td>{r.usuario_id ?? "-"}</td>
              <td>{r.tipo_evento}</td>
              <td>{r.descripcion}</td>
              <td>{sinZonaHoraria(r.fecha)}</td>
            </tr>
          ))}
          {rows.length === 0 && (
            <tr>
              <td colSpan={5}>Sin eventos registrados.</td>
            </tr>
          )}
        </tbody>
      </table>
    </section>
  );
}
