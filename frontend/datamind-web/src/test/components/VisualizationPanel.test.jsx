import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import VisualizationPanel from "../../components/VisualizationPanel";

describe("VisualizationPanel", () => {
  it("renders all supplied visualization specifications", () => {
    const result = {
      visualizations: {
        visualizations: [
          {
            type: "BAR",
            title: "Missing Values by Column",
            description: "Missing value counts.",
            data: [
              {
                column: "age",
                missingCount: 5,
              },
            ],
            x: "column",
            y: "missingCount",
          },
          {
            type: "HEATMAP",
            title: "Pearson Correlation Matrix",
            description: "Pearson correlation.",
            data: [
              {
                row: "age",
                age: 1,
                salary: 0.82,
              },
              {
                row: "salary",
                age: 0.82,
                salary: 1,
              },
            ],
            metadata: {
              columns: ["age", "salary"],
            },
          },
          {
            type: "TABLE",
            title: "Distribution Analysis",
            description: "Distribution characteristics.",
            data: [
              {
                column: "age",
                sampleSize: 10,
                shape: "APPROXIMATELY_SYMMETRIC",
              },
            ],
          },
        ],
      },
    };

    render(<VisualizationPanel result={result} />);

    expect(
      screen.getByText("Visualizations"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Missing Values by Column"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Pearson Correlation Matrix"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("Distribution Analysis"),
    ).toBeInTheDocument();
  });

  it("renders a BAR visualization through the renderer", () => {
    const result = {
      visualizations: {
        visualizations: [
          {
            type: "BAR",
            title: "Class Distribution",
            data: [
              {
                class: "0",
                proportion: 0.5,
              },
            ],
            x: "class",
            y: "proportion",
          },
        ],
      },
    };

    render(<VisualizationPanel result={result} />);

    expect(
      screen.getByText("Class Distribution"),
    ).toBeInTheDocument();

    expect(
      document.querySelector(".chart-container"),
    ).toBeInTheDocument();
  });

  it("renders a HEATMAP visualization through the renderer", () => {
    const result = {
      visualizations: {
        visualizations: [
          {
            type: "HEATMAP",
            title: "Spearman Correlation Matrix",
            data: [
              {
                row: "age",
                age: 1,
                salary: 0.75,
              },
              {
                row: "salary",
                age: 0.75,
                salary: 1,
              },
            ],
            metadata: {
              columns: ["age", "salary"],
            },
          },
        ],
      },
    };

    render(<VisualizationPanel result={result} />);

    expect(
      screen.getByText("Spearman Correlation Matrix"),
    ).toBeInTheDocument();

    expect(
      document.querySelector(".heatmap-container"),
    ).toBeInTheDocument();

    expect(
      screen.getAllByText("0.75"),
    ).toHaveLength(2);
  });

  it("renders a TABLE visualization through the renderer", () => {
    const result = {
      visualizations: {
        visualizations: [
          {
            type: "TABLE",
            title: "Distribution Analysis",
            data: [
              {
                column: "salary",
                sampleSize: 20,
                shape: "RIGHT_SKEWED",
              },
            ],
          },
        ],
      },
    };

    render(<VisualizationPanel result={result} />);

    expect(
      screen.getByText("Distribution Analysis"),
    ).toBeInTheDocument();

    expect(
      document.querySelector(".table-container"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("RIGHT_SKEWED"),
    ).toBeInTheDocument();
  });

  it("handles an empty visualization collection", () => {
    const result = {
      visualizations: {
        visualizations: [],
      },
    };

    render(<VisualizationPanel result={result} />);

    expect(
      screen.getByText(
        "No visualizations were generated.",
      ),
    ).toBeInTheDocument();
  });

  it("handles a missing visualization collection", () => {
    const result = {};

    render(<VisualizationPanel result={result} />);

    expect(
      screen.getByText(
        "No visualizations were generated.",
      ),
    ).toBeInTheDocument();
  });
});