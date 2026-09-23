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
            @RequestParam(value = "datasetId", required = false) UUID datasetId
    ) {
        Dataset dataset = datasetId == null
                ? datasetService.uploadDataset(file)
                : datasetService.uploadDataset(file, datasetId);

        return ResponseEntity.ok(new DatasetResponse(dataset));
    }

    @GetMapping("/{id}")
    public ResponseEntity<DatasetResponse> getDatasetById(@PathVariable UUID id) {
        return ResponseEntity.ok(
                new DatasetResponse(datasetService.getDatasetById(id))
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
