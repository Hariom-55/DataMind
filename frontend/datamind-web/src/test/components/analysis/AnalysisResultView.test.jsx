import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AnalysisResultView from "../../../components/analysis/AnalysisResultView";

describe("AnalysisResultView", () => {
  it("renders the aggregated analysis dashboard", () => {
    render(
      <AnalysisResultView
        analysisType="INSIGHT"
        result={{
          analysisType: "INSIGHT",
          result: {
            analysis: {
              eda: {
                overview: {
                  rowCount: 891,
                  columnCount: 2,
                  numericColumnCount: 1,
                  categoricalColumnCount: 1,
                },
              },
            },
            insights: {
              summary: {
                totalInsights: 3,
                high: 1,
                medium: 1,
                low: 1,
                info: 0,
              },
              insights: [],
            },
            visualizations: {
              visualizations: [],
            },
          },
        }}
      />,
    );

    expect(
      screen.getByRole("heading", { name: "Analysis Dashboard" }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", {
        name: "Dataset health & structure",
      }),
    ).toBeInTheDocument();

    expect(
      screen.getByRole("heading", { name: "Insights" }),
    ).toBeInTheDocument();

    expect(screen.getByText("891")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getAllByText("3").length).toBeGreaterThan(0);
  });

  it("renders an EDA-only result without empty insight or visualization panels", () => {
    render(
      <AnalysisResultView
        analysisType="EDA"
        result={{
          analysisType: "EDA",
          result: {
            overview: {
              rowCount: 10,
              columnCount: 3,
            },
            numericStatistics: {
              age: { mean: 22 },
            },
            categoricalStatistics: {
              department: { uniqueCount: 2 },
            },
          },
        }}
      />,
    );

    expect(screen.getByText("10")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "Insights" }),
    ).not.toBeInTheDocument();
    expect(
      screen.queryByRole("heading", { name: "Visualizations" }),
    ).not.toBeInTheDocument();
  });

  it("renders the empty state", () => {
    render(<AnalysisResultView />);

    expect(
      screen.getByText("No analysis result available."),
    ).toBeInTheDocument();
  });
});
