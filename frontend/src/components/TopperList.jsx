import { useMemo } from 'react'

const CATEGORY_CLASS = {
  Elite: 'elite',
  Distinction: 'distinction',
  'First Class': 'first-class',
  'Second Class': 'second-class',
  Fail: 'fail',
}

export default function TopperList({ students }) {
  const toppers = useMemo(() => {
    if (!students || students.length === 0) return []

    return [...students]
      .filter((s) => s.sgpa > 0)
      .sort((a, b) => b.sgpa - a.sgpa)
      .slice(0, 10)
  }, [students])

  if (toppers.length === 0) {
    return (
      <div className="panel" id="topper-panel">
        <div className="panel-header">
          <h3 className="panel-title">🏆 Top Performers</h3>
        </div>
        <div className="panel-body">
          <p style={{ color: 'var(--text-muted)', textAlign: 'center', padding: '1rem' }}>
            No student data available.
          </p>
        </div>
      </div>
    )
  }

  return (
    <div className="panel" id="topper-panel">
      <div className="panel-header">
        <h3 className="panel-title">🏆 Top 10 Performers</h3>
        <span style={{ fontSize: '0.78rem', color: 'var(--text-muted)' }}>
          Ranked by SGPA
        </span>
      </div>
      <div className="panel-body">
        <div className="toppers-list">
          {toppers.map((student, idx) => {
            const rankClass =
              idx === 0 ? 'gold' : idx === 1 ? 'silver' : idx === 2 ? 'bronze' : 'default'

            return (
              <div className="topper-item" key={idx}>
                <div className={`topper-rank ${rankClass}`}>{idx + 1}</div>
                <div className="topper-info">
                  <div className="topper-usn">Student #{idx + 1}</div>
                  <div className="topper-details">
                    Status: {student.status} &nbsp;·&nbsp;
                    <span className={`bracket-tag ${CATEGORY_CLASS[student.category] || 'na'}`}>
                      {student.category || 'N/A'}
                    </span>
                  </div>
                </div>
                <div className="topper-sgpa">{student.sgpa.toFixed(2)}</div>
              </div>
            )
          })}
        </div>
      </div>
    </div>
  )
}
