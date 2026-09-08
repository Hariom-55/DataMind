package com.datamind.datamind_api.dataset.controller;

import com.datamind.datamind_api.dataset.dto.DatasetLineageResponse;
import com.datamind.datamind_api.dataset.service.DatasetLineageService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/datasets")
public class DatasetLineageController {

    private final DatasetLineageService lineageService;

    public DatasetLineageController(
            DatasetLineageService lineageService
    ) {
        this.lineageService = lineageService;
    }

    @GetMapping("/{datasetId}/lineage")
    public ResponseEntity<List<DatasetLineageResponse>> getLineage(
            @PathVariable UUID datasetId
    ) {

        return ResponseEntity.ok(
                lineageService.getLineage(datasetId)
        );
    }
}