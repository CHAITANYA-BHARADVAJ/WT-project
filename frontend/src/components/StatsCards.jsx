export default function StatsCards({ data }) {
  const cards = [
    {
      label: 'Total Students',
      value: data.total_students,
      sub: `${data.overall_pass_count} passed - ${data.overall_fail_count} failed`,
      accent: 'indigo',
    },
    {
      label: 'Class Average SGPA',
      value: data.class_average_sgpa?.toFixed(2),
      sub: `Median: ${data.median_sgpa?.toFixed(2)}`,
      accent: 'blue',
    },
    {
      label: 'Pass Rate',
      value: `${data.pass_percentage?.toFixed(1)}%`,
      sub: `${data.overall_pass_count} of ${data.total_students}`,
      accent: 'emerald',
    },
    {
      label: 'Highest SGPA',
      value: data.max_sgpa?.toFixed(2),
      sub: `Lowest: ${data.min_sgpa?.toFixed(2)}`,
      accent: 'amber',
    },
    {
      label: 'Total O Grades',
      value: data.total_o_grades,
      sub: `${data.students_with_all_o} students all-O`,
      accent: 'emerald',
    },
    {
      label: 'Elite Students',
      value: data.elite_count,
      sub: 'SGPA > 9.0',
      accent: 'indigo',
    },
    {
      label: 'Distinction',
      value: data.distinction_count,
      sub: 'SGPA 7.5 - 9.0',
      accent: 'blue',
    },
    {
      label: 'Below Average',
      value: data.below_count + (data.overall_fail_count || 0),
      sub: 'SGPA < 5.0 + fails',
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
