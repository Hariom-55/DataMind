import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AnalysisDashboardRouter from "../../../components/analysis/AnalysisDashboardRouter";

describe("AnalysisDashboardRouter", () => {
  it("routes EDA results to the EDA dashboard", () => {
    render(
      <AnalysisDashboardRouter
        analysisType="EDA"
        result={{
          overview: {
            rowCount: 10,
            columnCount: 3,
            numericColumnCount: 2,
            categoricalColumnCount: 1,
          },
          schema: [],
          outlierSignals: {},
          visualizations: { visualizations: [] },
        }}
      />,
    );

    expect(screen.getByText("Quality diagnostics")).toBeInTheDocument();
    expect(screen.getByText("Columns with outlier signals")).toBeInTheDocument();
  });

  it("routes statistical results to the statistical dashboard", () => {
    render(
      <AnalysisDashboardRouter
        analysisType="STATISTICAL"
        result={{
          sampleSize: 10,
          numericColumnCount: 2,
          descriptiveStatistics: {},
          correlations: { pearson: {}, spearman: {} },
          visualizations: { visualizations: [] },
        }}
      />,
    );

    expect(screen.getByRole("heading", { name: "Descriptive statistics" })).toBeInTheDocument();
  });

  it("routes ML results to the ML dashboard", () => {
    render(
      <AnalysisDashboardRouter
        analysisType="MACHINE_LEARNING"
        result={{
          problemType: "CLASSIFICATION",
          training: { metrics: {}, featureImportance: [] },
          visualizations: { visualizations: [] },
        }}
      />,
    );

    expect(screen.getByText("PROBLEM TYPE")).toBeInTheDocument();
  });

  it("shows an explicit unsupported state for unknown analysis types", () => {
    render(<AnalysisDashboardRouter analysisType="FUTURE_TYPE" result={{}} />);

    expect(screen.getByRole("alert")).toHaveTextContent("Unsupported analysis type.");
    expect(screen.getByRole("alert")).toHaveTextContent("FUTURE_TYPE");
  });
});
