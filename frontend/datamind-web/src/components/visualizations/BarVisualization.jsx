import {
  Bar,
  BarChart,
  CartesianGrid,
  ResponsiveContainer,
  Tooltip,
  XAxis,
  YAxis,
} from "recharts";

function BarVisualization({ visualization }) {
  const data = Array.isArray(visualization.data)
    ? visualization.data
    : [];

  if (data.length === 0) {
    return <p>No data available for this visualization.</p>;
  }
  const valid = typeof visualization.x === "string"
    && typeof visualization.y === "string"
    && data.every((row) => row && typeof row === "object" && !Array.isArray(row)
      && Object.hasOwn(row, visualization.x)
      && typeof row[visualization.y] === "number" && Number.isFinite(row[visualization.y]));
  if (!valid) {
    return <div className="empty-state" role="alert"><strong>Invalid bar chart data</strong><span>Each row must include the configured category and a finite numeric value.</span></div>;
  }

  return (
    <div className="chart-container">
      <ResponsiveContainer width="100%" height={320}>
        <BarChart data={data}>
          <CartesianGrid strokeDasharray="3 3" />

          <XAxis
            dataKey={visualization.x}
            angle={-20}
            textAnchor="end"
            height={70}
          />

          <YAxis />

          <Tooltip />

          <Bar dataKey={visualization.y} />
        </BarChart>
      </ResponsiveContainer>
    </div>
  );
}

export default BarVisualization;
