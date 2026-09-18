import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import HeatmapVisualization from "../../../components/visualizations/HeatmapVisualization";

describe("HeatmapVisualization", () => {
  it("renders correlation matrix headers and values", () => {
    const visualization = {
      type: "HEATMAP",
      title: "Pearson Correlation Matrix",
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
    };

    render(
      <HeatmapVisualization
        visualization={visualization}
      />,
    );

    expect(
      screen.getAllByText("age"),
    ).toHaveLength(2);

    expect(
      screen.getAllByText("salary"),
    ).toHaveLength(2);

    expect(
      screen.getAllByText("0.82"),
    ).toHaveLength(2);

    expect(
      screen.getAllByText("1.00"),
    ).toHaveLength(2);
  });

  it("handles empty data", () => {
    const visualization = {
      type: "HEATMAP",
      title: "Correlation Matrix",
      data: [],
      metadata: {
        columns: ["age", "salary"],
      },
    };

    render(
      <HeatmapVisualization
        visualization={visualization}
      />,
    );

    expect(
      screen.getByText(
        "No data available for this visualization.",
      ),
    ).toBeInTheDocument();
  });

  it("handles missing columns metadata", () => {
    const visualization = {
      type: "HEATMAP",
      title: "Correlation Matrix",
      data: [
        {
          row: "age",
          age: 1,
        },
      ],
      metadata: {},
    };

    render(
      <HeatmapVisualization
        visualization={visualization}
      />,
    );

    expect(
      screen.getByText(
        "No data available for this visualization.",
      ),
    ).toBeInTheDocument();
  });
});