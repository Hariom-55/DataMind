import { useMemo, useState } from "react";

import VisualizationRenderer from "./VisualizationRenderer";

function VisualizationPanel({ result }) {
  const visualizations =
    Array.isArray(result?.visualizations?.visualizations)
      ? result.visualizations.visualizations
      : Array.isArray(result?.visualizations)
        ? result.visualizations
        : [];

  const [filter, setFilter] = useState("ALL");
  const [search, setSearch] = useState("");

  const types = useMemo(() => {
    const uniqueTypes = [
      ...new Set(
        visualizations
          .map((visualization) =>
            String(visualization.type || "")
              .toUpperCase(),
          )
          .filter(Boolean),
      ),
    ];

    return ["ALL", ...uniqueTypes];
  }, [visualizations]);

  const filteredVisualizations = useMemo(() => {
    const normalizedSearch =
      search.trim().toLowerCase();

    return visualizations.filter(
      (visualization) => {
        const type = String(
          visualization.type || "",
        ).toUpperCase();

        const matchesType =
          filter === "ALL" || type === filter;

        if (!matchesType) {
          return false;
        }

        if (!normalizedSearch) {
          return true;
        }

        const searchableText = [
          visualization.title,
          visualization.description,
          visualization.type,
        ]
          .filter(Boolean)
          .join(" ")
          .toLowerCase();

        return searchableText.includes(
          normalizedSearch,
        );
      },
    );
  }, [visualizations, filter, search]);

  return (
    <section className="visualization-panel">
      <div className="section-heading">
        <div>
          <span className="eyebrow">
            VISUAL ANALYTICS
          </span>

          <h2>Visualizations</h2>

          <p>
            Interactive representations generated from
            the analysis result.
          </p>
        </div>

        <div className="visualization-count">
          <strong>
            {visualizations.length}
          </strong>
          <span>visuals</span>
        </div>
      </div>

      {visualizations.length === 0 ? (
        <div className="empty-state">
          <strong>
            No visualizations were generated.
          </strong>

          <span>
            The selected analysis did not return
            visualization specifications.
          </span>
        </div>
      ) : (
        <>
          <div className="visualization-toolbar">
            <div className="visualization-filters">
              {types.map((type) => (
                <button
                  type="button"
                  key={type}
                  className={
                    filter === type
                      ? "visualization-filter active"
                      : "visualization-filter"
                  }
                  onClick={() =>
                    setFilter(type)
                  }
                >
                  {type}
                </button>
              ))}
            </div>

            <input
              className="visualization-search"
              value={search}
              onChange={(event) =>
                setSearch(event.target.value)
              }
              placeholder="Search visualizations..."
              aria-label="Search visualizations"
            />
          </div>

          {filteredVisualizations.length ===
          0 ? (
            <div className="empty-state">
              <strong>
                No matching visualizations
              </strong>

              <span>
                Try another type or search term.
              </span>
            </div>
          ) : (
            <div className="visualization-list">
              {filteredVisualizations.map(
                (visualization, index) => (
                  <article
                    className="visualization-card"
                    key={`${visualization.title}-${index}`}
                  >
                    <div className="visualization-card-header">
                      <div>
                        <span className="visualization-index">
                          VISUAL {index + 1}
                        </span>

                        <h3>
                          {visualization.title ||
                            "Untitled visualization"}
                        </h3>

                        {visualization.description && (
                          <p>
                            {
                              visualization.description
                            }
                          </p>
                        )}
                      </div>

                      <span className="visualization-type">
                        {visualization.type}
                      </span>
                    </div>

                    <VisualizationRenderer
                      visualization={
                        visualization
                      }
                    />
                  </article>
                ),
              )}
            </div>
          )}
        </>
      )}
    </section>
  );
}

export default VisualizationPanel;