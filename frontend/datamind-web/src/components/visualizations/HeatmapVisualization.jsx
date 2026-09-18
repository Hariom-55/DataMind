function getCellIntensity(value) {
  if (typeof value !== "number") {
    return 0;
  }

  return Math.min(Math.abs(value), 1);
}

function HeatmapVisualization({ visualization }) {
  const data = Array.isArray(visualization.data)
    ? visualization.data
    : [];

  const columns = Array.isArray(
    visualization.metadata?.columns,
  )
    ? visualization.metadata.columns
    : [];

  if (data.length === 0 || columns.length === 0) {
    return <p>No data available for this visualization.</p>;
  }

  return (
    <div className="heatmap-container">
      <div
        className="heatmap-grid"
        style={{
          gridTemplateColumns: `120px repeat(${columns.length}, minmax(80px, 1fr))`,
        }}
      >
        <div className="heatmap-header" />

        {columns.map((column) => (
          <div
            className="heatmap-header"
            key={column}
          >
            {column}
          </div>
        ))}

        {data.map((row) => (
          <div
            className="heatmap-row"
            key={row.row}
            style={{
              display: "contents",
            }}
          >
            <div className="heatmap-label">
              {row.row}
            </div>

            {columns.map((column) => {
              const value = row[column];

              return (
                <div
                  className="heatmap-cell"
                  key={`${row.row}-${column}`}
                  title={`${row.row} × ${column}: ${value ?? "N/A"}`}
                  style={{
                    opacity:
                      value === null ||
                      value === undefined
                        ? 0.15
                        : 0.25 +
                          getCellIntensity(value) * 0.75,
                  }}
                >
                  {typeof value === "number"
                    ? value.toFixed(2)
                    : "—"}
                </div>
              );
            })}
          </div>
        ))}
      </div>
    </div>
  );
}

export default HeatmapVisualization;