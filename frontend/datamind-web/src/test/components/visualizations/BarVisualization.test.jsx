import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import BarVisualization from "../../../components/visualizations/BarVisualization";

describe("BarVisualization", () => {
  it("renders a bar visualization with valid data", () => {
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
      <BarVisualization visualization={visualization} />,
    );

    expect(
      screen.queryByText(
        "No data available for this visualization.",
      ),
    ).not.toBeInTheDocument();

    expect(
      document.querySelector(".chart-container"),
    ).toBeInTheDocument();
  });

  it("handles empty data", () => {
    const visualization = {
      type: "BAR",
      title: "Missing Values",
      data: [],
      x: "column",
      y: "missingCount",
    };

    render(
      <BarVisualization visualization={visualization} />,
    );

    expect(
      screen.getByText(
        "No data available for this visualization.",
      ),
    ).toBeInTheDocument();
  });

  it("rejects rows without a configured numeric value", () => {
    render(<BarVisualization visualization={{ type: "BAR", data: [{ column: "age", missingCount: "many" }], x: "column", y: "missingCount" }} />);

    expect(screen.getByRole("alert")).toHaveTextContent("Invalid bar chart data");
  });
});
