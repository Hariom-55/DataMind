import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AnalysisHistory from "../../../components/analysis/AnalysisHistory";
import { getAnalysisHistory, getAnalysisResult } from "../../../api/analysisApi";

vi.mock("../../../api/analysisApi", () => ({
  getAnalysisHistory: vi.fn(),
  getAnalysisResult: vi.fn(),
}));

describe("AnalysisHistory", () => {
  beforeEach(() => {
    vi.clearAllMocks();
  });

  it("lists runs, filters by version, and reopens a completed result", async () => {
    const job = { id: "job-1", status: "COMPLETED", analysisType: "EDA", versionNumber: 2, createdAt: "2026-09-24T10:00:00" };
    const result = { contractVersion: "v1", analysisType: "EDA", result: { overview: {} } };
    getAnalysisHistory.mockResolvedValue([job]);
    getAnalysisResult.mockResolvedValue(result);
    const onOpen = vi.fn();

    render(
      <AnalysisHistory
        logicalDatasetId="logical-1"
        versions={[{ datasetVersionId: "version-2", versionNumber: 2 }]}
        onOpen={onOpen}
      />,
    );

    expect(await screen.findByText("EDA")).toBeInTheDocument();
    expect(screen.getByText("COMPLETED")).toBeInTheDocument();
    fireEvent.change(screen.getByLabelText("Version"), { target: { value: "version-2" } });
    await waitFor(() => expect(getAnalysisHistory).toHaveBeenLastCalledWith({
      logicalDatasetId: "logical-1",
      datasetVersionId: "version-2",
      analysisType: "",
      status: "",
    }));

    fireEvent.click(screen.getByRole("button", { name: "Open result" }));
    await waitFor(() => expect(onOpen).toHaveBeenCalledWith(job, result));
    expect(getAnalysisResult).toHaveBeenCalledWith("job-1");
  });
});
