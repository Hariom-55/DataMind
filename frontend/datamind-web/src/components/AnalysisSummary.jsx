function getFirstDefined(...values) {
  return values.find(
    (value) =>
      value !== undefined &&
      value !== null,
  );
}

function AnalysisSummary({ result }) {
  const analysis =
    result?.analysis ?? {};

  const eda =
    analysis?.eda ?? {};

  const overview =
    eda?.overview ??
    analysis?.overview ??
    result?.overview ??
    {};

  const insights =
    result?.insights ?? {};

  const insightSummary =
    insights?.summary ?? {};

  const visualizations =
    Array.isArray(
      result?.visualizations?.visualizations,
    )
      ? result.visualizations.visualizations
      : Array.isArray(result?.visualizations)
        ? result.visualizations
        : [];

  const rowCount = getFirstDefined(
    overview.rowCount,
    overview.rows,
    overview.totalRows,
    eda.rowCount,
    analysis.rowCount,
    result.rowCount,
  );

  const columnCount = getFirstDefined(
    overview.columnCount,
    overview.columns,
    overview.totalColumns,
    eda.columnCount,
    analysis.columnCount,
    result.columnCount,
  );

  const numericColumnCount =
    getFirstDefined(
      overview.numericColumnCount,
      overview.numericColumns?.length,
      eda.numericColumnCount,
      analysis.numericColumnCount,
      result?.numericStatistics
        ? Object.keys(result.numericStatistics).length
        : undefined,
    );

  const categoricalColumnCount =
    getFirstDefined(
      overview.categoricalColumnCount,
      overview.categoricalColumns?.length,
      eda.categoricalColumnCount,
      analysis.categoricalColumnCount,
      result?.categoricalStatistics
        ? Object.keys(result.categoricalStatistics).length
        : undefined,
    );

  return (
    <section className="analysis-summary">
      <div className="section-heading">
        <div>
          <span className="eyebrow">
            DATA OVERVIEW
          </span>

          <h2>
            Dataset health & structure
          </h2>

          <p>
            High-level characteristics detected
            during analysis.
          </p>
        </div>
      </div>

      <div className="summary-grid">
        <article className="summary-card">
          <span className="summary-label">
            ROWS
          </span>

          <strong>
            {rowCount ?? "—"}
          </strong>

          <small>
            Records analyzed
          </small>
        </article>

        <article className="summary-card">
          <span className="summary-label">
            COLUMNS
          </span>

          <strong>
            {columnCount ?? "—"}
          </strong>

          <small>
            Features detected
          </small>
        </article>

        <article className="summary-card">
          <span className="summary-label">
            NUMERIC
          </span>

          <strong>
            {numericColumnCount ?? "—"}
          </strong>

          <small>
            Numerical variables
          </small>
        </article>

        <article className="summary-card">
          <span className="summary-label">
            CATEGORICAL
          </span>

          <strong>
            {categoricalColumnCount ?? "—"}
          </strong>

          <small>
            Categorical variables
          </small>
        </article>

        <article className="summary-card summary-card-accent">
          <span className="summary-label">
            INSIGHTS
          </span>

          <strong>
            {insightSummary.total ?? insightSummary.totalInsights ?? 0}
          </strong>

          <small>
            Detected observations
          </small>
        </article>

        <article className="summary-card">
          <span className="summary-label">
            VISUALIZATIONS
          </span>

          <strong>
            {visualizations.length}
          </strong>

          <small>
            Generated views
          </small>
        </article>
      </div>
    </section>
  );
}

export default AnalysisSummary;