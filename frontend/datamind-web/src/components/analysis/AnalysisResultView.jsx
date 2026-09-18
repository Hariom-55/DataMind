import AnalysisSummary from "../AnalysisSummary";
import InsightPanel from "../InsightPanel";
import VisualizationPanel from "../VisualizationPanel";

function AnalysisResultView({ result }) {
  if (!result || typeof result !== "object") {
    return <p>No analysis result available.</p>;
  }

  const analysisResult = result.result ?? result;

  return (
    <section className="analysis-result">
      <h2>Analysis Result</h2>

      <AnalysisSummary result={analysisResult} />

      <InsightPanel result={analysisResult} />

      <VisualizationPanel result={analysisResult} />
    </section>
  );
}

export default AnalysisResultView;