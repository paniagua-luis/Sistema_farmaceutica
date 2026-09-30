import CrudPage from "../components/CrudPage";
import { inspeccionApi, loteApi } from "../api/client";

const fields = [
  { name: "lote_id", label: "Lote", type: "select", optionsKey: "lotes", required: true },
  { name: "resultado", label: "Resultado", type: "select", optionsKey: "resultados", required: true },
  { name: "observaciones", label: "Observaciones", type: "textarea" },
];

async function loadOptions(token) {
  const lotes = await loteApi.listar(token);
  return {
    lotes: lotes.map((l) => ({ value: l.id, label: `${l.codigo_lote} (estado: ${l.estado_lote})` })),
    resultados: [
      { value: "aprobado", label: "Aprobado" },
      { value: "rechazado", label: "Rechazado" },
    ],
  };
}

const columns = [
  { key: "lote_id", label: "Lote ID" },
  { key: "resultado", label: "Resultado" },
  { key: "observaciones", label: "Observaciones" },
  { key: "fecha_inspeccion", label: "Fecha" },
];

export default function InspeccionesPage() {
  return (
    <CrudPage
      title="Inspecciones de Calidad"
      fields={fields}
      columns={columns}
      fetchAll={inspeccionApi.listar}
      onCreate={inspeccionApi.registrar}
      loadOptions={loadOptions}
      submitLabel="Registrar inspección"
    />
  );
}
