// Decodifica el payload de un JWT sin verificar la firma.
// Solo se usa para leer claims (username, rol) y mejorar la UI;
// la verificación real de seguridad siempre ocurre en el backend.
export function decodeJwt(token) {
  try {
    const payload = token.split(".")[1];
    const json = atob(payload.replace(/-/g, "+").replace(/_/g, "/"));
    return JSON.parse(json);
  } catch {
    return null;
  }
}
