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

  it("unwraps the canonical result field without inspecting payload keys", () => {
    const payload = {
      overview: { rowCount: 10 },
    };

    expect(
      normalizeAnalysisResult({ contractVersion: "v1", result: payload }),
    ).toBe(payload);
  });

  it("reads the frozen v1 result envelope", () => {
    const payload = { overview: { rowCount: 10, columnCount: 2 } };
    const envelope = {
      contractVersion: "v1",
      jobId: "job-1",
      logicalDatasetId: "dataset-1",
      datasetVersionId: "version-2",
      versionNumber: 2,
      analysisType: "EDA",
      status: "COMPLETED",
      result: payload,
    };

    expect(normalizeAnalysisResult(envelope)).toBe(payload);
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
