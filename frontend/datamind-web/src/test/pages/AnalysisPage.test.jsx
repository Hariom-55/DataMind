import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import AnalysisPage from "../../pages/AnalysisPage";
import { getCurrentDatasetVersion, getDatasetLineage, getDatasetVersions } from "../../api/datasetApi";
import { useAnalysis } from "../../services/useAnalysis";
import { getAnalysisHistory } from "../../api/analysisApi";

vi.mock("../../api/datasetApi", () => ({
  getCurrentDatasetVersion: vi.fn(),
  getDatasetLineage: vi.fn(),
  getDatasetVersions: vi.fn(),
}));

vi.mock("../../services/useAnalysis", () => ({ useAnalysis: vi.fn() }));
vi.mock("../../api/analysisApi", () => ({ getAnalysisHistory: vi.fn() }));
vi.mock("../../components/dataset/DatasetUpload", () => ({
  default: ({ onUploadSuccess }) => <button onClick={() => onUploadSuccess({ logicalDatasetId: "logical-1", datasetVersionId: "version-2", versionNumber: 2, name: "sales.csv", fileType: "text/csv", status: "UPLOADED" })}>Mock upload</button>,
}));
vi.mock("../../components/dataset/CleaningWorkflowPanel", () => ({ default: () => null }));
vi.mock("../../components/analysis/AnalysisHistory", () => ({ default: () => null }));
vi.mock("../../components/analysis/AnalysisResultView", () => ({ default: () => null }));

describe("AnalysisPage version pinning", () => {
  const startAnalysis = vi.fn();
  const resetAnalysis = vi.fn();

  beforeEach(() => {
    vi.clearAllMocks();
    window.localStorage.clear();
    useAnalysis.mockReturnValue({ state: "IDLE", job: null, result: null, error: null, startAnalysis, resetAnalysis, resumeAnalysisJob: vi.fn(), openHistoricalAnalysis: vi.fn() });
    getDatasetVersions.mockResolvedValue([
      { datasetVersionId: "version-1", versionNumber: 1 },
      { datasetVersionId: "version-2", versionNumber: 2 },
    ]);
    getCurrentDatasetVersion.mockResolvedValue({ datasetVersionId: "version-2", versionNumber: 2 });
    getDatasetLineage.mockResolvedValue([]);
    getAnalysisHistory.mockResolvedValue([]);
  });

  it("runs against the selected version using the canonical logical dataset ID", async () => {
    render(<AnalysisPage />);
    fireEvent.click(screen.getByRole("button", { name: "Mock upload" }));

    const selector = await screen.findByLabelText("Version history");
    await waitFor(() => expect(selector).toHaveValue("version-2"));
    fireEvent.change(selector, { target: { value: "version-1" } });
    fireEvent.click(screen.getByRole("button", { name: "Run analysis" }));

    expect(startAnalysis).toHaveBeenCalledWith({
      logicalDatasetId: "logical-1",
      datasetVersionId: "version-1",
      analysisType: "INSIGHT",
      targetColumn: null,
      enableHyperparameterTuning: false,
    });
  });

  it("sends hyperparameter tuning only when explicitly enabled", async () => {
    render(<AnalysisPage />);
    fireEvent.click(screen.getByRole("button", { name: "Mock upload" }));
    await screen.findByLabelText("Version history");
    fireEvent.change(screen.getByLabelText("Analysis type"), {
      target: { value: "MACHINE_LEARNING" },
    });
    fireEvent.change(screen.getByLabelText("Target column"), {
      target: { value: "profit" },
    });
    fireEvent.click(screen.getByLabelText("Enable random forest hyperparameter tuning"));
    fireEvent.click(screen.getByRole("button", { name: "Run analysis" }));

    expect(startAnalysis).toHaveBeenCalledWith(expect.objectContaining({
      targetColumn: "profit",
      enableHyperparameterTuning: true,
    }));
  });

  it("restores the saved dataset and latest active job after refresh", async () => {
    const resumeAnalysisJob = vi.fn();
    useAnalysis.mockReturnValue({ state: "IDLE", job: null, result: null, error: null, startAnalysis, resetAnalysis, resumeAnalysisJob, openHistoricalAnalysis: vi.fn() });
    window.localStorage.setItem("datamind.activeLogicalDatasetId", "logical-1");
    getAnalysisHistory.mockImplementation(({ status }) => Promise.resolve(
      status === "PROCESSING" ? [{ id: "job-active", status: "PROCESSING" }] : [],
    ));
    getCurrentDatasetVersion.mockResolvedValue({ logicalDatasetId: "logical-1", datasetVersionId: "version-2", versionNumber: 2, name: "sales.csv", status: "COMPLETED" });

    render(<AnalysisPage />);

    expect(await screen.findByText("sales.csv")).toBeInTheDocument();
    await waitFor(() => expect(resumeAnalysisJob).toHaveBeenCalledWith({ id: "job-active", status: "PROCESSING" }));
  });

  it("includes configured statistical hypothesis tests in the job request", async () => {
    render(<AnalysisPage />);
    fireEvent.click(screen.getByRole("button", { name: "Mock upload" }));
    await screen.findByLabelText("Version history");
    fireEvent.change(screen.getByLabelText("Analysis type"), { target: { value: "STATISTICAL" } });
    fireEvent.change(screen.getByLabelText("Optional hypothesis test"), { target: { value: "ONE_SAMPLE_T_TEST" } });
    fireEvent.change(screen.getByLabelText("Numeric column"), { target: { value: "age" } });
    fireEvent.change(screen.getByLabelText("Reference mean"), { target: { value: "25" } });
    fireEvent.click(screen.getByRole("button", { name: "Run analysis" }));

    await waitFor(() => expect(startAnalysis).toHaveBeenCalledWith(expect.objectContaining({
      hypothesisTests: [{ test: "ONE_SAMPLE_T_TEST", alpha: 0.05, column: "age", referenceValue: 25 }],
    })));
  });
});
