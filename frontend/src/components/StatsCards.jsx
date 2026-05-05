export default function StatsCards({ data }) {
  const cards = [
    {
      label: 'Total Students',
      value: data.totalStudents ?? 0,
      sub: `${data.passed ?? 0} passed · ${data.failed ?? 0} failed`,
      accent: 'indigo',
    },
    {
      label: 'Average SGPA',
      value: data.averageSGPA ?? '—',
      sub: `Range: ${data.lowestSGPA ?? '—'} – ${data.highestSGPA ?? '—'}`,
      accent: 'blue',
    },
    {
      label: 'Pass Rate',
      value: `${data.passRate ?? 0}%`,
      sub: `${data.passed ?? 0} of ${data.totalStudents ?? 0}`,
      accent: 'emerald',
    },
    {
      label: 'Highest SGPA',
      value: data.highestSGPA ?? '—',
      sub: `Lowest: ${data.lowestSGPA ?? '—'}`,
      accent: 'amber',
    },
    {
      label: 'Elite',
      value: data.elite ?? 0,
      sub: 'SGPA > 9.0',
      accent: 'emerald',
    },
    {
      label: 'Distinction',
      value: data.distinction ?? 0,
      sub: 'SGPA 7.5 – 9.0',
      accent: 'indigo',
    },
    {
      label: 'First Class',
      value: data.firstClass ?? 0,
      sub: 'SGPA 6.5 – 7.5',
      accent: 'blue',
    },
    {
      label: 'Below Avg / Fail',
      value: (data.secondClass ?? 0) + (data.belowAvg ?? 0),
      sub: 'SGPA < 6.5',
      accent: 'rose',
    },
  ]

  return (
    <div className="stats-grid stagger" id="stats-cards">
      {cards.map((card) => (
        <div className={`stat-card ${card.accent}`} key={card.label}>
          <div className="label">{card.label}</div>
          <div className="value">{card.value}</div>
          <div className="sub">{card.sub}</div>
        </div>
      ))}
    </div>
  )
}
