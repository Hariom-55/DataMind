import { fireEvent, render, screen } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DatasetWorkspace from "../../../components/dataset/DatasetWorkspace";

vi.mock("../../../components/dataset/CleaningWorkflowPanel", () => ({
  default: () => <div>Cleaning actions</div>,
}));

describe("DatasetWorkspace", () => {
  it("shows dataset identity, version metadata, and cleaning lineage", () => {
    render(
      <DatasetWorkspace
        dataset={{ logicalDatasetId: "logical-1", name: "sales.csv", fileType: "text/csv", status: "UPLOADED" }}
        versions={[{ datasetVersionId: "version-2", versionNumber: 2, fileSize: 128, fileType: "text/csv", status: "COMPLETED", createdAt: "2026-09-24T10:00:00" }]}
        selectedVersion={{ datasetVersionId: "version-2", versionNumber: 2, fileSize: 128, fileType: "text/csv", status: "COMPLETED", createdAt: "2026-09-24T10:00:00" }}
        selectedVersionId="version-2"
        currentVersionId="version-2"
        lineage={[{ operation: "DROP_DUPLICATES", details: "Removed 2 duplicate rows", datasetVersionId: "version-2", operationConfig: [{ operation: "IMPUTE_MISSING_VALUES", column: "age", parameters: { strategy: "MEAN" } }] }]}
        onVersionChange={vi.fn()}
        onChooseAnother={vi.fn()}
      />,
    );

    expect(screen.getByText("logical-1")).toBeInTheDocument();
    expect(screen.getByText("version-2")).toBeInTheDocument();
    expect(screen.getByText("128 bytes")).toBeInTheDocument();
    expect(screen.getByText("DROP_DUPLICATES")).toBeInTheDocument();
    expect(screen.getByText(/"strategy": "MEAN"/)).toBeInTheDocument();
    expect(screen.getByText("Cleaning actions")).toBeInTheDocument();
  });

  it("notifies when the selected dataset version changes", () => {
    const onVersionChange = vi.fn();
    render(
      <DatasetWorkspace
        dataset={{ logicalDatasetId: "logical-1", name: "sales.csv" }}
        versions={[{ datasetVersionId: "version-1", versionNumber: 1 }, { datasetVersionId: "version-2", versionNumber: 2 }]}
        selectedVersion={{ datasetVersionId: "version-1", versionNumber: 1 }}
        selectedVersionId="version-1"
        currentVersionId="version-2"
        lineage={[]}
        onVersionChange={onVersionChange}
        onChooseAnother={vi.fn()}
      />,
    );

    fireEvent.change(screen.getByLabelText("Version history"), { target: { value: "version-2" } });
    expect(onVersionChange).toHaveBeenCalledWith("version-2");
  });
});
