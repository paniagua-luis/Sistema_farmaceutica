import CrudPage from "../components/CrudPage";
import { proveedorApi } from "../api/client";

const fields = [
  { name: "codigo_proveedor", label: "Código", required: true },
  { name: "nombre", label: "Nombre", required: true },
  { name: "contacto", label: "Contacto" },
];

const columns = [
  { key: "codigo_proveedor", label: "Código" },
  { key: "nombre", label: "Nombre" },
  { key: "contacto", label: "Contacto" },
];

export default function ProveedoresPage() {
  return (
    <CrudPage
      title="Proveedores"
      fields={fields}
      columns={columns}
      fetchAll={proveedorApi.listar}
      onCreate={proveedorApi.crear}
      onDelete={proveedorApi.eliminar}
    />
  );
}
