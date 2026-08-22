package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.springframework.stereotype.Service;

import java.util.UUID;

@Service
public class AnalysisJobService
{
    private final AnalysisJobRepository analysisJobRepository;
    private final DatasetService datasetService;

    public AnalysisJobService(
            AnalysisJobRepository analysisJobRepository,
            DatasetService datasetService
    ){
        this.analysisJobRepository = analysisJobRepository;
        this.datasetService = datasetService;
    }

    public AnalysisJob createAnalysisJob(
            java.util.UUID datasetId,
            AnalysisType analysisType
    ){
        Dataset dataset = datasetService.getDatasetById(datasetId);

        AnalysisJob analysisJob =new AnalysisJob(
                dataset,
                analysisType,
                AnalysisJobStatus.PENDING
        );

        return analysisJobRepository.save(analysisJob);
    }

    public AnalysisJob getAnalysisJobById(UUID id)
    {
        return analysisJobRepository.findById(id)
                .orElseThrow(
                        ()-> new AnalysisJobNotFoundException(
                                "Analysis job not Found with Id: " + id
                        )
                );
    }
}
