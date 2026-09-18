import BarVisualization from "./visualizations/BarVisualization";
import HeatmapVisualization from "./visualizations/HeatmapVisualization";
import TableVisualization from "./visualizations/TableVisualization";

function VisualizationRenderer({ visualization }) {
  if (!visualization) {
    return null;
  }

  switch (visualization.type) {
    case "BAR":
      return (
        <BarVisualization
          visualization={visualization}
        />
      );

    case "HEATMAP":
      return (
        <HeatmapVisualization
          visualization={visualization}
        />
      );

    case "TABLE":
      return (
        <TableVisualization
          visualization={visualization}
        />
      );

    default:
      return (
        <div className="visualization-not-supported">
          <p>
            Visualization type{" "}
            <strong>{visualization.type}</strong>{" "}
            is not supported yet.
          </p>
        </div>
      );
  }
}

export default VisualizationRenderer;