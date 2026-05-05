import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

const ACCEPTED_FILES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel.sheet.macroEnabled.12': ['.xlsm'],
  'text/csv': ['.csv'],
}

// Icons
const ChartIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M3 3v18h18"/><path d="M18 17V9"/><path d="M13 17V5"/><path d="M8 17v-3"/></svg>
)
const ShieldIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M12 22s8-4 8-10V5l-8-3-8 3v7c0 6 8 10 8 10z"/></svg>
)
const ZapIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><polygon points="13 2 3 14 12 14 11 22 21 10 12 10 13 2"/></svg>
)
const PdfIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="24" height="24" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="2" strokeLinecap="round" strokeLinejoin="round"><path d="M14 2H6a2 2 0 0 0-2 2v16a2 2 0 0 0 2 2h12a2 2 0 0 0 2-2V8z"/><polyline points="14 2 14 8 20 8"/><line x1="16" y1="13" x2="8" y2="13"/><line x1="16" y1="17" x2="8" y2="17"/><polyline points="10 9 9 9 8 9"/></svg>
)
const UploadIcon = () => (
  <svg xmlns="http://www.w3.org/2000/svg" width="48" height="48" viewBox="0 0 24 24" fill="none" stroke="currentColor" strokeWidth="1.5" strokeLinecap="round" strokeLinejoin="round"><path d="M21 15v4a2 2 0 0 1-2 2H5a2 2 0 0 1-2-2v-4"/><polyline points="17 8 12 3 7 8"/><line x1="12" y1="3" x2="12" y2="15"/></svg>
)

export default function FileUpload({ onUpload }) {
  const onDrop = useCallback((acceptedFiles) => {
    if (acceptedFiles.length > 0) {
      onUpload(acceptedFiles[0])
    }
  }, [onUpload])

  const { getRootProps, getInputProps, isDragActive } = useDropzone({
    onDrop,
    accept: ACCEPTED_FILES,
    maxFiles: 1,
    maxSize: 50 * 1024 * 1024,
  })

  return (
    <section className="upload-section" id="upload-section">
      <div className="upload-hero animate-fade-in-up">
        <h1 className="hero-title">Intelligent Result Analysis</h1>
        <p className="hero-subtitle">
          Transform raw university result sheets into beautiful, actionable dashboards instantly.
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`dropzone animate-fade-in-up ${isDragActive ? 'active' : ''}`}
        id="dropzone"
        style={{ animationDelay: '0.15s' }}
      >
        <input {...getInputProps()} id="result-input" />
        <div className="dropzone-icon-wrapper">
           <UploadIcon />
        </div>
        <h3 className="dropzone-title">{isDragActive ? 'Drop file to analyze...' : 'Click or Drag to Upload'}</h3>
        <p className="dropzone-hint">
          Supports PDF, XLSX, CSV up to 50MB
        </p>
      </div>

      <div className="features-grid animate-fade-in-up" style={{ animationDelay: '0.3s' }}>
        {[
          { icon: <ZapIcon />, title: 'Lightning Fast', desc: 'Instant processing' },
          { icon: <ChartIcon />, title: 'Rich Analytics', desc: 'Visual graphs & insights' },
          { icon: <PdfIcon />, title: 'Export Ready', desc: 'One-click PDF reports' },
          { icon: <ShieldIcon />, title: '100% Private', desc: 'No data is ever stored' },
        ].map((feat, i) => (
          <div className="feature-card" key={i}>
            <div className="feature-icon">{feat.icon}</div>
            <h4 className="feature-title">{feat.title}</h4>
            <p className="feature-desc">{feat.desc}</p>
          </div>
        ))}
      </div>
    </section>
  )
}
