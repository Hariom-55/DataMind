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
});