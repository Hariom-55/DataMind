import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import VisualizationRenderer from "../../components/VisualizationRenderer";

describe("VisualizationRenderer", () => {
  it("renders a bar visualization", () => {
    const visualization = {
      type: "BAR",
      title: "Missing Values",
      data: [
        {
          column: "age",
          missingCount: 5,
        },
      ],
      x: "column",
      y: "missingCount",
    };

    render(
      <VisualizationRenderer
        visualization={visualization}
      />,
    );

    expect(
      screen.queryByText(
        "No data available for this visualization.",
      ),
    ).not.toBeInTheDocument();
  });

  it("renders a heatmap visualization", () => {
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
      <VisualizationRenderer
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
  });

  it("renders a table visualization", () => {
    const visualization = {
      type: "TABLE",
      title: "Distribution Analysis",
      data: [
        {
          column: "age",
          sampleSize: 10,
          shape: "APPROXIMATELY_SYMMETRIC",
        },
      ],
    };

    render(
      <VisualizationRenderer
        visualization={visualization}
      />,
    );

    expect(
      screen.getByText("column"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("sampleSize"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("age"),
    ).toBeInTheDocument();
  });

  it.each(["LINE", "SCATTER", "HISTOGRAM", "PIE"])("selects a chart renderer for %s", (type) => {
    const data = type === "SCATTER"
      ? [{ x: 1, y: 2 }]
      : [{ category: "a", value: 2 }];
    const { container } = render(<VisualizationRenderer visualization={{ type, data, x: type === "SCATTER" ? "x" : "category", y: type === "SCATTER" ? "y" : "value" }} />);

    expect(container.querySelector(".chart-container")).toBeInTheDocument();
  });

  it("rejects malformed numeric chart data", () => {
    render(<VisualizationRenderer visualization={{ type: "LINE", data: [{ category: "a", value: "bad" }], x: "category", y: "value" }} />);

    expect(screen.getByRole("alert")).toHaveTextContent("Invalid line chart data");
  });

  it("shows a useful empty state for charts with no rows", () => {
    render(<VisualizationRenderer visualization={{ type: "HISTOGRAM", data: [], x: "bin", y: "count" }} />);

    expect(screen.getByText("No chart data")).toBeInTheDocument();
  });

  it("handles an unsupported visualization type", () => {
    const visualization = {
      type: "UNKNOWN",
      title: "Unknown Visualization",
      data: [],
    };

    render(
      <VisualizationRenderer
        visualization={visualization}
      />,
    );

    expect(
      screen.getByText("UNKNOWN"),
    ).toBeInTheDocument();
  });

  it("handles a missing visualization", () => {
    const { container } = render(
      <VisualizationRenderer visualization={null} />,
    );

    expect(container.firstChild).toBeNull();
  });
});
