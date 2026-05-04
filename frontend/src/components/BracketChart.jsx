import {
  PieChart, Pie, Cell, Tooltip, ResponsiveContainer, Legend,
} from 'recharts'

const BRACKET_COLORS = {
  Elite: '#10B981',
  Distinction: '#3B82F6',
  'First Class': '#F59E0B',
  'Second Class': '#F97316',
  'Below Avg': '#EF4444',
}

const CustomTooltip = ({ active, payload }) => {
  if (active && payload && payload.length) {
    const { name, value, payload: entry } = payload[0]
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
          {name}
        </p>
        <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
          Students: <strong style={{ color: '#f1f5f9' }}>{value}</strong>
          {entry.pct && (
            <span style={{ marginLeft: 8, color: '#64748b' }}>({entry.pct}%)</span>
          )}
        </p>
      </div>
    )
  }
  return null
}

const renderLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  if (percent < 0.05) return null
  const RADIAN = Math.PI / 180
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  return (
    <text
      x={x}
      y={y}
      fill="white"
      textAnchor="middle"
      dominantBaseline="central"
      fontSize={12}
      fontWeight={700}
      fontFamily="Inter"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

export default function BracketChart({ data }) {
  const total = data.total_students || 1
  const chartData = [
    { name: 'Elite', value: data.elite_count, pct: ((data.elite_count / total) * 100).toFixed(1) },
    { name: 'Distinction', value: data.distinction_count, pct: ((data.distinction_count / total) * 100).toFixed(1) },
    { name: 'First Class', value: data.first_class_count, pct: ((data.first_class_count / total) * 100).toFixed(1) },
    { name: 'Second Class', value: data.second_class_count, pct: ((data.second_class_count / total) * 100).toFixed(1) },
    { name: 'Below Avg', value: data.below_count, pct: ((data.below_count / total) * 100).toFixed(1) },
  ].filter((d) => d.value > 0)

  if (chartData.length === 0) return <p style={{ color: 'var(--text-muted)' }}>No bracket data</p>

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={300}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={110}
            paddingAngle={3}
            dataKey="value"
            label={renderLabel}
            labelLine={false}
            animationBegin={200}
            animationDuration={800}
          >
            {chartData.map((entry, idx) => (
              <Cell
                key={idx}
                fill={BRACKET_COLORS[entry.name] || '#94A3B8'}
                stroke="rgba(0,0,0,0.3)"
                strokeWidth={1}
              />
            ))}
          </Pie>
          <Tooltip content={<CustomTooltip />} />
          <Legend
            verticalAlign="bottom"
            iconType="circle"
            iconSize={8}
            formatter={(value) => (
              <span style={{ color: '#94a3b8', fontSize: '0.78rem', fontFamily: 'Inter' }}>
                {value}
              </span>
            )}
          />
        </PieChart>
      </ResponsiveContainer>
    </div>
  )
}
