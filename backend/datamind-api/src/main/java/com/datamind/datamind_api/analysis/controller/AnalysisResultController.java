package com.datamind.datamind_api.analysis.controller;


import com.datamind.datamind_api.analysis.dto.AnalysisResultResponse;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.service.AnalysisResultService;
import org.springframework.http.ResponseEntity;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.PathVariable;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.UUID;

@RestController
@RequestMapping("/api/analysis/jobs")
public class AnalysisResultController
{
    private final AnalysisResultService analysisResultService;

    public AnalysisResultController (
            AnalysisResultService analysisResultService
    ){
        this.analysisResultService = analysisResultService;
    }

    @GetMapping("/{jobId}/result")
    public ResponseEntity<AnalysisResultResponse> getAnalysisResult(
            @PathVariable UUID jobId
            ){
        AnalysisResult analysisResult =
                analysisResultService.getResultByJobId(jobId);

        return ResponseEntity.ok(
                new AnalysisResultResponse(analysisResult)
        );
    }
}
