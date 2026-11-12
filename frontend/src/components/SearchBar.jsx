export default function SearchBar({ value, onChange, placeholder = 'Search...', label = 'Search' }) {
  return (
    <div className="input-group search-bar">
      <span className="input-group-text bg-white"><i className="bi bi-search" aria-hidden="true" /></span>
      <input type="search" className="form-control" aria-label={label} placeholder={placeholder}
        value={value} onChange={(e) => onChange(e.target.value)} />
    </div>
  )
}
