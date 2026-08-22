package com.datamind.datamind_api.dataset.controller;

import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;
import java.util.stream.Collectors;

import com.datamind.datamind_api.dataset.dto.DatasetCreateRequest;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import com.datamind.datamind_api.dataset.dto.DatasetResponse;

@RestController
@RequestMapping("/api/datasets")
public class DatasetController {

    private final DatasetService datasetService;

    public DatasetController(DatasetService datasetService){
        this.datasetService = datasetService ;
    }

    @PostMapping
    public ResponseEntity<DatasetResponse> createDataset(
        @RequestBody DatasetCreateRequest request) {

            Dataset dataset = datasetService.createDataset(
                request.getName(),
                request.getContentHash(),
                request.getFileSize(),
                request.getFileType()
            );

            return ResponseEntity.ok(new DatasetResponse(dataset));
        }

    @GetMapping("/{id}")
    public Dataset getDatasetById(@PathVariable UUID id)
    {
        return datasetService.getDatasetById(id);
    }

    @GetMapping
    public ResponseEntity<List<DatasetResponse>> getAllDatasets()
    {
        List<Dataset> datasets = datasetService.getAllDatasets();

        List<DatasetResponse> response = datasets.stream()
                .map(DatasetResponse :: new)
                .collect(Collectors.toList());

        return ResponseEntity.ok(response);
    }
}
