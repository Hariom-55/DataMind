import AnalysisSummary from "../../AnalysisSummary";
import VisualizationPanel from "../../VisualizationPanel";

function StatisticalDashboard({ result }) {
  const statistical = result?.analysis?.statistical ?? result?.statistical ?? result ?? {};
  const descriptive = statistical?.descriptiveStatistics ?? {};
  const correlations = statistical?.correlations ?? {};
  const columns = Object.keys(descriptive);
  const visualizations = result?.visualizations?.visualizations ?? result?.visualizations;

  return (
    <>
      <AnalysisSummary result={{ analysis: { eda: { overview: {
        rowCount: statistical.sampleSize,
        numericColumnCount: statistical.numericColumnCount,
        columnCount: statistical.numericColumnCount,
      }}}, visualizations: result?.visualizations }} />
      <section className="table-container specialized-table">
        <div className="section-heading">
          <div>
            <span className="eyebrow">STATISTICAL PROFILE</span>
            <h2>Descriptive statistics</h2>
            <p>Central tendency and dispersion for numerical variables.</p>
          </div>
        </div>
        {columns.length === 0 ? (
          <div className="empty-state"><strong>No numerical statistics</strong><span>No numeric columns were available for statistical analysis.</span></div>
        ) : (
          <table>
            <thead><tr><th>Variable</th><th>Mean</th><th>Median</th><th>Std Dev</th><th>Min</th><th>Max</th></tr></thead>
            <tbody>
              {columns.map((column) => {
                const row = descriptive[column] || {};
                return <tr key={column}><td>{column}</td><td>{row.mean ?? "—"}</td><td>{row.median ?? row["50%"] ?? "—"}</td><td>{row.standardDeviation ?? row.std ?? row["std"] ?? "—"}</td><td>{row.min ?? "—"}</td><td>{row.max ?? "—"}</td></tr>;
              })}
            </tbody>
          </table>
        )}
      </section>
      <section className="specialized-grid">
        <article className="specialized-card"><span className="eyebrow">PEARSON</span><h3>Correlation matrix</h3><strong>{Object.keys(correlations.pearson ?? {}).length}</strong><p>Variables represented in the Pearson correlation result.</p></article>
        <article className="specialized-card"><span className="eyebrow">SPEARMAN</span><h3>Rank correlation</h3><strong>{Object.keys(correlations.spearman ?? {}).length}</strong><p>Variables represented in the Spearman correlation result.</p></article>
      </section>
      {Array.isArray(visualizations) && visualizations.length > 0 && (
        <VisualizationPanel result={result} />
      )}
    </>
  );
}

export default StatisticalDashboard;
