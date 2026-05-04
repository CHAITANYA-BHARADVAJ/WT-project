import StatsCards from './StatsCards'
import GradeChart from './GradeChart'
import BracketChart from './BracketChart'
import StudentTable from './StudentTable'

export default function Dashboard({ data, onExport, onReset }) {
  const toppers = data.toppers || []
  const meta = [data.college_name, data.program, data.semester, data.exam_date]
    .filter(Boolean)
    .join(' - ')

  return (
    <div className="dashboard animate-fade-in">
      <div className="dashboard-header">
        <div>
          <h2 className="dashboard-title">Analysis Dashboard</h2>
          <p className="dashboard-meta">
            {meta || `${data.total_students} students analyzed`}
          </p>
        </div>
        <div className="dashboard-actions">
          <button className="btn btn-primary" onClick={onExport} id="export-btn">
            Export PDF
          </button>
          <button className="btn btn-secondary" onClick={onReset} id="reset-btn">
            New Upload
          </button>
        </div>
      </div>

      <StatsCards data={data} />

      <div className="panel">
        <div className="panel-header">
          <h3 className="panel-title">Performance Brackets</h3>
        </div>
        <div className="panel-body">
          <div className="brackets-grid stagger">
            {[
              { name: 'Elite', range: 'SGPA > 9.0', count: data.elite_count, cls: 'elite' },
              { name: 'Distinction', range: '7.5 - 9.0', count: data.distinction_count, cls: 'distinction' },
              { name: 'First Class', range: '6.5 - 7.5', count: data.first_class_count, cls: 'first-class' },
              { name: 'Second Class', range: '5.0 - 6.5', count: data.second_class_count, cls: 'second-class' },
              { name: 'Below Avg', range: '< 5.0', count: data.below_count, cls: 'below' },
            ].map((b) => (
              <div className={`bracket-card ${b.cls}`} key={b.name}>
                <div className="bracket-name">{b.name}</div>
                <div className="bracket-count">{b.count}</div>
                <div className="bracket-pct">
                  {data.total_students > 0
                    ? `${((b.count / data.total_students) * 100).toFixed(1)}%`
                    : '0%'}{' '}
                  - {b.range}
                </div>
              </div>
            ))}
          </div>
        </div>
      </div>

      <div className="charts-row">
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Grade Distribution</h3>
          </div>
          <div className="panel-body">
            <GradeChart data={data.grade_distribution} />
          </div>
        </div>

        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">SGPA Spread</h3>
          </div>
          <div className="panel-body">
            <BracketChart data={data} />
          </div>
        </div>
      </div>

      {toppers.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Top Performers</h3>
          </div>
          <div className="panel-body">
            <div className="toppers-list">
              {toppers.map((student, idx) => {
                const rankClass =
                  idx === 0 ? 'gold' : idx === 1 ? 'silver' : idx === 2 ? 'bronze' : 'default'
                const oCount = student.subjects
                  ? student.subjects.filter((s) => s.grade === 'O').length
                  : 0

                return (
                  <div className="topper-item" key={student.usn}>
                    <div className={`topper-rank ${rankClass}`}>{idx + 1}</div>
                    <div className="topper-info">
                      <div className="topper-usn">{student.usn}</div>
                      <div className="topper-details">
                        {oCount} O grades - {student.subjects?.length || 0} subjects -{' '}
                        <span className={`bracket-tag ${student.bracket?.toLowerCase().replace(/\s+/g, '-') || 'na'}`}>
                          {student.bracket || 'N/A'}
                        </span>
                      </div>
                    </div>
                    <div className="topper-sgpa">{student.sgpa?.toFixed(2)}</div>
                  </div>
                )
              })}
            </div>
          </div>
        </div>
      )}

      {data.subject_stats && data.subject_stats.length > 0 && (
        <div className="panel">
          <div className="panel-header">
            <h3 className="panel-title">Subject-wise Analysis</h3>
          </div>
          <div className="panel-body subject-table-wrapper">
            <table className="data-table" id="subject-stats-table">
              <thead>
                <tr>
                  <th>Subject</th>
                  <th>Students</th>
                  <th>O</th>
                  <th>A+</th>
                  <th>A</th>
                  <th>B+</th>
                  <th>B</th>
                  <th>C</th>
                  <th>P</th>
                  <th>F</th>
                  <th>Pass %</th>
                  <th>Avg GP</th>
                </tr>
              </thead>
              <tbody>
                {data.subject_stats.map((subj) => (
                  <tr key={subj.code}>
                    <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>{subj.code}</td>
                    <td>{subj.total_students}</td>
                    <td><span className="grade-badge grade-O">{subj.o_grade_count}</span></td>
                    <td><span className="grade-badge grade-Aplus">{subj.a_plus_count}</span></td>
                    <td><span className="grade-badge grade-A">{subj.a_count}</span></td>
                    <td><span className="grade-badge grade-Bplus">{subj.b_plus_count}</span></td>
                    <td><span className="grade-badge grade-B">{subj.b_count}</span></td>
                    <td><span className="grade-badge grade-C">{subj.c_count}</span></td>
                    <td><span className="grade-badge grade-P">{subj.p_count}</span></td>
                    <td><span className="grade-badge grade-F">{subj.f_count}</span></td>
                    <td>{subj.pass_percentage?.toFixed(1)}%</td>
                    <td>{subj.avg_grade_point?.toFixed(1)}</td>
                  </tr>
                ))}
              </tbody>
            </table>
          </div>
        </div>
      )}

      <StudentTable students={data.students || []} />
    </div>
  )
}
