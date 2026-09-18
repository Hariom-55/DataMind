import VisualizationRenderer from "./VisualizationRenderer";

function VisualizationPanel({ result }) {
  const visualizations =
    result?.visualizations?.visualizations ?? [];

  return (
    <section className="visualization-panel">
      <h2>Visualizations</h2>

      {visualizations.length === 0 ? (
        <p>No visualizations were generated.</p>
      ) : (
        <div className="visualization-list">
          {visualizations.map((visualization, index) => (
            <article
              className="visualization-card"
              key={`${visualization.title}-${index}`}
            >
              <div className="visualization-card-header">
                <div>
                  <h3>{visualization.title}</h3>

                  {visualization.description && (
                    <p>{visualization.description}</p>
                  )}
                </div>

                <span>
                  {visualization.type}
                </span>
              </div>

              <VisualizationRenderer
                visualization={visualization}
              />
            </article>
          ))}
        </div>
      )}
    </section>
  );
}

export default VisualizationPanel;