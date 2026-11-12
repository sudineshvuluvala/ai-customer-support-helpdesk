import { useState, useEffect, useRef } from 'react'
import { userService } from '../../services/userService'
import { useAuth } from '../../context/AuthContext'
import ErrorMessage from '../../components/ErrorMessage'
import UserAvatar from '../../components/UserAvatar'

export default function ProfilePage() {
  const { user, setUser } = useAuth()
  const [name, setName] = useState('')
  const [currentPassword, setCurrentPassword] = useState('')
  const [newPassword, setNewPassword] = useState('')
  const [loading, setLoading] = useState(false)
  const [photoLoading, setPhotoLoading] = useState(false)
  const [err, setErr] = useState(null)
  const [success, setSuccess] = useState(false)
  const fileInputRef = useRef(null)

  useEffect(() => {
    if (user) setName(user.name.replace(' [SEED]', ''))
  }, [user])

  const handleUpdate = async (e) => {
    e.preventDefault()
    setErr(null)
    setSuccess(false)
    setLoading(true)
    try {
      const payload = { name }
      if (newPassword) {
        payload.current_password = currentPassword
        payload.new_password = newPassword
      }
      const updated = await userService.updateProfile(payload)
      setUser(updated)
      setSuccess(true)
      setCurrentPassword('')
      setNewPassword('')
    } catch (ex) {
      setErr(ex)
    } finally {
      setLoading(false)
    }
  }

  const handlePhotoUpload = async (e) => {
    const file = e.target.files?.[0]
    if (!file) return
    setErr(null)
    setPhotoLoading(true)
    try {
      const updated = await userService.uploadAvatar(file)
      setUser(updated)
      setSuccess(true)
    } catch (ex) {
      setErr(ex)
    } finally {
      setPhotoLoading(false)
      if (fileInputRef.current) fileInputRef.current.value = ''
    }
  }

  const handlePhotoDelete = async () => {
    setErr(null)
    setPhotoLoading(true)
    try {
      const updated = await userService.deleteAvatar()
      setUser(updated)
      setSuccess(true)
    } catch (ex) {
      setErr(ex)
    } finally {
      setPhotoLoading(false)
    }
  }

  return (
    <div className="row justify-content-center">
      <div className="col-lg-6">
        <div className="card shadow-sm border-0 mb-4">
          <div className="card-header bg-white p-4 pb-0 border-0">
            <h1 className="h4 fw-bold mb-1">User Account Profile</h1>
            <p className="text-muted small">Update your name, profile photo, and security password.</p>
          </div>
          <div className="card-body p-4 pt-2">
            {success && <div className="alert alert-success py-2 small">Profile updated successfully.</div>}
            <ErrorMessage error={err} />

            {/* Profile Photo Section */}
            <div className="d-flex align-items-center gap-3 p-3 bg-light rounded-3 mb-4">
              <UserAvatar user={user} size={64} className="shadow-sm" />
              <div>
                <div className="fw-semibold small mb-1">Profile Photo</div>
                <div className="d-flex gap-2 align-items-center flex-wrap">
                  <input
                    type="file"
                    ref={fileInputRef}
                    accept="image/png, image/jpeg, image/jpg"
                    style={{ display: 'none' }}
                    onChange={handlePhotoUpload}
                  />
                  <button
                    type="button"
                    disabled={photoLoading}
                    className="btn btn-sm btn-outline-primary"
                    onClick={() => fileInputRef.current?.click()}
                  >
                    <i className="bi bi-camera me-1" />
                    {photoLoading ? 'Uploading...' : 'Upload Photo'}
                  </button>
                  {user?.profile_photo && (
                    <button
                      type="button"
                      disabled={photoLoading}
                      className="btn btn-sm btn-outline-danger"
                      onClick={handlePhotoDelete}
                    >
                      <i className="bi bi-trash me-1" /> Remove
                    </button>
                  )}
                </div>
                <div className="text-muted" style={{ fontSize: '0.75rem', marginTop: '4px' }}>
                  Allowed formats: PNG, JPG, JPEG (Max 2MB)
                </div>
              </div>
            </div>

            <form onSubmit={handleUpdate}>
              <div className="mb-3">
                <label className="form-label small fw-medium">Email Address</label>
                <input type="email" disabled className="form-control bg-light" value={user?.email || ''} />
                <div className="form-text small">Email cannot be changed directly. Contact administrator.</div>
              </div>

              <div className="mb-3">
                <label className="form-label small fw-medium">Assigned Role</label>
                <input type="text" disabled className="form-control bg-light text-capitalize" value={user?.role || ''} />
              </div>

              <div className="mb-3">
                <label className="form-label small fw-medium">Display Name</label>
                <input
                  type="text"
                  required
                  className="form-control"
                  value={name}
                  onChange={(e) => setName(e.target.value)}
                />
              </div>

              <h2 className="h6 fw-bold mt-4 mb-3 border-top pt-3">Change Password</h2>
              <div className="mb-3">
                <label className="form-label small fw-medium">Current Password</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="Required if changing password"
                  value={currentPassword}
                  onChange={(e) => setCurrentPassword(e.target.value)}
                />
              </div>
              <div className="mb-4">
                <label className="form-label small fw-medium">New Password</label>
                <input
                  type="password"
                  className="form-control"
                  placeholder="At least 8 characters with letters & numbers"
                  value={newPassword}
                  onChange={(e) => setNewPassword(e.target.value)}
                />
              </div>

              <div className="d-flex justify-content-end">
                <button type="submit" disabled={loading} className="btn btn-primary px-4">
                  {loading ? 'Saving...' : 'Save Profile'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
