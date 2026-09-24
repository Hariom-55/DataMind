import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";
import BoxPlotVisualization from "../../../components/visualizations/BoxPlotVisualization";
import VisualizationRenderer from "../../../components/VisualizationRenderer";

describe("BoxPlotVisualization", () => {
  it("renders the five-number summary as a box plot", () => {
    render(<VisualizationRenderer visualization={{ type: "BOX_PLOT", title: "Age distribution", data: [{ column: "age", min: 1, q1: 3, median: 5, q3: 7, max: 9 }] }} />);

    expect(screen.getByRole("img", { name: /minimum 1, first quartile 3, median 5, third quartile 7, maximum 9/ })).toBeInTheDocument();
    expect(screen.getByText(/whiskers show observed minimum and maximum/)).toBeInTheDocument();
  });

  it("shows explicit empty and invalid states", () => {
    const { rerender } = render(<BoxPlotVisualization visualization={{ type: "BOX_PLOT", data: [] }} />);
    expect(screen.getByText("Invalid box plot data")).toBeInTheDocument();

    rerender(<BoxPlotVisualization visualization={{ type: "BOX_PLOT", data: [{ min: 5, q1: 4, median: 6, q3: 7, max: 9 }] }} />);
    expect(screen.getByText("Invalid box plot range")).toBeInTheDocument();
  });
});
