import CrudPage from "../components/CrudPage";
import { monitoreoApi, loteApi } from "../api/client";

const fields = [
  { name: "codigo_lectura", label: "Código de lectura", required: true },
  { name: "ubicacion_almacen", label: "Ubicación en almacén", required: true },
  { name: "temperatura_registrada", label: "Temperatura (°C)", type: "number", required: true },
  { name: "lote_id", label: "Lote (opcional)", type: "select", optionsKey: "lotes" },
];

async function loadOptions(token) {
  const lotes = await loteApi.listar(token);
  return { lotes: lotes.map((l) => ({ value: l.id, label: l.codigo_lote })) };
}

const columns = [
  { key: "codigo_lectura", label: "Código" },
  { key: "ubicacion_almacen", label: "Ubicación" },
  { key: "temperatura_registrada", label: "Temp. (°C)" },
  { key: "estado_lectura", label: "Estado" },
  { key: "fecha_hora", label: "Fecha/Hora" },
];

export default function MonitoreoPage() {
  return (
    <CrudPage
      title="Monitoreo de Cadena de Frío"
      fields={fields}
      columns={columns}
      fetchAll={monitoreoApi.listar}
      onCreate={monitoreoApi.registrarLectura}
      loadOptions={loadOptions}
      submitLabel="Registrar lectura"
    />
  );
}
