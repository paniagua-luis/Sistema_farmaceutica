import { useEffect, useState } from "react";
import CrudPage from "../components/CrudPage";
import { loteApi, medicamentoApi, proveedorApi, sucursalApi } from "../api/client";
import { useAuth } from "../context/useAuth";

const CAMPOS_RECEPCION = [
  { name: "codigo_lote", label: "Código de lote", type: "text" },
  { name: "proveedor_id", label: "Proveedor", type: "select", optionsKey: "proveedores" },
  { name: "sucursal_id", label: "Sucursal", type: "select", optionsKey: "sucursales" },
  { name: "fecha_recepcion", label: "Fecha de recepción", type: "date" },
  { name: "fecha_vencimiento", label: "Fecha de vencimiento", type: "date" },
];

const ESTADOS = ["pendiente_verificacion", "aprobado", "rechazado", "vencido", "dado_de_baja"];

async function loadOptions(token) {
  const [medicamentos, proveedores, sucursales] = await Promise.all([
    medicamentoApi.listar(token),
    proveedorApi.listar(token),
    sucursalApi.listar(token),
  ]);
  return {
    medicamentos: medicamentos.map((m) => ({ value: m.id, label: `${m.codigo_medicamento} - ${m.nombre}` })),
    proveedores: proveedores.map((p) => ({ value: p.id, label: `${p.codigo_proveedor} - ${p.nombre}` })),
    sucursales: sucursales.map((s) => ({ value: s.id, label: `${s.codigo_sucursal} - ${s.nombre}` })),
  };
}

function fechaLocalHoy() {
  const hoy = new Date();
  const mes = String(hoy.getMonth() + 1).padStart(2, "0");
  const dia = String(hoy.getDate()).padStart(2, "0");
  return `${hoy.getFullYear()}-${mes}-${dia}`;
}

