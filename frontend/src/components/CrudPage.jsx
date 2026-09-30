import { useEffect, useState, useCallback } from "react";
import { useAuth } from "../context/useAuth";
import { sinZonaHoraria } from "../utils/fechaHora";

 /**
 * @param {string} title
 * @param {Array}  fields        [{ name, label, type: "text"|"number"|"date"|"select"|"textarea", optionsKey?, required? }]
 * @param {Function} fetchAll    (token) => Promise<Array>
 * @param {Function} [onCreate]  (datos, token) => Promise<any>
 * @param {Function} [onDelete]  (id, token) => Promise<any>
 * @param {Function} [loadOptions] (token) => Promise<{ [optionsKey]: {value,label}[] }>
 * @param {Array}   columns      [{ key, label, render?: (row) => node }]
 * @param {Function} [extraActions] (row, reload) => node
 * @param {Object}  [initialValues]
 * @param {string}  [submitLabel]
 */
export default function CrudPage({
  title,
  fields,
  fetchAll,
  onCreate,
  onDelete,
  loadOptions,
  columns,
  extraActions,
  initialValues = {},
  submitLabel = "Guardar",
  refreshKey = 0,
}) {
  const { token } = useAuth();
  const [rows, setRows] = useState([]);
  const [options, setOptions] = useState({});
  const [form, setForm] = useState(initialValues);
  const [error, setError] = useState(null);
  const [cargando, setCargando] = useState(false);

  const reload = useCallback(async () => {
    try {
      const data = await fetchAll(token);
      setError(null);
      setRows(data || []);
        if (loadOptions) {
          setOptions(await loadOptions(token));
        }
    } catch (err) {
      setError(err.message);
    }
  }, [fetchAll, loadOptions, token]);

  useEffect(() => {
    fetchAll(token)
      .then((data) => {
        setError(null);
        setRows(data || []);
      })
      .catch((err) => setError(err.message));
      if (loadOptions) {
        loadOptions(token)
          .then(setOptions)
          .catch((err) => setError(err.message));
      }
  }, [fetchAll, loadOptions, token, refreshKey]);

  function handleChange(name, value) {
    setForm((prev) => ({ ...prev, [name]: value }));
  }

  async function handleSubmit(e) {
    e.preventDefault();
    if (!onCreate) return;
    setError(null);
    setCargando(true);
    try {
      const datos = {};
      for (const f of fields) {
        let val = form[f.name];
        if (val === undefined || val === "") {
          if (f.required) throw new Error(`El campo "${f.label}" es obligatorio`);
          continue;
        }
        if (f.type === "number") val = Number(val);
        datos[f.name] = val;
      }
      await onCreate(datos, token);
      setForm(initialValues);
      await reload();
    } catch (err) {
      setError(err.message);
    } finally {
      setCargando(false);
    }
  }

  async function handleDelete(id) {
    if (!onDelete) return;
    if (!window.confirm("¿Eliminar este registro?")) return;
    setError(null);
    try {
      await onDelete(id, token);
      await reload();
    } catch (err) {
      setError(err.message);
    }
  }

  return (
    <section className="crud-page">
      <h1>{title}</h1>
      {error && <p className="error-msg">{error}</p>}

      {onCreate && (
        <form className="crud-form" onSubmit={handleSubmit}>
          {fields.map((f) => (
            <label key={f.name}>
              {f.label}
              {f.type === "select" ? (
                <select
                  value={form[f.name] ?? ""}
                  onChange={(e) => handleChange(f.name, e.target.value)}
                  required={f.required}
                >
                  <option value="">-- Seleccionar --</option>
                  {(options[f.optionsKey] || []).map((opt) => (
                    <option key={opt.value} value={opt.value}>
                      {opt.label}
                    </option>
                  ))}
                </select>
              ) : f.type === "textarea" ? (
                <textarea
                  value={form[f.name] ?? ""}
                  onChange={(e) => handleChange(f.name, e.target.value)}
                  required={f.required}
                />
              ) : (
                <input
                  type={f.type || "text"}
                  value={form[f.name] ?? ""}
                  onChange={(e) => handleChange(f.name, e.target.value)}
                  required={f.required}
                  step={f.type === "number" ? "any" : undefined}
                />
              )}
            </label>
          ))}
          <button type="submit" disabled={cargando}>
            {cargando ? "Guardando..." : submitLabel}
          </button>
        </form>
      )}

      <div className="table-wrap">
        <table className="crud-table">
          <thead>
            <tr>
              {columns.map((c) => (
                <th key={c.key}>{c.label}</th>
              ))}
              {(onDelete || extraActions) && <th>Acciones</th>}
            </tr>
          </thead>
          <tbody>
            {rows.map((row) => (
              <tr key={row.id}>
                {columns.map((c) => (
                    <td key={c.key}>{c.render ? c.render(row, options) : sinZonaHoraria(row[c.key])}</td>
                ))}
                {(onDelete || extraActions) && (
                  <td className="row-actions">
                    {extraActions && extraActions(row, reload)}
                    {onDelete && <button className="danger-action" onClick={() => handleDelete(row.id)}>Eliminar</button>}
                  </td>
                )}
              </tr>
            ))}
            {rows.length === 0 && (
              <tr>
                <td colSpan={columns.length + 1}>Sin registros.</td>
              </tr>
            )}
          </tbody>
        </table>
      </div>
    </section>
  );
}
