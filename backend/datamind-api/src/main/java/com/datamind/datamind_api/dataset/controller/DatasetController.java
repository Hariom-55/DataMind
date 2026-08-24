package com.datamind.datamind_api.dataset.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import com.datamind.datamind_api.dataset.dto.DatasetResponse;
import org.springframework.web.multipart.MultipartFile;

@RestController
@RequestMapping("/api/datasets")
public class DatasetController {

    private final DatasetService datasetService;

    public DatasetController(DatasetService datasetService){
        this.datasetService = datasetService;
    }

    @PostMapping(consumes = "multipart/form-data")
    public ResponseEntity<DatasetResponse> uploadDataset(
            @RequestParam("file") MultipartFile file
    ) {
        Dataset dataset = datasetService.uploadDataset(file);

        return ResponseEntity.ok(new DatasetResponse(dataset));
    }

    @GetMapping("/{id}")
    public ResponseEntity<DatasetResponse> getDatasetById(@PathVariable UUID id)
    {
        Dataset dataset = datasetService.getDatasetById(id);

        return ResponseEntity.ok(new DatasetResponse(dataset));
    }

    @GetMapping
    public ResponseEntity<List<DatasetResponse>> getAllDatasets()
    {
        List<Dataset> datasets = datasetService.getAllDatasets();

        List<DatasetResponse> response = datasets.stream()
                .map(DatasetResponse::new)
                .collect(Collectors.toList());

        return ResponseEntity.ok(response);
    }
}
