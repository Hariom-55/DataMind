package com.datamind.datamind_api.analysis.controller;


import com.datamind.datamind_api.analysis.dto.CreateAnalysisJobRequest;
import com.datamind.datamind_api.analysis.dto.AnalysisJobResponse;
import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.*;
import java.util.UUID;
import jakarta.validation.Valid;

@RestController
@RequestMapping("api/analysis/jobs")
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
                request.getDatasetId(),
                request.getAnalysisType()
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

}
