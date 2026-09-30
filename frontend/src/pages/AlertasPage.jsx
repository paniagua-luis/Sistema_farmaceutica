import { useEffect, useState } from "react";
import { loteApi } from "../api/client";
import { useAuth } from "../context/useAuth";

export default function AlertasPage() {
  const { token } = useAuth();
  const [alertas, setAlertas] = useState([]);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(true);

  async function actualizar() {
    setCargando(true);
    setError(null);
    try {
      setAlertas(await loteApi.alertasStockBajo(token));
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  }

  useEffect(() => {
    let activa = true;
    loteApi.alertasStockBajo(token)
      .then((data) => {
        if (activa) setAlertas(data || []);
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

  return (
    <section className="stock-alerts-page" aria-labelledby="stock-alerts-title">
      <header className="stock-alerts-header">
        <div>
          <p className="eyebrow">INVENTARIO / SEGUIMIENTO</p>
          <h1 id="stock-alerts-title">Alertas de stock bajo</h1>
          <p className="subtitle">Existencias por debajo del umbral configurado para cada medicamento.</p>
        </div>
        <div className="stock-alerts-controls">
          <span className="reception-count">{String(alertas.length).padStart(2, "0")} ALERTAS</span>
          <button type="button" onClick={actualizar} disabled={cargando}>
            {cargando ? "Actualizando..." : "Actualizar"}
          </button>
        </div>
      </header>
      {error && <p className="error-msg" role="alert">{error}</p>}
      {!error && cargando && <p role="status">Cargando alertas...</p>}
      {!error && !cargando && alertas.length === 0 && <p>No hay alertas de stock bajo.</p>}
      {!error && !cargando && alertas.length > 0 && (
        <div className="table-wrap">
          <table className="crud-table">
            <thead>
              <tr>
                <th>Medicamento</th>
                <th>Sucursal</th>
                <th>Stock disponible</th>
                <th>Umbral</th>
              </tr>
            </thead>
            <tbody>
              {alertas.map((alerta) => (
                <tr key={`${alerta.medicamento_id}-${alerta.sucursal_id}`}>
                  <td>{alerta.medicamento}</td>
                  <td>{alerta.sucursal}</td>
                  <td className="stock-alert-value">{alerta.stock_disponible}</td>
                  <td>{alerta.umbral ?? "No informado"}</td>
                </tr>
              ))}
            </tbody>
          </table>
        </div>
      )}
    </section>
  );
}