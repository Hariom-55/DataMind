import { fireEvent, render, screen, waitFor } from "@testing-library/react";
import { describe, expect, it, vi } from "vitest";
import DatasetUpload from "../../../components/dataset/DatasetUpload";
import { uploadDatasetFile } from "../../../services/datasetService";

vi.mock("../../../services/datasetService", () => ({
  uploadDatasetFile: vi.fn(),
}));

describe("DatasetUpload", () => {
  it("renders the upload interface", () => {
    render(<DatasetUpload />);

    expect(screen.getByRole("heading", {name:"Upload Dataset"})).toBeInTheDocument();
    expect(screen.getByRole("button", { name: "Upload Dataset" })).toBeDisabled();
  });

  it("allows a file to be selected", () => {
    render(<DatasetUpload />);

    const file = new File(["name,age"], "users.csv", {
      type: "text/csv",
    });

    fireEvent.change(screen.getByLabelText("Dataset file"), {
      target: { files: [file] },
    });

    expect(screen.getByText("Selected file: users.csv")).toBeInTheDocument();
    expect(
      screen.getByRole("button", { name: "Upload Dataset" }),
    ).toBeEnabled();
  });

  it("uploads the selected file successfully", async () => {
    const uploadedDataset = {
      id: "dataset-123",
      name: "users.csv",
      status: "UPLOADED",
    };

    uploadDatasetFile.mockResolvedValue(uploadedDataset);

    const onUploadSuccess = vi.fn();

    render(<DatasetUpload onUploadSuccess={onUploadSuccess} />);

    const file = new File(["name,age"], "users.csv", {
      type: "text/csv",
    });

    fireEvent.change(screen.getByLabelText("Dataset file"), {
      target: { files: [file] },
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Upload Dataset" }),
    );

    expect(screen.getByRole("button", { name: "Uploading..." })).toBeDisabled();

    await waitFor(() => {
      expect(
        screen.getByRole("status"),
      ).toHaveTextContent("dataset-123");
    });

    expect(uploadDatasetFile).toHaveBeenCalledWith(file);
    expect(onUploadSuccess).toHaveBeenCalledWith(uploadedDataset);
  });

  it("displays an upload error", async () => {
    uploadDatasetFile.mockRejectedValue(
      new Error("Upload failed"),
    );

    render(<DatasetUpload />);

    const file = new File(["invalid"], "data.csv", {
      type: "text/csv",
    });

    fireEvent.change(screen.getByLabelText("Dataset file"), {
      target: { files: [file] },
    });

    fireEvent.click(
      screen.getByRole("button", { name: "Upload Dataset" }),
    );

    await waitFor(() => {
      expect(screen.getByRole("alert")).toHaveTextContent("Upload failed");
    });
  });
});