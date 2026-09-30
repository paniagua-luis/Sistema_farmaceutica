import CrudPage from "../components/CrudPage";
import { sucursalApi } from "../api/client";

const fields = [
  { name: "codigo_sucursal", label: "Código", required: true },
  { name: "nombre", label: "Nombre", required: true },
];

const columns = [
  { key: "codigo_sucursal", label: "Código" },
  { key: "nombre", label: "Nombre" },
];

export default function SucursalesPage() {
  return (
    <CrudPage
      title="Sucursales"
      fields={fields}
      columns={columns}
      fetchAll={sucursalApi.listar}
      onCreate={sucursalApi.crear}
      onDelete={sucursalApi.eliminar}
    />
  );
}
