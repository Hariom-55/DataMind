import BarVisualization from "./visualizations/BarVisualization";
import HeatmapVisualization from "./visualizations/HeatmapVisualization";
import TableVisualization from "./visualizations/TableVisualization";
import BoxPlotVisualization from "./visualizations/BoxPlotVisualization";
import { ResponsiveContainer, LineChart, Line, ScatterChart, Scatter, XAxis, YAxis, CartesianGrid, Tooltip, PieChart, Pie, Cell, BarChart, Bar } from "recharts";

function GenericChart({ visualization }) {
  const data = Array.isArray(visualization?.data) ? visualization.data : [];
  const x = visualization?.x || Object.keys(data[0] || {})[0];
  const y = visualization?.y || Object.keys(data[0] || {})[1];

  if (!data.length) {
    return (
      <div className="empty-state">
        <strong>No chart data</strong>
        <span>The visualization specification did not contain renderable rows.</span>
      </div>
    );
  }

  const rowsAreObjects = data.every((row) => row && typeof row === "object" && !Array.isArray(row));
  const valueKey = visualization.type === "SCATTER" ? y : y;
  const hasValidAxes = typeof x === "string" && typeof y === "string"
    && rowsAreObjects
    && data.every((row) => Object.hasOwn(row, x) && Object.hasOwn(row, valueKey)
      && typeof row[valueKey] === "number" && Number.isFinite(row[valueKey])
      && (visualization.type !== "SCATTER" || (typeof row[x] === "number" && Number.isFinite(row[x]))));
  if (!hasValidAxes) {
    return <div className="empty-state" role="alert"><strong>Invalid {visualization.type.toLowerCase()} chart data</strong><span>Chart rows must contain the configured axes and finite numeric values.</span></div>;
  }

  switch (visualization.type) {
    case "LINE":
      return (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <LineChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={x} />
              <YAxis />
              <Tooltip />
              <Line type="monotone" dataKey={y} dot={false} />
            </LineChart>
          </ResponsiveContainer>
        </div>
      );
    case "SCATTER":
      return (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <ScatterChart>
              <CartesianGrid />
              <XAxis dataKey={x} name={x} />
              <YAxis dataKey={y} name={y} />
              <Tooltip cursor={{ strokeDasharray: "3 3" }} />
              <Scatter data={data} />
            </ScatterChart>
          </ResponsiveContainer>
        </div>
      );
    case "HISTOGRAM":
      return (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <BarChart data={data}>
              <CartesianGrid strokeDasharray="3 3" />
              <XAxis dataKey={x} />
              <YAxis />
              <Tooltip />
              <Bar dataKey={y} />
            </BarChart>
          </ResponsiveContainer>
        </div>
      );
    case "PIE":
      return (
        <div className="chart-container">
          <ResponsiveContainer width="100%" height={320}>
            <PieChart>
              <Pie data={data} dataKey={y} nameKey={x} outerRadius={110} label>
                {data.map((entry, index) => <Cell key={`${entry[x]}-${index}`} />)}
              </Pie>
              <Tooltip />
            </PieChart>
          </ResponsiveContainer>
        </div>
      );
    default:
      return null;
  }
}

function VisualizationRenderer({ visualization }) {
  if (!visualization) return null;

  switch (visualization.type) {
    case "BAR":
      return <BarVisualization visualization={visualization} />;
    case "HEATMAP":
      return <HeatmapVisualization visualization={visualization} />;
    case "TABLE":
      return <TableVisualization visualization={visualization} />;
    case "BOX_PLOT":
      return <BoxPlotVisualization visualization={visualization} />;
    case "LINE":
    case "SCATTER":
    case "HISTOGRAM":
    case "PIE":
      return <GenericChart visualization={visualization} />;
    default:
      return (
        <div className="visualization-not-supported">
          <p>
            Visualization type <strong>{visualization.type}</strong> is not supported by the current renderer.
          </p>
        </div>
      );
  }
}

export default VisualizationRenderer;
