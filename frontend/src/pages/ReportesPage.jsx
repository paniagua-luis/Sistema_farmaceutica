import { useEffect, useState } from "react";
import CrudPage from "../components/CrudPage";
import { reporteApi, loteApi } from "../api/client";
import { useAuth } from "../context/useAuth";
import { tienePermiso } from "../utils/permisos";
import { sinZonaHoraria } from "../utils/fechaHora";

const fields = [
  { name: "tipo_reporte", label: "Tipo de reporte", required: true },
  { name: "destinatario", label: "Destinatario", required: true },
  { name: "contenido", label: "Contenido", type: "textarea", required: true },
  { name: "lote_id", label: "Lote (opcional)", type: "select", optionsKey: "lotes" },
];

let moduloJsPdfPromise;

function cargarJsPdf() {
  if (!moduloJsPdfPromise) {
    moduloJsPdfPromise = import("jspdf").catch((err) => {
      moduloJsPdfPromise = null;
      throw err;
    });
  }
  return moduloJsPdfPromise;
}

async function loadOptions(token) {
  const lotes = await loteApi.listar(token);
  return { lotes: lotes.map((l) => ({ value: l.id, label: l.codigo_lote })) };
}

function descargarReportePDF(reporte, JsPDF) {
  const pdf = new JsPDF();
  const margen = 20;
  const ancho = pdf.internal.pageSize.getWidth() - margen * 2;
  const limiteInferior = pdf.internal.pageSize.getHeight() - margen;
  let posicionY = 24;

  pdf.setFont("helvetica", "bold");
  pdf.setFontSize(18);
  pdf.text("Reporte farmacéutico", margen, posicionY);
  posicionY += 14;

  function agregarCampo(etiqueta, valor) {
    const lineas = pdf.splitTextToSize(String(valor ?? "No especificado"), ancho);
    if (posicionY + 14 > limiteInferior) {
      pdf.addPage();
      posicionY = margen;
    }

    pdf.setFont("helvetica", "bold");
    pdf.setFontSize(11);
    pdf.text(`${etiqueta}:`, margen, posicionY);
    posicionY += 6;
    pdf.setFont("helvetica", "normal");
    pdf.setFontSize(10);
    for (const linea of lineas) {
      if (posicionY + 5 > limiteInferior) {
        pdf.addPage();
        posicionY = margen;
      }
      pdf.text(linea, margen, posicionY);
      posicionY += 5;
    }
    posicionY += 8;
  }

  agregarCampo("Código", reporte.codigo_reporte);
  agregarCampo("Tipo", reporte.tipo_reporte);
  agregarCampo("Destinatario", reporte.destinatario);
  agregarCampo("Fecha", sinZonaHoraria(reporte.fecha));
  if (reporte.lote_id != null) agregarCampo("Lote", reporte.lote_id);
  agregarCampo("Contenido", reporte.contenido);

  const nombre = String(reporte.codigo_reporte || `reporte-${reporte.id || "nuevo"}`)
    .replace(/[^a-zA-Z0-9_-]/g, "_");
  pdf.save(`${nombre}.pdf`);
}

function DescargarReporte({ reporte }) {
  const [JsPDF, setJsPDF] = useState(null);
  const [error, setError] = useState(null);

  async function prepararJsPdf() {
    setError(null);
    try {
      const modulo = await cargarJsPdf();
      setJsPDF(() => modulo.jsPDF);
    } catch (err) {
      setError(`No se pudo preparar la descarga del PDF: ${err.message}`);
    }
  }

  useEffect(() => {
    let activa = true;
    cargarJsPdf()
      .then((modulo) => {
        if (activa) setJsPDF(() => modulo.jsPDF);
      })
      .catch((err) => {
        if (activa) setError(`No se pudo preparar la descarga del PDF: ${err.message}`);
      });
    return () => {
      activa = false;
    };
  }, []);

  function descargar() {
    setError(null);
    try {
      descargarReportePDF(reporte, JsPDF);
    } catch (err) {
      setError(`No se pudo descargar el PDF: ${err.message}`);
    }
  }

  return (
    <span className="inline-action">
      {JsPDF ? (
        <button type="button" onClick={descargar}>Descargar PDF</button>
      ) : (
        <button type="button" onClick={prepararJsPdf}>
          {error ? "Reintentar carga PDF" : "Preparando PDF..."}
        </button>
      )}
      {error && <span className="error-msg" role="alert">{error}</span>}
    </span>
  );
}

