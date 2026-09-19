import AnalysisSummary from "../AnalysisSummary";
import InsightPanel from "../InsightPanel";
import VisualizationPanel from "../VisualizationPanel";
import { normalizeAnalysisResult } from "../../utils/analysisResult";

function AnalysisResultView({ result }) {
  if (!result || typeof result !== "object") {
    return (
      <div className="empty-state">
        <strong>
          No analysis result available.
        </strong>

        <span>
          Run an analysis to populate the dashboard.
        </span>
      </div>
    );
  }

  const analysisResult =
    normalizeAnalysisResult(result);

  if (!analysisResult) {
    return (
      <div className="empty-state">
        <strong>
          Analysis result could not be parsed.
        </strong>

        <span>
          The API returned an unexpected result structure.
        </span>
      </div>
    );
  }

  return (
    <section className="dashboard">
      <div className="dashboard-header">
        <div>
          <span className="eyebrow">
            ANALYSIS COMPLETE
          </span>

          <h2>
            Analysis Dashboard
          </h2>

          <p>
            Review dataset structure, detected
            insights and generated visual analytics.
          </p>
        </div>

        <div className="dashboard-state">
          <span className="status-dot" />
          Result ready
        </div>
      </div>

      <AnalysisSummary
        result={analysisResult}
      />

      {analysisResult.insights && (
        <InsightPanel
          result={analysisResult}
        />
      )}

      {analysisResult.visualizations && (
        <VisualizationPanel
          result={analysisResult}
        />
      )}
    </section>
  );
}

export default AnalysisResultView;