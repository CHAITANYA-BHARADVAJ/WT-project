import StatsCards from './StatsCards'
import { BracketBarChart, PassFailPie } from './Charts'
import TopperList from './TopperList'

export default function Dashboard({ data, onExport, onReset }) {
  return (
    <div className="dashboard animate-fade-in" id="dashboard">
      {/* ─── Header ─── */}
      <div className="dashboard-header">
        <div>
          <h2 className="dashboard-title">Analysis Dashboard</h2>
          <p className="dashboard-meta">
            {data.totalStudents} students analyzed · Pass rate: {data.passRate}%
          </p>
        </div>
        <div className="dashboard-actions">
          <button className="btn btn-primary" onClick={onExport} id="export-btn">
            📄 Export PDF
          </button>
          <button className="btn btn-secondary" onClick={onReset} id="reset-btn">
            ↩ New Upload
          </button>
        </div>
      </div>

      {/* ─── Stats Cards ─── */}
      <StatsCards data={data} />

      {/* ─── Performance Brackets ─── */}
      <div className="panel">
        <div className="panel-header">
          <h3 className="panel-title">Performance Brackets</h3>
        </div>
        <div className="panel-body">
          <div className="brackets-grid stagger">
            {[
              { name: 'Elite', range: 'SGPA > 9.0', count: data.elite, cls: 'elite' },
              { name: 'Distinction', range: '7.5 – 9.0', count: data.distinction, cls: 'distinction' },
              { name: 'First Class', range: '6.5 – 7.5', count: data.firstClass, cls: 'first-class' },
              { name: 'Second Class', range: '5.0 – 6.5', count: data.secondClass, cls: 'second-class' },
              { name: 'Below Avg / Fail', range: '< 5.0', count: data.belowAvg, cls: 'below' },
            ].map((b) => (
              <div className={`bracket-card ${b.cls}`} key={b.name}>
                <div className="bracket-name">{b.name}</div>
                <div className="bracket-count">{b.count ?? 0}</div>
                <div className="bracket-pct">
                  {data.totalStudents > 0
                    ? `${(((b.count ?? 0) / data.totalStudents) * 100).toFixed(1)}%`
                    : '0%'}{' '}
                  · {b.range}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      {/* ─── Charts Row ─── */}
      <div className="charts-row">
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">📊 Grade Distribution</h3>
          </div>
          <div className="panel-body">
            <BracketBarChart data={data} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">🎯 Pass vs Fail</h3>
          </div>
          <div className="panel-body">
            <PassFailPie data={data} />
          </div>
        </div>
      </div>

      {/* ─── Topper List ─── */}
      <TopperList students={data.students} />

      {/* ─── Subject-wise Analysis ─── */}
      {data.subjects && data.subjects.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">📚 Subject-wise Analysis</h3>
          </div>
          <div className="panel-body subject-table-wrapper">
            <table className="data-table" id="subject-stats-table">
              <thead>
                <tr>
                  <th>Subject #</th>
                  <th>Avg GP</th>
                  <th>Pass Rate</th>
                  <th>Fail Count</th>
                </tr>
              </thead>
              <tbody>
                {data.subjects.map((subj, idx) => (
                  <tr key={idx}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                      Subject {idx + 1}
                    </td>
                    <td>{subj.averageGP ?? '—'}</td>
                    <td>{subj.passRate ?? '—'}%</td>
                    <td>
                      <span className="grade-badge grade-F">{subj.failCount ?? 0}</span>
                    </td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}
    </div>
  )
}
