const ISO_FECHA_HORA = /^(\d{4}-\d{2}-\d{2})[T ](\d{2}:\d{2}(?::\d{2}(?:\.\d+)?)?)(?:Z|[+-]\d{2}:?\d{2})?$/i;

export function sinZonaHoraria(valor) {
  if (typeof valor !== "string") return valor;
  const coincidencia = valor.match(ISO_FECHA_HORA);
  return coincidencia ? `${coincidencia[1]} ${coincidencia[2]}` : valor;
}