function RecepcionMultiple({ onRegistrar }) {
  const { token } = useAuth();
  const [siguienteId, setSiguienteId] = useState(1);
  const crearFila = (id) => ({
    id,
    datos: { fecha_recepcion: fechaLocalHoy() },
    productos: [{ id: 0, medicamento_id: "", cantidad_recibida: "" }],
  });
  const [filas, setFilas] = useState(() => [crearFila(0)]);
  const [opciones, setOpciones] = useState({});
  const [cargandoOpciones, setCargandoOpciones] = useState(true);
  const [guardando, setGuardando] = useState(false);
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);

  useEffect(() => {
    let activa = true;
    loadOptions(token)
      .then((data) => {
        if (activa) setOpciones(data);
      })
      .catch((err) => {
        if (activa) setError(err.message);
      })
      .finally(() => {
        if (activa) setCargandoOpciones(false);
      });
    return () => {
      activa = false;
    };
  }, [token]);

  function cambiarDato(id, nombre, valor) {
    setFilas((actuales) => actuales.map((fila) =>
      fila.id === id ? { ...fila, datos: { ...fila.datos, [nombre]: valor } } : fila
    ));
  }

  function cambiarProducto(loteId, productoId, nombre, valor) {
    setFilas((actuales) => actuales.map((fila) =>
      fila.id === loteId
        ? {
            ...fila,
            productos: fila.productos.map((producto) =>
              producto.id === productoId ? { ...producto, [nombre]: valor } : producto
            ),
          }
        : fila
    ));
  }

  function agregarProducto(loteId) {
    setFilas((actuales) => actuales.map((fila) => {
      if (fila.id !== loteId) return fila;
      const siguienteProductoId = Math.max(...fila.productos.map((producto) => producto.id)) + 1;
      return {
        ...fila,
        productos: [...fila.productos, { id: siguienteProductoId, medicamento_id: "", cantidad_recibida: "" }],
      };
    }));
    setError(null);
    setMensaje(null);
  }

  function quitarProducto(loteId, productoId) {
    setFilas((actuales) => actuales.map((fila) =>
      fila.id === loteId && fila.productos.length > 1
        ? { ...fila, productos: fila.productos.filter((producto) => producto.id !== productoId) }
        : fila
    ));
  }

  function agregarFila() {
    setFilas((actuales) => [...actuales, crearFila(siguienteId)]);
    setSiguienteId((actual) => actual + 1);
    setError(null);
    setMensaje(null);
  }

  function quitarFila(id) {
    setFilas((actuales) => actuales.length > 1 ? actuales.filter((fila) => fila.id !== id) : actuales);
  }

  async function handleSubmit(event) {
    event.preventDefault();
    setError(null);
    setMensaje(null);
    setGuardando(true);

    try {
      const lotes = filas.map(({ datos, productos }, index) => {
        const faltante = CAMPOS_RECEPCION.find(({ name }) => !String(datos[name] ?? "").trim());
        if (faltante) {
          throw new Error(`Completa "${faltante.label}" en el lote ${index + 1}.`);
        }

        const proveedorId = Number(datos.proveedor_id);
        const sucursalId = Number(datos.sucursal_id);
        if (![proveedorId, sucursalId].every((id) => Number.isInteger(id) && id > 0)) {
          throw new Error(`Selecciona proveedor y sucursal válidos para el lote ${index + 1}.`);
        }
        if (productos.length === 0) {
          throw new Error(`Agrega al menos un medicamento al lote ${index + 1}.`);
        }
        if (datos.fecha_vencimiento < datos.fecha_recepcion) {
          throw new Error(`La fecha de vencimiento del lote ${index + 1} debe ser posterior a su recepción.`);
        }

        const productosNormalizados = productos.map((producto, productoIndex) => {
          const medicamentoId = Number(producto.medicamento_id);
          const cantidad = Number(producto.cantidad_recibida);
          if (!Number.isInteger(medicamentoId) || medicamentoId <= 0) {
            throw new Error(`Selecciona un medicamento válido en la línea ${productoIndex + 1} del lote ${index + 1}.`);
          }
          if (!Number.isInteger(cantidad) || cantidad <= 0) {
            throw new Error(`La cantidad en la línea ${productoIndex + 1} del lote ${index + 1} debe ser un entero mayor que cero.`);
          }
          return { medicamento_id: medicamentoId, cantidad_recibida: cantidad };
        });
        const idsMedicamentos = productosNormalizados.map((producto) => producto.medicamento_id);
        if (new Set(idsMedicamentos).size !== idsMedicamentos.length) {
          throw new Error(`No repitas medicamentos dentro del lote ${index + 1}.`);
        }

        return {
          codigo_lote: datos.codigo_lote.trim(),
          proveedor_id: proveedorId,
          sucursal_id: sucursalId,
          fecha_recepcion: datos.fecha_recepcion,
          fecha_vencimiento: datos.fecha_vencimiento,
          productos: productosNormalizados,
        };
      });

      await loteApi.registrarRecepcion(lotes, token);
      setFilas([crearFila(siguienteId)]);
      setSiguienteId((actual) => actual + 1);
      const totalProductos = lotes.reduce((total, lote) => total + lote.productos.length, 0);
      setMensaje(`${lotes.length} ${lotes.length === 1 ? "lote registrado" : "lotes registrados"} con ${totalProductos} ${totalProductos === 1 ? "medicamento" : "medicamentos"} en la recepción.`);
      onRegistrar();
    } catch (err) {
      setError(err.message);
    } finally {
      setGuardando(false);
    }
  }

  return (
    <section className="reception-panel" aria-labelledby="reception-title">
      <header className="reception-heading">
        <div>
          <p className="eyebrow">INGRESO DE INVENTARIO</p>
          <h2 id="reception-title">Recepción de medicamentos</h2>
          <p className="subtitle">Registra uno o varios lotes, cada uno con uno o más medicamentos.</p>
        </div>
        <span className="reception-count">{String(filas.length).padStart(2, "0")} {filas.length === 1 ? "LOTE" : "LOTES"}</span>
      </header>

      {error && <p className="error-msg" role="alert">{error}</p>}
      {mensaje && <p className="success-msg" role="status">{mensaje}</p>}

      <form className="reception-form" onSubmit={handleSubmit}>
        {filas.map((fila, index) => (
          <section className="reception-lot" key={fila.id} aria-labelledby={`lote-title-${fila.id}`}>
            <header className="reception-lot-heading">
              <div>
                <h3 id={`lote-title-${fila.id}`}>Lote {String(index + 1).padStart(2, "0")}</h3>
                <p>Datos del lote y medicamentos incluidos</p>
              </div>
              <button
                className="secondary-action remove-lot-button"
                type="button"
                onClick={() => quitarFila(fila.id)}
                disabled={filas.length === 1 || guardando}
                aria-label={`Quitar lote ${index + 1}`}
              >
                Quitar
              </button>
            </header>
            <div className="reception-lot-fields">
              {CAMPOS_RECEPCION.map((campo) => (
                <label key={campo.name}>
                  {campo.label}
                  {campo.type === "select" ? (
                    <select
                      required
                      value={fila.datos[campo.name] ?? ""}
                      disabled={cargandoOpciones || guardando}
                      onChange={(event) => cambiarDato(fila.id, campo.name, event.target.value)}
                    >
                      <option value="">Seleccionar</option>
                      {(opciones[campo.optionsKey] || []).map((opcion) => (
                        <option key={opcion.value} value={opcion.value}>{opcion.label}</option>
                      ))}
                    </select>
                  ) : (
                    <input
                      required
                      type={campo.type}
                      min={campo.name === "fecha_vencimiento" ? fila.datos.fecha_recepcion : undefined}
                      value={fila.datos[campo.name] ?? ""}
                      disabled={guardando}
                      onChange={(event) => cambiarDato(fila.id, campo.name, event.target.value)}
                    />
                  )}
                </label>
              ))}
            </div>
            <div className="reception-products">
              <h4>Medicamentos del lote</h4>
              {fila.productos.map((producto, productoIndex) => (
                <div className="reception-product-row" key={producto.id}>
                  <label>
                    Medicamento {productoIndex + 1}
                    <select
                      required
                      value={producto.medicamento_id}
                      disabled={cargandoOpciones || guardando}
                      onChange={(event) => cambiarProducto(fila.id, producto.id, "medicamento_id", event.target.value)}
                    >
                      <option value="">Seleccionar medicamento</option>
                      {(opciones.medicamentos || []).map((opcion) => (
                        <option key={opcion.value} value={opcion.value}>{opcion.label}</option>
                      ))}
                    </select>
                  </label>
                  <label>
                    Cantidad recibida
                    <input
                      required
                      type="number"
                      min="1"
                      step="1"
                      value={producto.cantidad_recibida}
                      disabled={guardando}
                      onChange={(event) => cambiarProducto(fila.id, producto.id, "cantidad_recibida", event.target.value)}
                    />
                  </label>
                  <button
                    className="secondary-action remove-lot-button"
                    type="button"
                    onClick={() => quitarProducto(fila.id, producto.id)}
                    disabled={fila.productos.length === 1 || guardando}
                    aria-label={`Quitar medicamento ${productoIndex + 1} del lote ${index + 1}`}
                  >
                    Quitar medicamento
                  </button>
                </div>
              ))}
              <button
                className="secondary-action add-product-button"
                type="button"
                onClick={() => agregarProducto(fila.id)}
                disabled={guardando || cargandoOpciones}
              >
                + Agregar medicamento al lote
              </button>
            </div>
          </section>
        ))}

        <div className="reception-actions">
          <button className="secondary-action" type="button" onClick={agregarFila} disabled={guardando}>
            + Agregar otro lote
          </button>
          <button type="submit" disabled={guardando || cargandoOpciones}>
            {guardando ? "Registrando..." : "Registrar recepción"}
          </button>
        </div>
      </form>
    </section>
  );
}

