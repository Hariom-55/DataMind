function isFiniteNumber(value) {
  return typeof value === "number" && Number.isFinite(value);
}

function BoxPlotVisualization({ visualization }) {
  const datum = Array.isArray(visualization?.data) ? visualization.data[0] : null;
  const keys = ["min", "q1", "median", "q3", "max"];
  if (!datum || !keys.every((key) => isFiniteNumber(datum[key]))) {
    return <div className="empty-state" role="alert"><strong>Invalid box plot data</strong><span>Expected numeric min, q1, median, q3, and max values.</span></div>;
  }
  if (!(datum.min <= datum.q1 && datum.q1 <= datum.median && datum.median <= datum.q3 && datum.q3 <= datum.max)) {
    return <div className="empty-state" role="alert"><strong>Invalid box plot range</strong><span>Values must satisfy min ≤ q1 ≤ median ≤ q3 ≤ max.</span></div>;
  }

  const width = 720;
  const left = 48;
  const right = width - 48;
  const span = datum.max - datum.min || 1;
  const x = (value) => left + ((value - datum.min) / span) * (right - left);
  const label = datum.column || visualization.title || "Distribution";

  return (
    <figure className="box-plot" aria-label={`Box plot for ${label}`}>
      <svg role="img" aria-label={`${label}: minimum ${datum.min}, first quartile ${datum.q1}, median ${datum.median}, third quartile ${datum.q3}, maximum ${datum.max}`} viewBox={`0 0 ${width} 150`}>
        <line x1={x(datum.min)} x2={x(datum.max)} y1="70" y2="70" stroke="currentColor" strokeWidth="2" />
        <line x1={x(datum.min)} x2={x(datum.min)} y1="52" y2="88" stroke="currentColor" strokeWidth="2" />
        <line x1={x(datum.max)} x2={x(datum.max)} y1="52" y2="88" stroke="currentColor" strokeWidth="2" />
        <rect x={x(datum.q1)} y="42" width={Math.max(1, x(datum.q3) - x(datum.q1))} height="56" fill="#dbeafe" stroke="#2563eb" strokeWidth="2" />
        <line x1={x(datum.median)} x2={x(datum.median)} y1="42" y2="98" stroke="#1d4ed8" strokeWidth="3" />
        <text x={x(datum.min)} y="122" textAnchor="middle">{datum.min}</text>
        <text x={x(datum.q1)} y="122" textAnchor="middle">Q1 {datum.q1}</text>
        <text x={x(datum.median)} y="28" textAnchor="middle">Median {datum.median}</text>
        <text x={x(datum.q3)} y="122" textAnchor="middle">Q3 {datum.q3}</text>
        <text x={x(datum.max)} y="28" textAnchor="middle">{datum.max}</text>
      </svg>
      <figcaption>{label} · whiskers show observed minimum and maximum</figcaption>
    </figure>
  );
}

export default BoxPlotVisualization;
