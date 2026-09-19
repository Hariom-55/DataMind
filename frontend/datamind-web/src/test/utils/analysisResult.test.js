import { describe, expect, it } from "vitest";
import { normalizeAnalysisResult } from "../../utils/analysisResult";

describe("normalizeAnalysisResult", () => {
  it("unwraps the Spring Boot AnalysisResultResponse", () => {
    const payload = {
      analysis: {},
      insights: {},
      visualizations: {},
    };

    expect(
      normalizeAnalysisResult({ result: payload }),
    ).toBe(payload);
  });

  it("unwraps nested result wrappers", () => {
    const payload = {
      analysis: { eda: {} },
      insights: {},
      visualizations: {},
    };

    expect(
      normalizeAnalysisResult({
        result: {
          status: "COMPLETED",
          result: payload,
        },
      }),
    ).toBe(payload);
  });

  it("returns direct EDA results", () => {
    const payload = {
      overview: { rowCount: 10, columnCount: 2 },
    };

    expect(normalizeAnalysisResult(payload)).toBe(payload);
  });

  it("rejects non-object responses", () => {
    expect(normalizeAnalysisResult(null)).toBeNull();
    expect(normalizeAnalysisResult([])).toBeNull();
  });
});
