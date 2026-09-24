import EDADashboard from "./dashboards/EDADashboard";
import StatisticalDashboard from "./dashboards/StatisticalDashboard";
import InsightDashboard from "./dashboards/InsightDashboard";
import MLDashboard from "./dashboards/MLDashboard";

function AnalysisDashboardRouter({ analysisType, result }) {
  const type = String(analysisType || "INSIGHT").toUpperCase();

  switch (type) {
    case "EDA":
      return <EDADashboard result={result} />;
    case "STATISTICAL":
      return <StatisticalDashboard result={result} />;
    case "MACHINE_LEARNING":
      return <MLDashboard result={result} />;
    case "INSIGHT":
      return <InsightDashboard result={result} />;
    default:
      return (
        <div className="empty-state" role="alert">
          <strong>Unsupported analysis type.</strong>
          <span>This dashboard does not support “{type}”.</span>
        </div>
      );
  }
}

export default AnalysisDashboardRouter;
