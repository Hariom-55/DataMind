import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { beforeEach, describe, expect, it, vi } from "vitest";
import CleaningWorkflowPanel from "../../../components/dataset/CleaningWorkflowPanel";
import {
  applyDatasetCleaning,
  getCleaningRecommendations,
  previewDatasetCleaning,
} from "../../../api/datasetApi";

vi.mock("../../../api/datasetApi", () => ({
  applyDatasetCleaning: vi.fn(),
  getCleaningRecommendations: vi.fn(),
  previewDatasetCleaning: vi.fn(),
}));

const version = { datasetVersionId: "version-7", versionNumber: 7 };

describe("CleaningWorkflowPanel", () => {
  beforeEach(() => vi.clearAllMocks());

  it("assesses and previews changes against the selected version", async () => {
    getCleaningRecommendations.mockResolvedValue({
      totalRows: 3,
      totalColumns: 2,
      issueCount: 1,
      recommendations: [{ operation: "REMOVE_DUPLICATES", issueType: "Duplicate rows", recommendation: "Remove repeated rows" }],
    });
    previewDatasetCleaning.mockResolvedValue({
      versionNumber: 7,
      originalRows: 3,
      cleanedRows: 2,
      originalColumns: 2,
      cleanedColumns: 2,
      changes: [],
    });

    render(<CleaningWorkflowPanel logicalDatasetId="logical-1" datasetVersion={version} />);
    fireEvent.click(screen.getByRole("button", { name: "Get recommendations" }));

    await screen.findByText("Duplicate rows");
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Preview selected changes" }));

    await screen.findByText("Rows: 3 → 2 · Columns: 2 → 2");
    expect(getCleaningRecommendations).toHaveBeenCalledWith("logical-1", "version-7");
    expect(previewDatasetCleaning).toHaveBeenCalledWith("logical-1", "version-7", [
      { operation: "REMOVE_DUPLICATES", column: null, parameters: {} },
    ]);
    expect(applyDatasetCleaning).not.toHaveBeenCalled();
  });

  it("applies reviewed operations and reports the created version", async () => {
    getCleaningRecommendations.mockResolvedValue({
      totalRows: 3,
      totalColumns: 2,
      issueCount: 1,
      recommendations: [{ operation: "REMOVE_DUPLICATES", issueType: "Duplicate rows", recommendation: "Remove repeated rows" }],
    });
    previewDatasetCleaning.mockResolvedValue({ versionNumber: 7, originalRows: 3, cleanedRows: 2, originalColumns: 2, cleanedColumns: 2, changes: [] });
    applyDatasetCleaning.mockResolvedValue({ dataset: { datasetVersionId: "version-8", versionNumber: 8 } });
    const onVersionCreated = vi.fn();

    render(<CleaningWorkflowPanel logicalDatasetId="logical-1" datasetVersion={version} onVersionCreated={onVersionCreated} />);
    fireEvent.click(screen.getByRole("button", { name: "Get recommendations" }));
    await screen.findByText("Duplicate rows");
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.click(screen.getByRole("button", { name: "Preview selected changes" }));
    await screen.findByText("Rows: 3 → 2 · Columns: 2 → 2");
    fireEvent.click(screen.getByRole("button", { name: "Apply and create new version" }));

    await waitFor(() => expect(onVersionCreated).toHaveBeenCalledWith({ datasetVersionId: "version-8", versionNumber: 8 }));
    expect(applyDatasetCleaning).toHaveBeenCalledWith("logical-1", "version-7", [
      { operation: "REMOVE_DUPLICATES", column: null, parameters: {} },
    ]);
    expect(screen.getByRole("status")).toHaveTextContent("Cleaned version created");
  });

  it("sends the selected imputation strategy as operation parameters", async () => {
    getCleaningRecommendations.mockResolvedValue({
      totalRows: 3,
      totalColumns: 1,
      issueCount: 1,
      recommendations: [{ operation: "IMPUTE_MISSING_VALUES", column: "age", issueType: "Missing values", recommendation: "Impute missing values" }],
    });
    previewDatasetCleaning.mockResolvedValue({ versionNumber: 7, originalRows: 3, cleanedRows: 3, originalColumns: 1, cleanedColumns: 1, changes: [] });

    render(<CleaningWorkflowPanel logicalDatasetId="logical-1" datasetVersion={version} />);
    fireEvent.click(screen.getByRole("button", { name: "Get recommendations" }));
    await screen.findByText(/Missing values/);
    fireEvent.click(screen.getByRole("checkbox"));
    fireEvent.change(screen.getByLabelText("Imputation strategy"), { target: { value: "MEAN" } });
    fireEvent.click(screen.getByRole("button", { name: "Preview selected changes" }));

    await waitFor(() => expect(previewDatasetCleaning).toHaveBeenCalledWith("logical-1", "version-7", [
      { operation: "IMPUTE_MISSING_VALUES", column: "age", parameters: { strategy: "MEAN" } },
    ]));
  });
});
