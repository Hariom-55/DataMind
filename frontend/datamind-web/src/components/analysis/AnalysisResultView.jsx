import AnalysisDashboardRouter from "./AnalysisDashboardRouter";
import { normalizeAnalysisResult } from "../../utils/analysisResult";

function AnalysisResultView({ result, analysisType }) {
  if (!result || typeof result !== "object") {
    return (
      <div className="empty-state">
        <strong>No analysis result available.</strong>
        <span>Run an analysis to populate the dashboard.</span>
      </div>
    );
  }

  const analysisResult = normalizeAnalysisResult(result);

  if (!analysisResult) {
    return (
      <div className="empty-state">
        <strong>Analysis result could not be parsed.</strong>
        <span>The API returned an unexpected result structure.</span>
      </div>
    );
  }

  const isDirectEdaResult = Boolean(
    analysisResult.overview ||
    analysisResult.numericStatistics ||
    analysisResult.categoricalStatistics ||
    analysisResult.missingValues,
  );
  const resolvedType = String(
    analysisType ||
    result.analysisType ||
    result.job?.analysisType ||
    analysisResult.analysisType ||
    (analysisResult.analysis ? "INSIGHT" : isDirectEdaResult ? "EDA" : "INSIGHT"),
  ).toUpperCase();

  return (
    <section className="dashboard">
      <div className="dashboard-header">
        <div>
          <span className="eyebrow">ANALYSIS COMPLETE</span>
          <h2>Analysis Dashboard</h2>
          <p>
            Production dashboard for the {resolvedType.replaceAll("_", " ").toLowerCase()} analytical workflow.
          </p>
        </div>
        <div className="dashboard-state">
          <span className="status-dot" />
          Result ready
        </div>
      </div>

      <AnalysisDashboardRouter
        analysisType={resolvedType}
        result={analysisResult}
      />
    </section>
  );
}

export default AnalysisResultView;
