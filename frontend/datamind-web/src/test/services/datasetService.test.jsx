import { describe, expect, it, vi } from "vitest";
import { uploadDatasetFile } from "../../services/datasetService";
import { uploadDataset } from "../../api/datasetApi";

vi.mock("../../api/datasetApi", () => ({
  uploadDataset: vi.fn(),
}));

describe("datasetService", () => {
  it("uploads a valid file", async () => {
    const file = new File(["name,age\nJohn,22"], "users.csv", {
      type: "text/csv",
    });

    const dataset = {
      id: "dataset-123",
      name: "users.csv",
      status: "UPLOADED",
    };

    uploadDataset.mockResolvedValue(dataset);

    const result = await uploadDatasetFile(file);

    expect(uploadDataset).toHaveBeenCalledWith(file);
    expect(result).toEqual(dataset);
  });

  it("rejects when file is missing", async () => {
    await expect(uploadDatasetFile(null)).rejects.toThrow(
      "A valid file is required.",
    );

    expect(uploadDataset).not.toHaveBeenCalled();
  });

  it("rejects an empty file", async () => {
    const file = new File([], "empty.csv", {
      type: "text/csv",
    });

    await expect(uploadDatasetFile(file)).rejects.toThrow(
      "The selected file is empty.",
    );

    expect(uploadDataset).not.toHaveBeenCalled();
  });
});