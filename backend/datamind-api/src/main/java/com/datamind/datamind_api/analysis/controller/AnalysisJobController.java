package com.datamind.datamind_api.analysis.controller;


import com.datamind.datamind_api.analysis.dto.CreateAnalysisJobRequest;
import com.datamind.datamind_api.analysis.dto.AnalysisJobResponse;
import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;
import java.util.List;
import jakarta.validation.Valid;

@RestController
@RequestMapping("/api/analysis/jobs")
public class AnalysisJobController
{
    private final AnalysisJobService analysisJobService ;

    public AnalysisJobController(
            AnalysisJobService analysisJobService
    ){
        this.analysisJobService = analysisJobService;
    }

    @PostMapping
    public ResponseEntity<AnalysisJobResponse> createAnalysisJob(
           @Valid @RequestBody CreateAnalysisJobRequest request
            ){
        AnalysisJob analysisJob = analysisJobService.createAnalysisJob(
                request.getLogicalDatasetId(),
                request.getDatasetVersionId(),
                request.getAnalysisType(),
                request.getTargetColumn(),
                request.isEnableHyperparameterTuning(),
                request.getHypothesisTests()
        );

        return ResponseEntity
                .accepted()
                .body(
                new AnalysisJobResponse(analysisJob)
        );


    }

    @GetMapping("/{id}")
    public ResponseEntity<AnalysisJobResponse> getAnalysisJobById(
            @PathVariable UUID id
    ){
        AnalysisJob analysisJob =
                analysisJobService.getAnalysisJobById(id);

        return ResponseEntity.ok(
                new AnalysisJobResponse(analysisJob)
        );
    }

    @GetMapping
    public ResponseEntity<List<AnalysisJobResponse>> getAnalysisHistory(
            @RequestParam UUID logicalDatasetId,
            @RequestParam(required = false) UUID datasetVersionId,
            @RequestParam(required = false) AnalysisType analysisType,
            @RequestParam(required = false) AnalysisJobStatus status,
            @RequestParam(defaultValue = "50") int limit
    ) {
        List<AnalysisJobResponse> history = analysisJobService.getAnalysisHistory(
                        logicalDatasetId, datasetVersionId, analysisType, status, limit
                ).stream()
                .map(AnalysisJobResponse::new)
                .toList();
        return ResponseEntity.ok(history);
    }

}
