package com.datamind.datamind_api.dataset.controller;

import com.datamind.datamind_api.dataset.dto.DatasetResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/datasets")
public class DatasetController {

    private final DatasetService datasetService;

    public DatasetController(DatasetService datasetService) {
        this.datasetService = datasetService;
    }

    @PostMapping(consumes = "multipart/form-data")
    public ResponseEntity<DatasetResponse> uploadDataset(
            @RequestParam("file") MultipartFile file,
            @RequestParam(value = "logicalDatasetId", required = false) UUID logicalDatasetId,
            @RequestParam(value = "datasetId", required = false) UUID legacyDatasetId
    ) {
        if (logicalDatasetId != null && legacyDatasetId != null
                && !logicalDatasetId.equals(legacyDatasetId)) {
            throw new IllegalArgumentException(
                    "logicalDatasetId and legacy datasetId must match when both are supplied"
            );
        }
        UUID requestedLogicalId = logicalDatasetId != null ? logicalDatasetId : legacyDatasetId;
        Dataset dataset = requestedLogicalId == null
                ? datasetService.uploadDataset(file)
                : datasetService.uploadDataset(file, requestedLogicalId);

        return ResponseEntity.ok(new DatasetResponse(dataset));
    }

    @GetMapping("/{datasetVersionId}")
    public ResponseEntity<DatasetResponse> getDatasetVersionById(
            @PathVariable UUID datasetVersionId
    ) {
        return ResponseEntity.ok(
                new DatasetResponse(datasetService.getDatasetById(datasetVersionId))
        );
    }

    @GetMapping("/{logicalDatasetId}/versions")
    public ResponseEntity<List<DatasetResponse>> getVersions(
            @PathVariable UUID logicalDatasetId
    ) {
        return ResponseEntity.ok(
                datasetService.getVersions(logicalDatasetId)
                        .stream()
                        .map(DatasetResponse::new)
                        .toList()
        );
    }

    @GetMapping("/{logicalDatasetId}/versions/{versionNumber}")
    public ResponseEntity<DatasetResponse> getVersion(
            @PathVariable UUID logicalDatasetId,
            @PathVariable int versionNumber
    ) {
        return ResponseEntity.ok(
                new DatasetResponse(
                        datasetService.getVersion(logicalDatasetId, versionNumber)
                )
        );
    }

    @GetMapping("/{logicalDatasetId}/current")
    public ResponseEntity<DatasetResponse> getCurrentVersion(
            @PathVariable UUID logicalDatasetId
    ) {
        return ResponseEntity.ok(
                new DatasetResponse(datasetService.getCurrentVersion(logicalDatasetId))
        );
    }

    @GetMapping
    public ResponseEntity<List<DatasetResponse>> getAllDatasets() {
        return ResponseEntity.ok(
                datasetService.getAllDatasets()
                        .stream()
                        .map(DatasetResponse::new)
                        .toList()
        );
    }
}
