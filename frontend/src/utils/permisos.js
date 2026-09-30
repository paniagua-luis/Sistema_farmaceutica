
export const ROLE_PERMISSIONS = {
  administrador: [
    "medicamentos.gestionar",
    "proveedores.gestionar",
    "sucursales.gestionar",
    "lotes.gestionar",
    "calidad.gestionar",
    "despachos.gestionar",
    "temperatura.gestionar",
    "trazabilidad.consultar",
    "reportes.consultar",
    "reportes.generar",
    "usuarios.gestionar",
  ],
  almacen: ["lotes.gestionar", "temperatura.gestionar", "trazabilidad.consultar", "reportes.consultar", "reportes.generar"],
  personal_calidad: ["calidad.gestionar", "temperatura.gestionar", "trazabilidad.consultar", "reportes.consultar", "reportes.generar"],
  personal_sucursal: ["despachos.gestionar"],
  proveedor: ["lotes.gestionar"],
  ente_regulador: ["trazabilidad.consultar", "reportes.consultar"],
};

export const ROLES_DISPONIBLES = Object.keys(ROLE_PERMISSIONS);

export function tienePermiso(rol, permiso) {
  const rolNormalizado = typeof rol === "string" ? rol.trim().toLowerCase().replace(/[ -]+/g, "_") : rol;
  return ROLE_PERMISSIONS[rolNormalizado]?.includes(permiso) ?? false;
}
