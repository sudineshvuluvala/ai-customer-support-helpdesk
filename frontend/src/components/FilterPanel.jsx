// fields: [{ name, label, options: [{value,label}] }]
export default function FilterPanel({ fields, values, onChange, onReset }) {
  return (
    <div className="filter-panel">
      {fields.map((f) => (
        <div key={f.name} className="filter-item">
          <label className="form-label small text-muted mb-1" htmlFor={`f-${f.name}`}>{f.label}</label>
          <select id={`f-${f.name}`} className="form-select form-select-sm" value={values[f.name] ?? ''}
            onChange={(e) => onChange(f.name, e.target.value)}>
            <option value="">All</option>
            {f.options.map((o) => <option key={o.value} value={o.value}>{o.label}</option>)}
          </select>
        </div>
      ))}
      {onReset && <button type="button" className="btn btn-sm btn-outline-secondary align-self-end" onClick={onReset}>Reset</button>}
    </div>
  )
}
