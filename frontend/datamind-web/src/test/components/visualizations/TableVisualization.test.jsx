import { render, screen } from "@testing-library/react";
import { describe, expect, it } from "vitest";

import TableVisualization from "../../../components/visualizations/TableVisualization";

describe("TableVisualization", () => {
  it("renders table headers and rows", () => {
    const visualization = {
      type: "TABLE",
      title: "Distribution Analysis",
      data: [
        {
          column: "age",
          sampleSize: 10,
          shape: "APPROXIMATELY_SYMMETRIC",
        },
        {
          column: "salary",
          sampleSize: 10,
          shape: "RIGHT_SKEWED",
        },
      ],
    };

    render(
      <TableVisualization
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
      screen.getByText("shape"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("age"),
    ).toBeInTheDocument();

    expect(
      screen.getByText("salary"),
    ).toBeInTheDocument();

    expect(
      screen.getAllByText("10"),
    ).toHaveLength(2);

    expect(
      screen.getByText("RIGHT_SKEWED"),
    ).toBeInTheDocument();
  });

  it("renders null and undefined values as an em dash", () => {
    const visualization = {
      type: "TABLE",
      title: "Distribution Analysis",
      data: [
        {
          column: "age",
          sampleSize: null,
          shape: undefined,
        },
      ],
    };

    render(
      <TableVisualization
        visualization={visualization}
      />,
    );

    expect(
      screen.getByText("age"),
    ).toBeInTheDocument();

    expect(
      screen.getAllByText("—"),
    ).toHaveLength(2);
  });

  it("handles empty data", () => {
    const visualization = {
      type: "TABLE",
      title: "Distribution Analysis",
      data: [],
    };

    render(
      <TableVisualization
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