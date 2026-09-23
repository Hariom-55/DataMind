import AnalysisSummary from "../../AnalysisSummary";
import VisualizationPanel from "../../VisualizationPanel";

function EDADashboard({ result }) {
  const analysis = result?.analysis?.eda ?? result?.eda ?? result ?? {};
  const quality = analysis?.dataQuality ?? {};
  const outliers = analysis?.outlierSignals ?? {};
  const rareCategoryCount = Object.values(analysis?.categoricalStatistics ?? {})
    .reduce((total, stats) => total + Object.keys(stats.rareValues ?? {}).length, 0);
  const visualizations = result?.visualizations?.visualizations ?? result?.visualizations;

  return (
    <>
      <AnalysisSummary result={{ analysis: { eda: analysis }, visualizations: result?.visualizations }} />
      <section className="specialized-grid">
        <article className="specialized-card">
          <span className="eyebrow">DATA QUALITY</span>
          <h3>Quality diagnostics</h3>
          <strong>{quality.score ?? quality.qualityScore ?? "—"}</strong>
          <p>Quality score returned by the EDA quality analyzer.</p>
        </article>
        <article className="specialized-card">
          <span className="eyebrow">OUTLIERS</span>
          <h3>Columns with outlier signals</h3>
          <strong>{Object.keys(outliers).length}</strong>
          <p>IQR-based signals generated during profiling.</p>
        </article>
        <article className="specialized-card">
          <span className="eyebrow">RARE CATEGORIES</span>
          <h3>Singleton category values</h3>
          <strong>{rareCategoryCount}</strong>
          <p>Observed category values appearing once in the dataset.</p>
        </article>
        <article className="specialized-card">
          <span className="eyebrow">SCHEMA</span>
          <h3>Profiled columns</h3>
          <strong>{analysis?.schema?.length ?? analysis?.columns?.length ?? "—"}</strong>
          <p>Column-level type, missingness and cardinality metadata.</p>
        </article>
      </section>
      {Array.isArray(visualizations) && visualizations.length > 0 && (
        <VisualizationPanel result={result} />
      )}
    </>
  );
}

export default EDADashboard;
