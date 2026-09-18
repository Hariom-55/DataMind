import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import AnalysisResultView from "../../../components/analysis/AnalysisResultView";

describe("AnalysisResultView", () => {
  it("renders the analysis result", () => {
    render(
        <AnalysisResultView
        result={{
            result: {
            analysis: {
                eda: {
                overview: {
                    rowCount: 891,
                    columnCount: 2,
                },
                },
            },
            insights: {
                summary: {
                total: 3,
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
        screen.getByRole("heading", { name: "Analysis Result" }),
    ).toBeInTheDocument();

    expect(
        screen.getByRole("heading", { name: "Analysis Summary" }),
    ).toBeInTheDocument();

    expect(screen.getByText("891")).toBeInTheDocument();
    expect(screen.getByText("2")).toBeInTheDocument();
    expect(screen.getByText("3")).toBeInTheDocument();
  });

  it("renders the empty state", () => {
    render(<AnalysisResultView />);

    expect(
      screen.getByText("No analysis result available."),
    ).toBeInTheDocument();
  });
});