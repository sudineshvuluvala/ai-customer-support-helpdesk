import { useState, useEffect } from 'react'
import { analyticsService } from '../../services/miscServices'
import { useFetch } from '../../hooks/useFetch'
import Loading from '../../components/Loading'
import ErrorMessage from '../../components/ErrorMessage'

export default function SettingsPage() {
  const { data, loading, error, reload } = useFetch(analyticsService.settings)

  const [settings, setSettings] = useState({})
  const [saving, setSaving] = useState(false)
  const [success, setSuccess] = useState(false)
  const [saveErr, setSaveErr] = useState(null)

  useEffect(() => {
    if (data) setSettings(data)
  }, [data])

  const handleSave = async (e) => {
    e.preventDefault()
    setSaving(true)
    setSaveErr(null)
    setSuccess(false)
    try {
      await analyticsService.saveSettings(settings)
      setSuccess(true)
      reload()
    } catch (ex) {
      setSaveErr(ex)
    } finally {
      setSaving(false)
    }
  }

  if (loading) return <Loading text="Loading platform configuration..." />
  if (error) return <ErrorMessage error={error} onRetry={reload} />

  return (
    <div className="row justify-content-center">
      <div className="col-lg-8">
        <div className="card shadow-sm border-0">
          <div className="card-header bg-white p-4 pb-0 border-0">
            <h1 className="h4 fw-bold mb-1">Application &amp; SLA Settings</h1>
            <p className="text-muted small">Configure priority target thresholds, response windows, and ticket life-cycle rules.</p>
          </div>
          <div className="card-body p-4 pt-2">
            {success && <div className="alert alert-success py-2 small">Settings successfully updated and applied.</div>}
            <ErrorMessage error={saveErr} />

            <form onSubmit={handleSave}>
              <h2 className="h6 fw-bold mb-3 border-bottom pb-2">Service Level Agreement Target Windows (Hours)</h2>

              {['critical', 'high', 'medium', 'low'].map((p) => (
                <div key={p} className="row g-3 mb-3 align-items-center">
                  <div className="col-md-4">
                    <span className="fw-semibold text-capitalize">{p} Priority</span>
                  </div>
                  <div className="col-md-4">
                    <label className="form-label small text-muted">First Response (hrs)</label>
                    <input
                      type="number"
                      required
                      min={0.5}
                      step={0.5}
                      className="form-control form-control-sm"
                      value={settings[`sla_response_hours_${p}`] || ''}
                      onChange={(e) => setSettings({ ...settings, [`sla_response_hours_${p}`]: e.target.value })}
                    />
                  </div>
                  <div className="col-md-4">
                    <label className="form-label small text-muted">Resolution (hrs)</label>
                    <input
                      type="number"
                      required
                      min={1}
                      step={0.5}
                      className="form-control form-control-sm"
                      value={settings[`sla_resolution_hours_${p}`] || ''}
                      onChange={(e) => setSettings({ ...settings, [`sla_resolution_hours_${p}`]: e.target.value })}
                    />
                  </div>
                </div>
              ))}

              <h2 className="h6 fw-bold mt-4 mb-3 border-bottom pb-2">Lifecycle Policies</h2>
              <div className="row g-3 mb-4">
                <div className="col-md-6">
                  <label className="form-label small fw-medium">Auto-Close Days After Resolution</label>
                  <input
                    type="number"
                    min={1}
                    className="form-control form-control-sm"
                    value={settings.auto_close_days || ''}
                    onChange={(e) => setSettings({ ...settings, auto_close_days: e.target.value })}
                  />
                  <div className="form-text small">Days before a resolved ticket automatically marks as Closed.</div>
                </div>
              </div>

              <div className="d-flex justify-content-end">
                <button type="submit" disabled={saving} className="btn btn-primary px-4">
                  {saving ? 'Saving...' : 'Save Configuration'}
                </button>
              </div>
            </form>
          </div>
        </div>
      </div>
    </div>
  )
}
