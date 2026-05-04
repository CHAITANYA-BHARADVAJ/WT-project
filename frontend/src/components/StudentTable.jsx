import { useState, useMemo } from 'react'

const BRACKET_CLASS_MAP = {
  Elite: 'elite',
  Distinction: 'distinction',
  'First Class': 'first-class',
  'Second Class': 'second-class',
  'Below Average': 'below',
  Fail: 'fail',
  'N/A': 'na',
  NP: 'na',
}

const gradeClass = (grade) => {
  if (grade === 'A+') return 'grade-Aplus'
  if (grade === 'B+') return 'grade-Bplus'
  return `grade-${grade}`
}

export default function StudentTable({ students }) {
  const [search, setSearch] = useState('')
  const [sortField, setSortField] = useState('sl_no')
  const [sortDir, setSortDir] = useState('asc')
  const [bracketFilter, setBracketFilter] = useState('all')

  const handleSort = (field) => {
    if (sortField === field) {
      setSortDir((d) => (d === 'asc' ? 'desc' : 'asc'))
    } else {
      setSortField(field)
      setSortDir('asc')
    }
  }

  const filtered = useMemo(() => {
    let result = [...students]

    if (search) {
      const q = search.toLowerCase()
      result = result.filter(
        (s) =>
          s.usn.toLowerCase().includes(q) ||
          (s.name || '').toLowerCase().includes(q) ||
          String(s.sl_no).includes(q)
      )
    }

    if (bracketFilter !== 'all') {
      result = result.filter((s) => s.bracket === bracketFilter)
    }

    result.sort((a, b) => {
      let va = a[sortField] ?? 0
      let vb = b[sortField] ?? 0
      if (typeof va === 'string') va = va.toLowerCase()
      if (typeof vb === 'string') vb = vb.toLowerCase()
      if (va < vb) return sortDir === 'asc' ? -1 : 1
      if (va > vb) return sortDir === 'asc' ? 1 : -1
      return 0
    })

    return result
  }, [students, search, sortField, sortDir, bracketFilter])

  const sortIndicator = (field) =>
    sortField === field ? ` (${sortDir})` : ''

  return (
    <div className="panel" id="student-table-panel">
      <div className="panel-header">
        <h3 className="panel-title">Student Records ({filtered.length})</h3>
      </div>
      <div className="panel-body">
        <div className="table-controls">
          <div className="search-wrapper">
            <span className="search-icon">Q</span>
            <input
              type="text"
              className="search-input"
              placeholder="Search by USN or name..."
              value={search}
              onChange={(e) => setSearch(e.target.value)}
              id="student-search"
            />
          </div>
          <select
            className="filter-select"
            value={bracketFilter}
            onChange={(e) => setBracketFilter(e.target.value)}
            id="bracket-filter"
          >
            <option value="all">All Brackets</option>
            <option value="Elite">Elite</option>
            <option value="Distinction">Distinction</option>
            <option value="First Class">First Class</option>
            <option value="Second Class">Second Class</option>
            <option value="Below Average">Below Average</option>
            <option value="Fail">Fail</option>
            <option value="N/A">N/A</option>
          </select>
        </div>

        <div className="subject-table-wrapper">
          <table className="data-table" id="student-table">
            <thead>
              <tr>
                <th className={sortField === 'sl_no' ? 'sorted' : ''} onClick={() => handleSort('sl_no')}>
                  Sl No{sortIndicator('sl_no')}
                </th>
                <th className={sortField === 'usn' ? 'sorted' : ''} onClick={() => handleSort('usn')}>
                  USN{sortIndicator('usn')}
                </th>
                <th>Grades</th>
                <th className={sortField === 'sgpa' ? 'sorted' : ''} onClick={() => handleSort('sgpa')}>
                  SGPA{sortIndicator('sgpa')}
                </th>
                <th className={sortField === 'cgpa' ? 'sorted' : ''} onClick={() => handleSort('cgpa')}>
                  CGPA{sortIndicator('cgpa')}
                </th>
                <th>Status</th>
                <th>Bracket</th>
              </tr>
            </thead>
            <tbody>
              {filtered.map((student) => (
                <tr key={student.usn}>
                  <td>{student.sl_no}</td>
                  <td>{student.usn}</td>
                  <td>
                    <div style={{ display: 'flex', gap: 4, flexWrap: 'wrap' }}>
                      {(student.subjects || []).map((sub, idx) => (
                        <span
                          key={idx}
                          className={`grade-badge ${gradeClass(sub.grade)}`}
                          title={`${sub.code}: ${sub.grade} (GP ${sub.grade_point})`}
                        >
                          {sub.grade}
                        </span>
                      ))}
                    </div>
                  </td>
                  <td style={{ fontWeight: 600, color: 'var(--text-primary)' }}>
                    {student.sgpa > 0 ? student.sgpa.toFixed(2) : '-'}
                  </td>
                  <td>{student.cgpa > 0 ? student.cgpa.toFixed(2) : '-'}</td>
                  <td>
                    <span
                      className={`grade-badge ${
                        student.status === 'P'
                          ? 'grade-O'
                          : student.status === 'F'
                          ? 'grade-F'
                          : 'grade-AB'
                      }`}
                    >
                      {student.status}
                    </span>
                  </td>
                  <td>
                    <span className={`bracket-tag ${BRACKET_CLASS_MAP[student.bracket] || 'na'}`}>
                      {student.bracket || 'N/A'}
                    </span>
                  </td>
                </tr>
              ))}
              {filtered.length === 0 && (
                <tr>
                  <td colSpan={7} style={{ textAlign: 'center', padding: '2rem', color: 'var(--text-muted)' }}>
                    No students match your search criteria.
                  </td>
                </tr>
              )}
            </tbody>
          </table>
        </div>
      </div>
    </div>
  )
}