const columns = [
  { key: "codigo_reporte", label: "Código" },
  { key: "tipo_reporte", label: "Tipo" },
  { key: "destinatario", label: "Destinatario" },
  { key: "fecha", label: "Fecha" },
];

function resumenProductos(fila) {
  if (!Array.isArray(fila.productos) || fila.productos.length === 0) {
    return fila.medicamento || "—";
  }
  return fila.productos.map((producto) => {
    const nombre = producto.medicamento || `Medicamento ${producto.medicamento_id}`;
    const cantidad = producto.cantidad_disponible ?? producto.cantidad_recibida;
    return cantidad == null ? nombre : `${nombre} (${cantidad})`;
  }).join(", ");
}

function cantidadDisponible(fila) {
  if (Array.isArray(fila.productos) && fila.productos.length > 0) {
    return fila.productos.reduce((total, producto) => total + Number(producto.cantidad_disponible || 0), 0);
  }
  return fila.cantidad_disponible;
}

function ReportesInventario({ token, destinatario, puedeGuardar, onReporteGuardado }) {
  const [proveedores, setProveedores] = useState([]);
  const [medicamentos, setMedicamentos] = useState([]);
  const [alertas, setAlertas] = useState([]);
  const [tipo, setTipo] = useState("proveedor");
  const [proveedorId, setProveedorId] = useState("");
  const [medicamentoId, setMedicamentoId] = useState("");
  const [fechaDesde, setFechaDesde] = useState("");
  const [fechaHasta, setFechaHasta] = useState("");
  const [filas, setFilas] = useState([]);
  const [consultado, setConsultado] = useState(false);
  const [error, setError] = useState(null);
  const [mensaje, setMensaje] = useState(null);
  const [cargando, setCargando] = useState(true);
  const [consultando, setConsultando] = useState(false);

  useEffect(() => {
    let activa = true;
    Promise.all([
      reporteApi.consultarInventario(token),
      reporteApi.alertasVencimiento(token),
    ])
      .then(([inventario, alertasVencimiento]) => {
        if (!activa) return;
        const mapaProveedores = new Map(inventario.map((lote) => [lote.proveedor_id, lote.proveedor]));
        const mapaMedicamentos = new Map();
        for (const lote of inventario) {
          const productos = Array.isArray(lote.productos) && lote.productos.length > 0
            ? lote.productos
            : [{ medicamento_id: lote.medicamento_id, medicamento: lote.medicamento }];
          for (const producto of productos) {
            mapaMedicamentos.set(producto.medicamento_id, producto.medicamento || `Medicamento ${producto.medicamento_id}`);
          }
        }
        setProveedores([...mapaProveedores].map(([id, nombre]) => ({ id, nombre })));
        setMedicamentos([...mapaMedicamentos].map(([id, nombre]) => ({ id, nombre })));
        setAlertas(alertasVencimiento || []);
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

  async function generarReporte(event) {
    event.preventDefault();
    setError(null);
    setMensaje(null);
    setConsultando(true);
    const filtros = {};
    if (tipo === "proveedor") filtros.proveedor_id = proveedorId;
    if (tipo === "medicamento" || (tipo === "vencimientos" && medicamentoId)) {
      filtros.medicamento_id = medicamentoId;
    }
    if (tipo === "vencimientos") {
      filtros.fecha_desde = fechaDesde;
      filtros.fecha_hasta = fechaHasta;
    }
    if (tipo === "vencimientos" && fechaDesde && fechaHasta && fechaDesde > fechaHasta) {
      setError("La fecha inicial no puede ser posterior a la fecha final.");
      setConsultando(false);
      return;
    }
    try {
      const resultados = await reporteApi.consultarInventario(token, filtros);
      setFilas(resultados);
      setConsultado(true);
      if (puedeGuardar) {
        const descripcionTipo = {
          proveedor: "Inventario por proveedor",
          medicamento: "Inventario por medicamento",
          vencimientos: "Inventario por fecha de vencimiento",
        }[tipo];
        const descripcionFiltro = tipo === "proveedor"
          ? `Proveedor: ${proveedores.find((proveedor) => String(proveedor.id) === proveedorId)?.nombre || proveedorId}`
          : tipo === "medicamento"
            ? `Medicamento: ${medicamentos.find((medicamento) => String(medicamento.id) === medicamentoId)?.nombre || medicamentoId}`
            : `Fechas de vencimiento${medicamentoId
              ? ` · Medicamento: ${medicamentos.find((medicamento) => String(medicamento.id) === medicamentoId)?.nombre || medicamentoId}`
              : ""}`;
        const rango = tipo === "vencimientos"
          ? `\nVence desde: ${fechaDesde || "sin límite"}\nVence hasta: ${fechaHasta || "sin límite"}`
          : "";
        const detalleFilas = resultados.map((fila) =>
          `${fila.codigo_lote} | ${resumenProductos(fila)} | ${fila.proveedor} | ${fila.sucursal} | ${cantidadDisponible(fila)} | ${fila.fecha_vencimiento} | ${fila.estado_lote}`,
        );
        const contenido = [
          descripcionFiltro + rango,
          `Generado: ${new Date().toLocaleString()}`,
          `Lotes encontrados: ${resultados.length}`,
          "Lote | Medicamento | Proveedor | Sucursal | Disponible | Vencimiento | Estado",
          ...detalleFilas,
        ].join("\n");
        if (contenido.length > 2000) {
          throw new Error("El resultado supera el límite de 2000 caracteres del PDF. Reduce los filtros y vuelve a generarlo.");
        }
        await reporteApi.generar({
          tipo_reporte: descripcionTipo,
          destinatario: destinatario || "Sistema",
          contenido,
        }, token);
        onReporteGuardado();
        setMensaje("Reporte guardado en el historial; ya puedes descargarlo como PDF.");
      }
    } catch (err) {
      setError(err.message);
    } finally {
      setConsultando(false);
    }
  }

  return (
    <div className="inventory-reports">
      <section className="stock-alerts" aria-labelledby="expiry-alerts-title">
        <header className="stock-alerts-header">
          <div>
            <h2 id="expiry-alerts-title">Alertas de vencimiento</h2>
            <p className="subtitle">Lotes con existencias próximos a vencer o ya vencidos.</p>
          </div>
        </header>
        {cargando && <p role="status">Cargando alertas...</p>}
        {!cargando && error && <p className="error-msg" role="alert">{error}</p>}
        {!cargando && !error && alertas.length === 0 && <p>No hay lotes próximos a vencer ni vencidos.</p>}
        {!cargando && !error && alertas.length > 0 && (
          <div className="table-wrap">
            <table className="crud-table">
              <thead>
                <tr>
                  <th>Medicamento</th>
                  <th>Lote</th>
                  <th>Proveedor</th>
                  <th>Vencimiento</th>
                  <th>Existencias</th>
                  <th>Tiempo restante</th>
                </tr>
              </thead>
              <tbody>
                {alertas.map((alerta) => (
                  <tr key={`${alerta.lote_id}-${alerta.medicamento_id ?? "lote"}`}>
                    <td>{resumenProductos(alerta)}</td>
                    <td>{alerta.codigo_lote}</td>
                    <td>{alerta.proveedor}</td>
                    <td>{alerta.fecha_vencimiento}</td>
                    <td>{cantidadDisponible(alerta)}</td>
                    <td className="expiry-alert-value">
                      {alerta.estado_lote === "vencido" || alerta.dias_restantes < 0
                        ? `Vencido${Number.isFinite(alerta.dias_restantes) ? ` hace ${Math.abs(alerta.dias_restantes)} días` : ""}`
                        : alerta.dias_restantes === 0
                          ? "Vence hoy"
                          : Number.isFinite(alerta.dias_restantes)
                            ? `${alerta.dias_restantes} días`
                            : alerta.estado_lote || "Por vencer"}
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
      </section>

      <section className="inventory-report" aria-labelledby="inventory-report-title">
        <h2 id="inventory-report-title">Reporte de inventario</h2>
        <form className="crud-form" onSubmit={generarReporte}>
          <label>
            Tipo de reporte
            <select value={tipo} onChange={(event) => setTipo(event.target.value)}>
              <option value="proveedor">Por proveedor</option>
              <option value="medicamento">Por medicamento</option>
              <option value="vencimientos">Por fecha de vencimiento</option>
            </select>
          </label>
          {tipo === "proveedor" ? (
            <label>
              Proveedor
              <select value={proveedorId} onChange={(event) => setProveedorId(event.target.value)} required>
                <option value="">Seleccionar proveedor</option>
                {proveedores.map((proveedor) => (
                  <option key={proveedor.id} value={proveedor.id}>{proveedor.nombre}</option>
                ))}
              </select>
            </label>
          ) : tipo === "medicamento" ? (
            <label>
              Medicamento
              <select value={medicamentoId} onChange={(event) => setMedicamentoId(event.target.value)} required>
                <option value="">Seleccionar medicamento</option>
                {medicamentos.map((medicamento) => (
                  <option key={medicamento.id} value={medicamento.id}>{medicamento.nombre}</option>
                ))}
              </select>
            </label>
          ) : (
            <label>
              Medicamento (opcional)
              <select value={medicamentoId} onChange={(event) => setMedicamentoId(event.target.value)}>
                <option value="">Todos los medicamentos</option>
                {medicamentos.map((medicamento) => (
                  <option key={medicamento.id} value={medicamento.id}>{medicamento.nombre}</option>
                ))}
              </select>
            </label>
          )}
          {tipo === "vencimientos" && (
            <>
              <label>
                Vence desde
                <input type="date" value={fechaDesde} onChange={(event) => setFechaDesde(event.target.value)} />
              </label>
              <label>
                Vence hasta
                <input type="date" value={fechaHasta} onChange={(event) => setFechaHasta(event.target.value)} />
              </label>
            </>
          )}
          <button type="submit" disabled={consultando || cargando}>
            {consultando ? "Generando..." : puedeGuardar ? "Generar y guardar PDF" : "Generar reporte"}
          </button>
        </form>
        {error && !cargando && <p className="error-msg" role="alert">{error}</p>}
        {mensaje && <p className="success-msg" role="status">{mensaje}</p>}
        {filas.length > 0 && (
          <div className="table-wrap">
            <table className="crud-table">
              <thead>
                <tr>
                  <th>Lote</th>
                  <th>Medicamento</th>
                  <th>Proveedor</th>
                  <th>Sucursal</th>
                  <th>Disponible</th>
                  <th>Vencimiento</th>
                  <th>Estado</th>
                </tr>
              </thead>
              <tbody>
                {filas.map((fila) => (
                  <tr key={`${fila.lote_id}-${fila.medicamento_id ?? "lote"}`}>
                    <td>{fila.codigo_lote}</td>
                    <td>{resumenProductos(fila)}</td>
                    <td>{fila.proveedor}</td>
                    <td>{fila.sucursal}</td>
                    <td>{cantidadDisponible(fila)}</td>
                    <td>{fila.fecha_vencimiento}</td>
                    <td>{fila.estado_lote}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        )}
        {!consultando && filas.length === 0 && (
          <p>{consultado ? "No se encontraron lotes para este criterio." : "Selecciona un criterio para generar el reporte."}</p>
        )}
      </section>
    </div>
  );
}

export default function ReportesPage() {
  const { rol, token, username } = useAuth();
  const puedeGenerar = tienePermiso(rol, "reportes.generar");
  const [historialActualizado, setHistorialActualizado] = useState(0);

  return (
    <section className="crud-page">
      <h1>Reportes</h1>
      <ReportesInventario
        token={token}
        destinatario={username}
        puedeGuardar={puedeGenerar}
        onReporteGuardado={() => setHistorialActualizado((actual) => actual + 1)}
      />
      <CrudPage
        title="Historial de reportes guardados"
        fields={fields}
        columns={columns}
        fetchAll={reporteApi.listar}
        onCreate={puedeGenerar ? reporteApi.generar : undefined}
        loadOptions={puedeGenerar ? loadOptions : undefined}
        extraActions={(reporte) => <DescargarReporte reporte={reporte} />}
        submitLabel="Guardar reporte"
        refreshKey={historialActualizado}
      />
    </section>
  );
}
