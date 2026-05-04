import { useState, useCallback } from 'react'
import axios from 'axios'
import FileUpload from './components/FileUpload'
import Dashboard from './components/Dashboard'

const API_URL = import.meta.env.VITE_API_URL || (import.meta.env.DEV ? 'http://localhost:8000' : '')

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
      const response = await axios.post(`${API_URL}/api/upload`, formData, {
        headers: { 'Content-Type': 'multipart/form-data' },
        timeout: 60000,
      })

      if (response.data.success) {
        setData(response.data.data)
      } else {
        setError(response.data.message || 'Failed to parse the result file.')
      }
    } catch (err) {
      if (err.response) {
        setError(err.response.data.detail || 'Server error occurred.')
      } else if (err.request) {
        setError('Cannot connect to the server. Make sure the backend is running on port 8000.')
      } else {
        setError('An unexpected error occurred.')
      }
    } finally {
      setLoading(false)
    }
  }, [])

  const handleExport = useCallback(async () => {
    try {
      const response = await axios.post(`${API_URL}/api/export`, null, {
        responseType: 'blob',
        timeout: 30000,
      })

      const url = window.URL.createObjectURL(new Blob([response.data]))
      const link = document.createElement('a')
      link.href = url
      link.setAttribute('download', 'result_analysis_report.pdf')
      document.body.appendChild(link)
      link.click()
      link.remove()
      window.URL.revokeObjectURL(url)
    } catch {
      setError('Failed to generate report PDF.')
    }
  }, [])

  const handleReset = useCallback(() => {
    setData(null)
    setError(null)
  }, [])

  return (
    <>
      <div className="app-bg" />

      <header className="app-header">
        <div className="header-inner">
          <div className="logo">
            <div className="logo-icon">RA</div>
            <span className="logo-text">ResultAnalyzer</span>
          </div>
          <span className="header-badge">
            <span className="pulse-dot" />
            Stateless - Privacy First
          </span>
        </div>
      </header>

      <main className="app-main">
        {error && (
          <div className="error-banner animate-fade-in">
            <span className="icon">!</span>
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
              Extracting data, computing statistics, and preparing charts
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

      <footer className="app-footer">
        <p>
          Built with FastAPI + React - all processing in memory - no data stored
        </p>
      </footer>
    </>
  )
}

export default App
