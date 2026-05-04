import { useCallback } from 'react'
import { useDropzone } from 'react-dropzone'

const ACCEPTED_FILES = {
  'application/pdf': ['.pdf'],
  'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet': ['.xlsx'],
  'application/vnd.ms-excel.sheet.macroEnabled.12': ['.xlsm'],
  'text/csv': ['.csv'],
}

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
        <h1>Analyze University Results</h1>
        <p>
          Upload a PDF, Excel, or CSV result sheet and get instant statistical analysis:
          grade distributions, SGPA brackets, toppers, and exportable reports.
          <br />
          <em style={{ color: 'var(--text-muted)', fontSize: '0.85rem' }}>
            100% private - processed in memory - nothing stored
          </em>
        </p>
      </div>

      <div
        {...getRootProps()}
        className={`dropzone animate-fade-in-up ${isDragActive ? 'active' : ''}`}
        id="dropzone"
        style={{ animationDelay: '0.15s' }}
      >
        <input {...getInputProps()} id="result-input" />
        <span className="dropzone-icon">PDF/XLSX</span>
        <h3>
          {isDragActive
            ? 'Drop your result file here...'
            : 'Drag and drop your result file'}
        </h3>
        <p>
          or <span className="dropzone-browse">browse files</span> - PDF, XLSX, XLSM, or CSV up to 50MB
        </p>
      </div>

      <div
        className="animate-fade-in-up"
        style={{
          display: 'flex',
          gap: '2rem',
          marginTop: '1rem',
          animationDelay: '0.3s',
          flexWrap: 'wrap',
          justifyContent: 'center',
        }}
      >
        {[
          { icon: '01', label: 'Instant Analysis' },
          { icon: '02', label: 'Rich Charts' },
          { icon: '03', label: 'PDF Export' },
          { icon: '04', label: 'Privacy First' },
        ].map((feat) => (
          <div
            key={feat.label}
            style={{
              textAlign: 'center',
              color: 'var(--text-muted)',
              fontSize: '0.78rem',
            }}
          >
            <span style={{ fontSize: '1rem', display: 'block', marginBottom: '0.3rem', fontWeight: 700 }}>
              {feat.icon}
            </span>
            {feat.label}
          </div>
        ))}
      </div>
    </section>
  )
}
