import { initials } from '../utils/format'
import { userService } from '../services/userService'

export default function UserAvatar({ user, size = 32, className = '' }) {
  if (!user) return null

  const photo = user.profile_photo
  const url = photo ? userService.avatarUrl(photo) : null

  if (url) {
    return (
      <img
        src={url}
        alt={user.name || 'User'}
        className={`rounded-circle object-fit-cover ${className}`}
        style={{ width: `${size}px`, height: `${size}px`, border: '1px solid rgba(0,0,0,0.1)' }}
        onError={(e) => {
          // If image fails to load, gracefully fallback to letter avatar
          e.target.style.display = 'none'
          if (e.target.nextSibling) e.target.nextSibling.style.display = 'flex'
        }}
      />
    )
  }

  return (
    <span
      className={`avatar role-${user.role || 'customer'} ${className}`}
      style={{ width: `${size}px`, height: `${size}px`, fontSize: `${Math.round(size * 0.42)}px` }}
      title={user.name}
    >
      {initials(user.name)}
    </span>
  )
}
