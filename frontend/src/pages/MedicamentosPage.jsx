import CrudPage from "../components/CrudPage";
import { loteApi, medicamentoApi } from "../api/client";

const fields = [
  { name: "codigo_medicamento", label: "Código", required: true },
  { name: "nombre", label: "Nombre", required: true },
  { name: "principio_activo", label: "Principio activo", required: true },
  { name: "temperatura_minima", label: "Temp. mínima (°C)", type: "number", required: true },
  { name: "temperatura_maxima", label: "Temp. máxima (°C)", type: "number", required: true },
  { name: "dias_alerta_vencimiento", label: "Días de alerta de vencimiento", type: "number" },
];

const columns = [
  { key: "codigo_medicamento", label: "Código" },
  { key: "nombre", label: "Nombre" },
  { key: "principio_activo", label: "Principio activo" },
  { key: "temperatura_minima", label: "T. mín." },
  { key: "temperatura_maxima", label: "T. máx." },
  { key: "dias_alerta_vencimiento", label: "Alerta (días)" },
  {
    key: "fecha_vencimiento",
    label: "Próximo vencimiento",
    render: (medicamento) => medicamento.fecha_vencimiento || "Sin lote aprobado",
  },
];

async function listarMedicamentosConVencimiento(token) {
  const [medicamentos, lotes] = await Promise.all([
    medicamentoApi.listar(token),
    loteApi.listar(token),
  ]);
  const ahora = new Date();
  const hoy = [
    ahora.getFullYear(),
    String(ahora.getMonth() + 1).padStart(2, "0"),
    String(ahora.getDate()).padStart(2, "0"),
  ].join("-");
  const vencimientos = new Map();

  for (const lote of lotes) {
    if (lote.estado_lote !== "aprobado" || lote.fecha_vencimiento < hoy) {
      continue;
    }

    const productos = Array.isArray(lote.productos) && lote.productos.length > 0
      ? lote.productos
      : [{
          medicamento_id: lote.medicamento_id,
          cantidad_disponible: lote.cantidad_disponible,
        }];
    for (const producto of productos) {
      const cantidadDisponible = producto.cantidad_disponible
        ?? (producto.medicamento_id === lote.medicamento_id ? lote.cantidad_disponible : 0);
      if (cantidadDisponible <= 0) continue;

      const vencimientoActual = vencimientos.get(producto.medicamento_id);
      if (!vencimientoActual || lote.fecha_vencimiento < vencimientoActual) {
        vencimientos.set(producto.medicamento_id, lote.fecha_vencimiento);
      }
    }
  }

  return medicamentos.map((medicamento) => ({
    ...medicamento,
    fecha_vencimiento: vencimientos.get(medicamento.id) || null,
  }));
}

export default function MedicamentosPage() {
  return (
    <CrudPage
      title="Medicamentos"
      fields={fields}
      columns={columns}
      fetchAll={listarMedicamentosConVencimiento}
      onCreate={medicamentoApi.crear}
      onDelete={medicamentoApi.eliminar}
      initialValues={{ dias_alerta_vencimiento: 30 }}
    />
  );
}
