import {
  BarChart, Bar, XAxis, YAxis, CartesianGrid, Tooltip,
  ResponsiveContainer, Cell,
  PieChart, Pie, Legend,
} from 'recharts'

/* ─── Color Palettes ─── */
const BRACKET_COLORS = {
  Elite: '#10B981',
  Distinction: '#3B82F6',
  'First Class': '#F59E0B',
  'Second Class': '#F97316',
  Fail: '#EF4444',
}

const PIE_COLORS = ['#10B981', '#EF4444']

/* ─── Custom Tooltip ─── */
const ChartTooltip = ({ active, payload, label }) => {
  if (!active || !payload?.length) return null
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
        {label || payload[0].name}
      </p>
      <p style={{ color: '#94a3b8', fontSize: '0.85rem' }}>
        Count: <strong style={{ color: '#f1f5f9' }}>{payload[0].value}</strong>
      </p>
    </div>
  )
}

/* ─── Pie label renderer ─── */
const renderPieLabel = ({ cx, cy, midAngle, innerRadius, outerRadius, percent }) => {
  if (percent < 0.05) return null
  const RADIAN = Math.PI / 180
  const radius = innerRadius + (outerRadius - innerRadius) * 0.5
  const x = cx + radius * Math.cos(-midAngle * RADIAN)
  const y = cy + radius * Math.sin(-midAngle * RADIAN)
  return (
    <text
      x={x} y={y} fill="white" textAnchor="middle"
      dominantBaseline="central" fontSize={13} fontWeight={700} fontFamily="Inter"
    >
      {`${(percent * 100).toFixed(0)}%`}
    </text>
  )
}

/* ═══════════════════════════════════════════════════
   BracketBarChart — Elite / Distinction / First / Second / Fail
   ═══════════════════════════════════════════════════ */
export function BracketBarChart({ data }) {
  const chartData = [
    { name: 'Elite', count: data.elite || 0 },
    { name: 'Distinction', count: data.distinction || 0 },
    { name: 'First Class', count: data.firstClass || 0 },
    { name: 'Second Class', count: data.secondClass || 0 },
    { name: 'Fail', count: data.belowAvg || 0 },
  ]

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={chartData} margin={{ top: 10, right: 10, left: -10, bottom: 5 }}>
          <CartesianGrid strokeDasharray="3 3" stroke="rgba(255,255,255,0.04)" />
          <XAxis
            dataKey="name"
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
          <Tooltip content={<ChartTooltip />} cursor={{ fill: 'rgba(255,255,255,0.03)' }} />
          <Bar dataKey="count" radius={[6, 6, 0, 0]} maxBarSize={52}>
            {chartData.map((entry, idx) => (
              <Cell key={idx} fill={BRACKET_COLORS[entry.name] || '#94A3B8'} />
            ))}
          </Bar>
        </BarChart>
      </ResponsiveContainer>
    </div>
  )
}

/* ═══════════════════════════════════════════════════
   PassFailPie — Passed vs Failed donut chart
   ═══════════════════════════════════════════════════ */
export function PassFailPie({ data }) {
  const chartData = [
    { name: 'Passed', value: data.passed || 0 },
    { name: 'Failed', value: data.failed || 0 },
  ].filter((d) => d.value > 0)

  if (chartData.length === 0) {
    return <p style={{ color: 'var(--text-muted)', textAlign: 'center' }}>No data available</p>
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={320}>
        <PieChart>
          <Pie
            data={chartData}
            cx="50%"
            cy="50%"
            innerRadius={60}
            outerRadius={110}
            paddingAngle={4}
            dataKey="value"
            label={renderPieLabel}
            labelLine={false}
            animationBegin={200}
            animationDuration={800}
          >
            {chartData.map((entry, idx) => (
              <Cell
                key={idx}
                fill={PIE_COLORS[idx]}
                stroke="rgba(0,0,0,0.3)"
                strokeWidth={1}
              />
            ))}
          </Pie>
          <Tooltip content={<ChartTooltip />} />
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
