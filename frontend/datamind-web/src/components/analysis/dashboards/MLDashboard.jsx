import AnalysisSummary from "../../AnalysisSummary";
import VisualizationPanel from "../../VisualizationPanel";

function MLDashboard({ result }) {
  const ml = result?.analysis?.machineLearning ?? result?.machineLearning ?? result ?? {};
  const training = ml?.training ?? {};
  const metrics = training?.metrics ?? {};
  const featureImportance = training?.featureImportance ?? [];
  const isClustering = ml?.problemType === "CLUSTERING";
  const visualizations = result?.visualizations?.visualizations ?? result?.visualizations;

  return (
    <>
      <AnalysisSummary result={{ analysis: { eda: { overview: {
        rowCount: ml?.rowCount,
        columnCount: ml?.featureCount,
        numericColumnCount: ml?.featureCount,
      }}}, visualizations: result?.visualizations }} />
      <section className="specialized-grid">
        <article className="specialized-card"><span className="eyebrow">PROBLEM TYPE</span><h3>{ml?.problemType ?? "—"}</h3><p>Problem classification returned by the ML pipeline.</p></article>
        <article className="specialized-card"><span className="eyebrow">PRIMARY METRIC</span><h3>{Object.keys(metrics)[0] ?? "—"}</h3><strong>{Object.values(metrics)[0] ?? "—"}</strong><p>First evaluation metric returned by training.</p></article>
        <article className="specialized-card"><span className="eyebrow">{isClustering ? "CLUSTERS" : "FEATURE IMPORTANCE"}</span><h3>{isClustering ? "KMeans groups" : "Selected model features"}</h3><strong>{isClustering ? training.clusterCount ?? "—" : featureImportance.length}</strong><p>{isClustering ? "Groups identified from standardized numeric features." : "Importance metadata exposed by the current ML result."}</p></article>
      </section>
      {Array.isArray(visualizations) && visualizations.length > 0 && (
        <VisualizationPanel result={result} />
      )}
    </>
  );
}

export default MLDashboard;
