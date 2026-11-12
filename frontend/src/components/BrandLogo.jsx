export default function BrandLogo({ size = 36, className = '' }) {
  return (
    <div
      className={`d-inline-flex align-items-center justify-content-center flex-shrink-0 ${className}`}
      style={{
        width: `${size}px`,
        height: `${size}px`,
        borderRadius: `${Math.round(size * 0.28)}px`,
        background: 'linear-gradient(135deg, #2563eb 0%, #0284c7 100%)',
        boxShadow: '0 2px 8px rgba(37, 99, 235, 0.3)',
        color: '#ffffff',
        position: 'relative',
        overflow: 'hidden',
      }}
    >
      <svg
        viewBox="0 0 32 32"
        fill="none"
        xmlns="http://www.w3.org/2000/svg"
        style={{ width: `${Math.round(size * 0.65)}px`, height: `${Math.round(size * 0.65)}px` }}
      >
        <path d="M7 16C7 11.0294 11.0294 7 16 7C20.9706 7 25 11.0294 25 16" stroke="white" strokeWidth="2.2" strokeLinecap="round" />
        <rect x="5.5" y="15" width="3" height="7" rx="1.5" fill="white" />
        <rect x="23.5" y="15" width="3" height="7" rx="1.5" fill="white" />
        <path d="M24 21C24 23.5 21.5 25 18 25H16" stroke="white" strokeWidth="2" strokeLinecap="round" />
        <circle cx="15.5" cy="25" r="1.5" fill="#38bdf8" />
        <path d="M16 10L16.6 11.8L18.5 12.5L16.6 13.2L16 15L15.4 13.2L13.5 12.5L15.4 11.8Z" fill="white" />
      </svg>
    </div>
  )
}
