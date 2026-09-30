const API_URL = import.meta.env.VITE_API_URL || "http://127.0.0.1:8000";

export async function request(path, { method = "GET", token, body } = {}) {
  const headers = { "Content-Type": "application/json" };

  if (token) {
    headers["Authorization"] = `Bearer ${token}`;
  }

  const response = await fetch(`${API_URL}${path}`, {
    method,
    headers,
    body: body !== undefined ? JSON.stringify(body) : undefined,
  });

  if (!response.ok) {
    let detail = "Error en la petición";
    try {
      const errorbody = await response.json();
      detail = errorbody.detail || detail;
    } catch {
      // la respuesta no era JSON
    }
    throw new Error(typeof detail === "string" ? detail : JSON.stringify(detail));
  }

  // Algunas respuestas (ej. DELETE) pueden venir sin body
  const texto = await response.text();
  return texto ? JSON.parse(texto) : null;
}

export const authApi = {
  registrar: (username, password) =>
    request("/auth/registro", { method: "POST", body: { username, password } }),

  login: async (username, password) => {
    const form = new URLSearchParams();
    form.append("grant_type", "password");
    form.append("username", username);
    form.append("password", password);

    const response = await fetch(`${API_URL}/auth/login`, {
      method: "POST",
      headers: { "Content-Type": "application/x-www-form-urlencoded" },
      body: form,
    });

    if (!response.ok) {
      const errorbody = await response.json();
      throw new Error(errorbody.detail || "Credenciales inválidas");
    }

    return response.json();
  },
};

export const usuarioApi = {
  listar: (token) => request("/usuarios/", { token }),
  actualizarRol: (id, rol, token) =>
    request(`/usuarios/${id}/rol`, { method: "PATCH", body: { rol }, token }),
};

// --- 7.0 Mantener Datos Técnicos de Medicamentos ---
export const medicamentoApi = {
  listar: (token) => request("/medicamentos/", { token }),
  obtener: (id, token) => request(`/medicamentos/${id}`, { token }),
  crear: (datos, token) => request("/medicamentos/", { method: "POST", body: datos, token }),
  actualizar: (id, datos, token) => request(`/medicamentos/${id}`, { method: "PUT", body: datos, token }),
  eliminar: (id, token) => request(`/medicamentos/${id}`, { method: "DELETE", token }),
};

// Catálogos base
export const proveedorApi = {
  listar: (token) => request("/proveedores/", { token }),
  obtener: (id, token) => request(`/proveedores/${id}`, { token }),
  crear: (datos, token) => request("/proveedores/", { method: "POST", body: datos, token }),
  eliminar: (id, token) => request(`/proveedores/${id}`, { method: "DELETE", token }),
};

export const sucursalApi = {
  listar: (token) => request("/sucursales/", { token }),
  obtener: (id, token) => request(`/sucursales/${id}`, { token }),
  crear: (datos, token) => request("/sucursales/", { method: "POST", body: datos, token }),
  eliminar: (id, token) => request(`/sucursales/${id}`, { method: "DELETE", token }),
};

// --- 1.0 / 5.0 Recepción de Mercancía y Vencimientos/Bajas ---
export const loteApi = {
  listar: (token) => request("/lotes/", { token }),
  obtener: (id, token) => request(`/lotes/${id}`, { token }),
  alertasStockBajo: (token, umbral) => {
    const query = umbral === undefined ? "" : `?umbral=${encodeURIComponent(umbral)}`;
    return request(`/lotes/alertas/bajo-stock${query}`, { token });
  },
  registrarRecepcion: (lotes, token) =>
    request("/lotes/recepciones", { method: "POST", body: { lotes }, token }),
  actualizarEstado: (id, nuevoEstado, token) =>
    request(`/lotes/${id}/estado`, { method: "PATCH", body: { nuevo_estado: nuevoEstado }, token }),
};

// --- 2.0 Verificación de Calidad ---
export const inspeccionApi = {
  listar: (token) => request("/inspecciones/", { token }),
  historialLote: (loteId, token) => request(`/inspecciones/lote/${loteId}`, { token }),
  registrar: (datos, token) => request("/inspecciones/", { method: "POST", body: datos, token }),
};

// --- 3.0 Distribución y Despacho ---
export const despachoApi = {
  listar: (token) => request("/despachos/", { token }),
  registrar: (datos, token) => request("/despachos/", { method: "POST", body: datos, token }),
  registrarMultiple: (datos, token) =>
    request("/despachos/multiple", { method: "POST", body: datos, token }),
  confirmarRecepcion: (id, token) => request(`/despachos/${id}/confirmar`, { method: "PATCH", token }),
};

// --- 4.0 Monitoreo de Cadena de Frío ---
export const monitoreoApi = {
  listar: (token) => request("/monitoreo-temperatura/", { token }),
  registrarLectura: (datos, token) => request("/monitoreo-temperatura/", { method: "POST", body: datos, token }),
};

// --- 6.0 Trazabilidad y Reportes ---
export const trazabilidadApi = {
  listar: (token) => request("/trazabilidad/", { token }),
  historialLote: (loteId, token) => request(`/trazabilidad/lote/${loteId}`, { token }),
};

export const reporteApi = {
  listar: (token) => request("/reportes/", { token }),
  consultarInventario: (token, filtros = {}) => {
    const params = new URLSearchParams();
    Object.entries(filtros).forEach(([nombre, valor]) => {
      if (valor !== undefined && valor !== null && valor !== "") params.set(nombre, valor);
    });
    const query = params.toString();
    return request(`/reportes/inventario${query ? `?${query}` : ""}`, { token });
  },
  alertasVencimiento: (token) => request("/reportes/alertas/vencimiento", { token }),
  generar: (datos, token) => request("/reportes/", { method: "POST", body: datos, token }),
};
