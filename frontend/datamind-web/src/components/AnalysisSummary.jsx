function AnalysisSummary({ result }) {
  const analysis = result?.analysis ?? {};
  const eda = analysis.eda ?? {};
  const overview = eda.overview ?? {};

  const insights = result?.insights ?? {};
  const insightSummary = insights.summary ?? {};

  const visualizations = result?.visualizations?.visualizations ?? [];

  return (
    <section className="analysis-summary">
      <h2>Analysis Summary</h2>

      <div className="summary-grid">
        <div className="summary-card">
          <span>Rows</span>
          <strong>{overview.rowCount ?? "—"}</strong>
        </div>

        <div className="summary-card">
          <span>Columns</span>
          <strong>{overview.columnCount ?? "—"}</strong>
        </div>

        <div className="summary-card">
          <span>Insights</span>
          <strong>{insightSummary.total ?? 0}</strong>
        </div>

        <div className="summary-card">
          <span>Visualizations</span>
          <strong>{visualizations.length}</strong>
        </div>
      </div>
    </section>
  );
}

export default AnalysisSummary;