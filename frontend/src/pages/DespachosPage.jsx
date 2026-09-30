import { useCallback, useEffect, useState } from "react";
import { despachoApi, loteApi, sucursalApi } from "../api/client";
import { useAuth } from "../context/useAuth";
import { sinZonaHoraria } from "../utils/fechaHora";

function productosDisponibles(lote) {
  if (Array.isArray(lote.productos) && lote.productos.length > 0) {
    return lote.productos.map((producto) => ({
      medicamento_id: producto.medicamento_id,
      medicamento: producto.medicamento,
      cantidad_disponible: producto.cantidad_disponible ?? (
        producto.medicamento_id === lote.medicamento_id ? lote.cantidad_disponible : 0
      ),
    })).filter((producto) => producto.cantidad_disponible > 0);
  }

  if (lote.medicamento_id && lote.cantidad_disponible > 0) {
    return [{
      medicamento_id: lote.medicamento_id,
      medicamento: lote.medicamento,
      cantidad_disponible: lote.cantidad_disponible,
    }];
  }

  return [];
}

function nuevaLinea(id) {
  return { id, lote_id: "", medicamento_id: "", cantidad_despachada: "" };
}

export default function DespachosPage() {
  const { token } = useAuth();
  const [lotes, setLotes] = useState([]);
  const [sucursales, setSucursales] = useState([]);
  const [despachos, setDespachos] = useState([]);
  const [sucursalId, setSucursalId] = useState("");
  const [lineas, setLineas] = useState([nuevaLinea(0)]);
  const [siguienteId, setSiguienteId] = useState(1);
  const [cargando, setCargando] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [confirmandoId, setConfirmandoId] = useState(null);
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  const cargarDatos = useCallback(async () => {
    const [lotesData, sucursalesData, despachosData] = await Promise.all([
      loteApi.listar(token),
      sucursalApi.listar(token),
      despachoApi.listar(token),
    ]);
    setLotes(lotesData);
    setSucursales(sucursalesData);
    setDespachos(despachosData);
  }, [token]);

  useEffect(() => {
    let activa = true;
    Promise.all([
      loteApi.listar(token),
      sucursalApi.listar(token),
      despachoApi.listar(token),
    ])
      .then(([lotesData, sucursalesData, despachosData]) => {
        if (!activa) return;
        setLotes(lotesData);
        setSucursales(sucursalesData);
        setDespachos(despachosData);
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
  }, [cargarDatos, token]);

  function cambiarLinea(id, nombre, valor) {
    setLineas((actuales) => actuales.map((linea) => (
      linea.id === id ? { ...linea, [nombre]: valor } : linea
    )));
  }

  function seleccionarLote(lineaId, loteId) {
    const lote = lotes.find((actual) => String(actual.id) === loteId);
    const productos = lote ? productosDisponibles(lote) : [];
    setLineas((actuales) => actuales.map((linea) => (
      linea.id === lineaId
        ? {
            ...linea,
            lote_id: loteId,
            medicamento_id: productos.length === 1 ? String(productos[0].medicamento_id) : "",
            cantidad_despachada: "",
          }
        : linea
    )));
  }

  function agregarLinea() {
    setLineas((actuales) => [...actuales, nuevaLinea(siguienteId)]);
    setSiguienteId((actual) => actual + 1);
    setError(null);
    setMensaje(null);
  }

  function quitarLinea(id) {
    setLineas((actuales) => actuales.length > 1
      ? actuales.filter((linea) => linea.id !== id)
      : actuales);
  }

  function obtenerStock(linea) {
    const lote = lotes.find((actual) => String(actual.id) === String(linea.lote_id));
    const producto = lote && productosDisponibles(lote).find(
      (actual) => String(actual.medicamento_id) === String(linea.medicamento_id),
    );
    return producto?.cantidad_disponible ?? 0;
  }

  async function registrarDespachos(event) {
    event.preventDefault();
    setError(null);
    setMensaje(null);

    if (!sucursalId) {
      setError("Selecciona una sucursal de destino.");
      return;
    }

    const agregados = new Map();
    for (let index = 0; index < lineas.length; index += 1) {
      const linea = lineas[index];
      const lote = lotes.find((actual) => String(actual.id) === String(linea.lote_id));
      const producto = lote && productosDisponibles(lote).find(
        (actual) => String(actual.medicamento_id) === String(linea.medicamento_id),
      );
      const cantidad = Number(linea.cantidad_despachada);

      if (!lote) {
        setError(`Selecciona un lote válido en la línea ${index + 1}.`);
        return;
      }
      if (lote.estado_lote !== "aprobado") {
        setError(`El lote ${lote.codigo_lote} no está aprobado para despacho.`);
        return;
      }
      if (!producto) {
        setError(`Selecciona un medicamento con existencias en la línea ${index + 1}.`);
        return;
      }
      if (!Number.isInteger(cantidad) || cantidad <= 0) {
        setError(`La cantidad de la línea ${index + 1} debe ser un entero mayor que cero.`);
        return;
      }

      const claveStock = `${lote.id}:${producto.medicamento_id}`;
      const entradaExistente = agregados.get(claveStock);
      const acumulado = (entradaExistente?.cantidad_despachada || 0) + cantidad;
      if (acumulado > producto.cantidad_disponible) {
        setError(`La cantidad total del lote ${lote.codigo_lote} para ${producto.medicamento} excede las existencias disponibles (${producto.cantidad_disponible}).`);
        return;
      }
      agregados.set(claveStock, {
        lote_id: lote.id,
        medicamento_id: producto.medicamento_id,
        cantidad_despachada: acumulado,
      });
    }
    const datos = [...agregados.values()];

    setGuardando(true);
    try {
      const despachosRegistrados = await despachoApi.registrarMultiple({
        sucursal_id: Number(sucursalId),
        productos: datos,
      }, token);
      setLineas([nuevaLinea(siguienteId)]);
      setSiguienteId((actual) => actual + 1);
      const cantidadRegistrada = Array.isArray(despachosRegistrados) ? despachosRegistrados.length : datos.length;
      setMensaje(`${cantidadRegistrada} ${cantidadRegistrada === 1 ? "despacho registrado" : "despachos registrados"} para la sucursal seleccionada.`);
      try {
        await cargarDatos();
      } catch (errorCarga) {
        setError(`Los despachos se registraron, pero no se pudo actualizar la información en pantalla: ${errorCarga.message}`);
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  }

  async function confirmarRecepcion(despachoId) {
    setError(null);
    setMensaje(null);
    setConfirmandoId(despachoId);
    try {
      await despachoApi.confirmarRecepcion(despachoId, token);
      await cargarDatos();
      setMensaje("Recepción del despacho confirmada.");
    } catch (err) {
      setError(err.message);
    } finally {
      setConfirmandoId(null);
    }
  }

  return (
    <section className="crud-page">
      <header>
        <p className="eyebrow">DISTRIBUCIÓN / INVENTARIO</p>
        <h1>Distribución y Despacho</h1>
        <p className="subtitle">Envía varios lotes o medicamentos a una misma sucursal.</p>
      </header>

      {error && <p className="error-msg" role="alert">{error}</p>}
      {mensaje && <p className="success-msg" role="status">{mensaje}</p>}
      {cargando && <p role="status">Cargando lotes y sucursales...</p>}

      <form className="dispatch-form" onSubmit={registrarDespachos}>
        <label>
          Sucursal destino
          <select
            required
            value={sucursalId}
            disabled={cargando || guardando}
            onChange={(event) => setSucursalId(event.target.value)}
          >
            <option value="">Seleccionar sucursal</option>
            {sucursales.map((sucursal) => (
              <option key={sucursal.id} value={sucursal.id}>
                {sucursal.codigo_sucursal} - {sucursal.nombre}
              </option>
            ))}
          </select>
        </label>

        {lineas.map((linea, index) => {
          const lote = lotes.find((actual) => String(actual.id) === String(linea.lote_id));
          const productos = lote ? productosDisponibles(lote) : [];
          const stock = obtenerStock(linea);
          return (
            <fieldset className="dispatch-line" key={linea.id}>
              <legend>Producto {index + 1}</legend>
              <label>
                Medicamento / lote
                <select
                  required
                  value={linea.lote_id}
                  disabled={cargando || guardando}
                  onChange={(event) => seleccionarLote(linea.id, event.target.value)}
                >
                  <option value="">Seleccionar medicamento</option>
                  {lotes.filter((item) => item.estado_lote === "aprobado" && productosDisponibles(item).length > 0).map((item) => (
                    <option key={item.id} value={item.id}>
                      {productosDisponibles(item)
                        .map((producto) => `${producto.medicamento} (${producto.cantidad_disponible})`)
                        .join(", ")} · Lote {item.codigo_lote}
                    </option>
                  ))}
                </select>
              </label>

              {productos.length > 1 && (
                <label>
                  Medicamento
                  <select
                    required
                    value={linea.medicamento_id}
                    disabled={guardando}
                    onChange={(event) => cambiarLinea(linea.id, "medicamento_id", event.target.value)}
                  >
                    <option value="">Seleccionar medicamento</option>
                    {productos.map((producto) => (
                      <option key={producto.medicamento_id} value={producto.medicamento_id}>
                        {producto.medicamento} (disp: {producto.cantidad_disponible})
                      </option>
                    ))}
                  </select>
                </label>
              )}

              {productos.length === 1 && (
                <p className="dispatch-product-stock">
                  {productos[0].medicamento} · {productos[0].cantidad_disponible} disponibles
                </p>
              )}

              <label>
                Cantidad despachada
                <input
                  required
                  type="number"
                  min="1"
                  max={stock || undefined}
                  step="1"
                  value={linea.cantidad_despachada}
                  disabled={guardando || !linea.medicamento_id}
                  onChange={(event) => cambiarLinea(linea.id, "cantidad_despachada", event.target.value)}
                />
                {linea.medicamento_id && <small>Máximo disponible: {stock}</small>}
              </label>

              <button
                className="secondary-action remove-lot-button"
                type="button"
                onClick={() => quitarLinea(linea.id)}
                disabled={lineas.length === 1 || guardando}
                aria-label={`Quitar línea ${index + 1}`}
              >
                Quitar
              </button>
            </fieldset>
          );
        })}

        <div className="dispatch-actions">
          <button className="secondary-action" type="button" onClick={agregarLinea} disabled={guardando || cargando}>
            + Agregar lote o medicamento
          </button>
          <button type="submit" disabled={guardando || cargando || lotes.length === 0 || sucursales.length === 0}>
            {guardando ? "Registrando despachos..." : "Registrar despachos"}
          </button>
        </div>
      </form>

      <section className="crud-page" aria-labelledby="dispatch-history-title">
        <h2 id="dispatch-history-title">Despachos registrados</h2>
        {despachos.length === 0 && !cargando && <p>No hay despachos registrados.</p>}
        {despachos.length > 0 && (
          <div className="table-wrap">
            <table className="crud-table">
              <thead>
                <tr>
                  <th>Código</th>
                  <th>Lote</th>
                  <th>Medicamento</th>
                  <th>Sucursal ID</th>
                  <th>Cantidad</th>
                  <th>Estado</th>
                  <th>Fecha</th>
                  <th>Acciones</th>
                </tr>
              </thead>
              <tbody>
                {despachos.map((despacho) => {
                  const lote = lotes.find((item) => item.id === despacho.lote_id);
                  const producto = lote?.productos?.find(
                    (item) => item.medicamento_id === despacho.medicamento_id,
                  ) || (lote?.medicamento_id === despacho.medicamento_id ? lote : null);
                  return (
                    <tr key={despacho.id}>
                      <td>{despacho.codigo_despacho}</td>
                      <td>{lote?.codigo_lote || despacho.lote_id}</td>
                      <td>{producto?.medicamento || despacho.medicamento_id || "—"}</td>
                      <td>{despacho.sucursal_id}</td>
                      <td>{despacho.cantidad_despachada}</td>
                      <td>{despacho.estado_despacho}</td>
                      <td>{sinZonaHoraria(despacho.fecha_despacho)}</td>
                      <td>
                        {despacho.estado_despacho === "recibido" ? "Recibido" : (
                          <button
                            type="button"
                            disabled={confirmandoId !== null}
                            onClick={() => confirmarRecepcion(despacho.id)}
                          >
                            {confirmandoId === despacho.id ? "Confirmando..." : "Confirmar recepción"}
                          </button>
                        )}
                      </td>
                    </tr>
                  );
                })}
              </tbody>
            </table>
          </div>
        )}
      </section>
    </section>
  );
}
