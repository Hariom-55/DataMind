package com.datamind.datamind_api.dataset.controller;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningPreviewResponse;
import com.datamind.datamind_api.dataset.dto.ApplyDatasetCleaningRequest;
import com.datamind.datamind_api.dataset.dto.CleaningAssessmentResponse;
import com.datamind.datamind_api.dataset.dto.CleaningPreviewResponse;
import com.datamind.datamind_api.dataset.dto.DatasetCleaningResponse;
import com.datamind.datamind_api.dataset.dto.DatasetLineageResponse;
import com.datamind.datamind_api.dataset.dto.DatasetResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetCleaningExecution;
import com.datamind.datamind_api.dataset.service.DatasetCleaningOrchestrationService;
import com.datamind.datamind_api.dataset.service.DatasetLineageService;
import com.datamind.datamind_api.dataset.service.DatasetService;
import jakarta.validation.Valid;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;

import java.util.List;
import java.util.UUID;

@RestController
@RequestMapping("/api/datasets/{logicalDatasetId}/versions/{datasetVersionId}/cleaning")
public class DatasetCleaningController {
    private final DatasetService datasetService;
    private final DatasetCleaningOrchestrationService cleaningService;
    private final DatasetLineageService lineageService;

    public DatasetCleaningController(
            DatasetService datasetService,
            DatasetCleaningOrchestrationService cleaningService,
            DatasetLineageService lineageService
    ) {
        this.datasetService = datasetService;
        this.cleaningService = cleaningService;
        this.lineageService = lineageService;
    }

    @GetMapping("/recommendations")
    public ResponseEntity<CleaningAssessmentResponse> recommendations(
            @PathVariable UUID logicalDatasetId,
            @PathVariable UUID datasetVersionId
    ) {
        Dataset version = resolveVersion(logicalDatasetId, datasetVersionId);
        var assessment = cleaningService.assessDataset(version);
        return ResponseEntity.ok(new CleaningAssessmentResponse(
                assessment.totalRows(),
                assessment.totalColumns(),
                assessment.issueCount(),
                assessment.issues(),
                assessment.recommendations()
        ));
    }

    @PostMapping("/preview")
    public ResponseEntity<CleaningPreviewResponse> preview(
            @PathVariable UUID logicalDatasetId,
            @PathVariable UUID datasetVersionId,
            @Valid @RequestBody ApplyDatasetCleaningRequest request
    ) {
        Dataset version = resolveVersion(logicalDatasetId, datasetVersionId);
        PythonCleaningPreviewResponse preview = cleaningService.previewDataset(
                version, request.operations()
        );
        return ResponseEntity.ok(new CleaningPreviewResponse(
                logicalDatasetId,
                datasetVersionId,
                version.getVersionNumber(),
                preview.originalRows(),
                preview.cleanedRows(),
                preview.originalColumns(),
                preview.cleanedColumns(),
                preview.operationsApplied(),
                preview.changes()
        ));
    }

    @PostMapping
    public ResponseEntity<DatasetCleaningResponse> apply(
            @PathVariable UUID logicalDatasetId,
            @PathVariable UUID datasetVersionId,
            @Valid @RequestBody ApplyDatasetCleaningRequest request
    ) {
        Dataset parent = resolveVersion(logicalDatasetId, datasetVersionId);
        DatasetCleaningExecution execution = cleaningService.cleanDatasetWithResult(
                parent, request.operations()
        );
        Dataset child = execution.dataset();
        List<DatasetLineageResponse> lineage = lineageService.getLineage(child.getId());
        var result = execution.cleaningResult();

        return ResponseEntity.ok(new DatasetCleaningResponse(
                logicalDatasetId,
                datasetVersionId,
                parent.getVersionNumber(),
                result.original_rows(),
                result.cleaned_rows(),
                result.original_columns(),
                result.cleaned_columns(),
                result.operations_applied(),
                result.format(),
                result.extension(),
                result.content_type(),
                new DatasetResponse(child),
                result.changes(),
                lineage
        ));
    }

    private Dataset resolveVersion(UUID logicalDatasetId, UUID datasetVersionId) {
        Dataset logicalDataset = datasetService.getDatasetById(logicalDatasetId);
        UUID actualLogicalId = logicalDataset.getLogicalDatasetId() != null
                ? logicalDataset.getLogicalDatasetId()
                : logicalDataset.getId();
        Dataset version = datasetService.getDatasetById(datasetVersionId);
        if (!actualLogicalId.equals(version.getLogicalDatasetId())) {
            throw new IllegalArgumentException(
                    "datasetVersionId does not belong to logicalDatasetId"
            );
        }
        return version;
    }
}
