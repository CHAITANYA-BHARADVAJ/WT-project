import { useState, useCallback } from 'react'
import axios from 'axios'
import FileUpload from './components/FileUpload'
import Dashboard from './components/Dashboard'

const API_URL = "https://wt-project-2wde.onrender.com"

function App() {
  const [data, setData] = useState(null)
  const [loading, setLoading] = useState(false)
  const [error, setError] = useState(null)

  const handleUpload = useCallback(async (file) => {
    setLoading(true)
    setError(null)
    setData(null)

    const formData = new FormData()
    formData.append('file', file)

    try {
      const response = await axios.post(
        `${API_URL}/upload`,
        formData,
        {
          headers: { 'Content-Type': 'multipart/form-data' },
          timeout: 60000,
        }
      )

      setData(response.data)

    } catch (err) {
      if (err.response) {
        setError(err.response.data.detail || 'Server error occurred.')
      } else if (err.request) {
        setError('Server is waking up (Render free tier). Try again in a few seconds.')
      } else {
        setError('An unexpected error occurred.')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  const handleExport = useCallback(() => {
    window.print()
  }, [])

  const handleReset = useCallback(() => {
    setData(null)
    setError(null)
  }, [])

  return (
    <>
      <div className="app-bg" />

      <header className="app-header no-print">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-icon">RA</div>
            <span className="logo-text">ResultAnalyzer</span>
          </div>
          <span className="header-badge">
            <span className="pulse-dot" />
            Stateless · Privacy First
          </span>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner animate-fade-in no-print">
            <span className="icon">⚠</span>
            <span>{error}</span>
            <button
              className="btn btn-danger"
              style={{ marginLeft: 'auto', padding: '0.3rem 0.75rem', fontSize: '0.78rem' }}
              onClick={() => setError(null)}
            >
              Dismiss
            </button>
          </div>
        )}

        {loading ? (
          <div className="loading-overlay animate-fade-in">
            <div className="spinner" />
            <p className="loading-text">Analyzing your results...</p>
            <p style={{ color: 'var(--text-muted)', fontSize: '0.8rem' }}>
              Processing file and extracting data
            </p>
          </div>
        ) : data ? (
          <Dashboard
            data={data}
            onExport={handleExport}
            onReset={handleReset}
          />
        ) : (
          <FileUpload onUpload={handleUpload} />
        )}
      </main>

      <footer className="app-footer no-print">
        <p>
          Built with FastAPI + React · All processing in memory · No data stored
        </p>
      </footer>
    </>
  )
}

export default App