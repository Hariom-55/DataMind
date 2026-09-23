import AnalysisSummary from "../../AnalysisSummary";
import InsightPanel from "../../InsightPanel";
import VisualizationPanel from "../../VisualizationPanel";

function InsightDashboard({ result }) {
  return (
    <>
      <AnalysisSummary result={result} />
      <InsightPanel result={result} />
      <VisualizationPanel result={result} />
    </>
  );
}

export default InsightDashboard;