function CambiarEstado({ row, reload }) {
  const { token } = useAuth();
  const [nuevoEstado, setNuevoEstado] = useState(row.estado_lote);

  async function aplicar() {
    await loteApi.actualizarEstado(row.id, nuevoEstado, token);
    await reload();
  }

  return (
    <span className="inline-action">
      <select value={nuevoEstado} onChange={(e) => setNuevoEstado(e.target.value)}>
        {ESTADOS.map((e) => (
          <option key={e} value={e}>
            {e}
          </option>
        ))}
      </select>
      <button onClick={aplicar} disabled={nuevoEstado === row.estado_lote}>
        Cambiar
      </button>
    </span>
  );
}

const columns = [
  { key: "codigo_lote", label: "Código" },
  {
    key: "cantidad_recibida",
    label: "Recibida",
    render: (row) => Array.isArray(row.productos) && row.productos.length > 0
      ? row.productos.reduce((total, producto) => total + (producto.cantidad_recibida || 0), 0)
      : row.cantidad_recibida,
  },
  {
    key: "cantidad_disponible",
    label: "Disponible",
    render: (row) => Array.isArray(row.productos) && row.productos.length > 0
      ? row.productos.reduce((total, producto) => total + (producto.cantidad_disponible || 0), 0)
      : row.cantidad_disponible,
  },
  {
    key: "productos",
    label: "Medicamentos",
    render: (row) => Array.isArray(row.productos) && row.productos.length > 0
      ? row.productos.map((producto) => `${producto.medicamento} (${producto.cantidad_disponible ?? producto.cantidad_recibida})`).join(", ")
      : row.medicamento || "—",
  },
  { key: "fecha_vencimiento", label: "Vencimiento" },
  { key: "estado_lote", label: "Estado" },
];

export default function LotesPage() {
  const [refreshKey, setRefreshKey] = useState(0);

  return (
    <>
      <RecepcionMultiple onRegistrar={() => setRefreshKey((actual) => actual + 1)} />
      <CrudPage
        title="Lotes registrados"
        columns={columns}
        fetchAll={loteApi.listar}
        extraActions={(row, reload) => <CambiarEstado row={row} reload={reload} />}
        refreshKey={refreshKey}
      />
    </>
  );
}
