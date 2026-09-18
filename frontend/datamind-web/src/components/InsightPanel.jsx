function InsightPanel({ result }) {
  const insights = result?.insights ?? {};
  const summary = insights.summary ?? {};
  const items = Array.isArray(insights.insights)
    ? insights.insights
    : [];

  return (
    <section className="insight-panel">
      <h2>Insights</h2>

      <div className="insight-summary">
        <span>Total: {summary.total ?? 0}</span>
        <span>High: {summary.high ?? 0}</span>
        <span>Medium: {summary.medium ?? 0}</span>
        <span>Low: {summary.low ?? 0}</span>
        <span>Info: {summary.info ?? 0}</span>
      </div>

      {items.length === 0 ? (
        <p>No insights were generated.</p>
      ) : (
        <div className="insight-list">
          {items.map((insight) => (
            <article
              className="insight-card"
              key={insight.id}
            >
              <div className="insight-card-header">
                <h3>{insight.title}</h3>

                <span>
                  {insight.severity}
                </span>
              </div>

              <p>{insight.description}</p>

              {insight.recommendation && (
                <p>
                  <strong>Recommendation:</strong>{" "}
                  {insight.recommendation}
                </p>
              )}
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default InsightPanel;