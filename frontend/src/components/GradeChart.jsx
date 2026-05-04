import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
} from 'recharts'

const GRADE_COLORS = {
  O: '#10B981',
  'A+': '#3B82F6',
  A: '#6366F1',
  'B+': '#8B5CF6',
  B: '#F59E0B',
  C: '#F97316',
  P: '#FBBF24',
  F: '#EF4444',
  AB: '#6B7280',
  NE: '#9CA3AF',
}

const CustomTooltip = ({ active, payload, label }) => {
  if (active && payload && payload.length) {
    return (
      <div
        style={{
          background: '#1e293b',
          border: '1px solid rgba(255,255,255,0.1)',
          borderRadius: 8,
          padding: '0.6rem 1rem',
          boxShadow: '0 8px 32px rgba(0,0,0,0.4)',
        }}
      >
        <p style={{ fontWeight: 600, color: '#f1f5f9', marginBottom: 4 }}>
          Grade: {label}
        </p>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
          Count: <strong style={{ color: '#f1f5f9' }}>{payload[0].value}</strong>
        </p>
      </div>
    )
  }
  return null
}

export default function GradeChart({ data }) {
  if (!data) return null

  const chartData = Object.entries(data)
    .filter(([, count]) => count > 0)
    .map(([grade, count]) => ({
      grade,
      count,
      fill: GRADE_COLORS[grade] || '#94A3B8',
    }))

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <BarChart
          data={chartData}
          margin={{ top: 10, right: 10, left: -10, bottom: 5 }}
        >
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis
            dataKey="grade"
            tick={{ fill: '#94a3b8', fontSize: 12, fontFamily: 'Inter' }}
            axisLine={{ stroke: 'rgba(255,255,255,0.06)' }}
            tickLine={false}
          />
          <YAxis
            tick={{ fill: '#64748b', fontSize: 11, fontFamily: 'Inter' }}
            axisLine={false}
            tickLine={false}
            allowDecimals={false}
          />
          <Tooltip content={<CustomTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={48}>
            {chartData.map((entry, idx) => (
              <Cell key={idx} fill={entry.fill} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}
