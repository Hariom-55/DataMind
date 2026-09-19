import { useMemo, useState } from "react";

function InsightPanel({ result }) {
  const insights = result?.insights ?? {};
  const summary = insights.summary ?? {};
  const totalInsights =
    summary.total ?? summary.totalInsights ?? 0;

  const items = Array.isArray(insights.insights)
    ? insights.insights
    : [];

  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const filteredInsights = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return items.filter((insight) => {
      const matchesSeverity =
        filter === "ALL" ||
        String(insight.severity).toUpperCase() ===
          filter;

      if (!matchesSeverity) {
        return false;
      }

      if (!normalizedSearch) {
        return true;
      }

      const searchableText = [
        insight.title,
        insight.description,
        insight.recommendation,
      ]
        .filter(Boolean)
        .join(" ")
        .toLowerCase();

      return searchableText.includes(
        normalizedSearch,
      );
    });
  }, [items, filter, search]);

  return (
    <section className="insight-panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">
            INTELLIGENCE
          </span>

          <h2>Insights</h2>

          <p>
            Automatically detected observations and
            recommendations.
          </p>
        </div>

        <div className="insight-total">
          <strong>{totalInsights}</strong>
          <span>total insights</span>
        </div>
      </div>

      <div className="insight-summary">
        <button
          type="button"
          className={
            filter === "ALL"
              ? "insight-filter active"
              : "insight-filter"
          }
          onClick={() => setFilter("ALL")}
        >
          All
          <span>{totalInsights}</span>
        </button>

        <button
          type="button"
          className={
            filter === "HIGH"
              ? "insight-filter high active"
              : "insight-filter high"
          }
          onClick={() => setFilter("HIGH")}
        >
          High
          <span>{summary.high ?? 0}</span>
        </button>

        <button
          type="button"
          className={
            filter === "MEDIUM"
              ? "insight-filter medium active"
              : "insight-filter medium"
          }
          onClick={() => setFilter("MEDIUM")}
        >
          Medium
          <span>{summary.medium ?? 0}</span>
        </button>

        <button
          type="button"
          className={
            filter === "LOW"
              ? "insight-filter low active"
              : "insight-filter low"
          }
          onClick={() => setFilter("LOW")}
        >
          Low
          <span>{summary.low ?? 0}</span>
        </button>

        <button
          type="button"
          className={
            filter === "INFO"
              ? "insight-filter info active"
              : "insight-filter info"
          }
          onClick={() => setFilter("INFO")}
        >
          Info
          <span>{summary.info ?? 0}</span>
        </button>

        <input
          className="insight-search"
          value={search}
          onChange={(event) =>
            setSearch(event.target.value)
          }
          placeholder="Search insights..."
          aria-label="Search insights"
        />
      </div>

      {items.length === 0 ? (
        <div className="empty-state">
          <strong>No insights generated</strong>
          <span>
            DataMind did not detect any actionable
            observations for this analysis.
          </span>
        </div>
      ) : filteredInsights.length === 0 ? (
        <div className="empty-state">
          <strong>No matching insights</strong>
          <span>
            Try changing the severity filter or search
            term.
          </span>
        </div>
      ) : (
        <div className="insight-list">
          {filteredInsights.map(
            (insight, index) => {
              const severity =
                String(
                  insight.severity ?? "INFO",
                ).toLowerCase();

              return (
                <article
                  className={`insight-card severity-${severity}`}
                  key={
                    insight.id ??
                    `${insight.title}-${index}`
                  }
                >
                  <div className="insight-card-header">
                    <div>
                      <span className="insight-number">
                        INSIGHT {index + 1}
                      </span>

                      <h3>
                        {insight.title ||
                          "Untitled insight"}
                      </h3>
                    </div>

                    <span
                      className={`severity-badge ${severity}`}
                    >
                      {String(
                        insight.severity ?? "INFO",
                      )}
                    </span>
                  </div>

                  {insight.description && (
                    <p className="insight-description">
                      {insight.description}
                    </p>
                  )}

                  {insight.recommendation && (
                    <div className="recommendation">
                      <span>
                        RECOMMENDATION
                      </span>

                      <p>
                        {insight.recommendation}
                      </p>
                    </div>
                  )}
                </article>
              );
            },
          )}
        </div>
      )}
    </section>
  );
}

export default InsightPanel;