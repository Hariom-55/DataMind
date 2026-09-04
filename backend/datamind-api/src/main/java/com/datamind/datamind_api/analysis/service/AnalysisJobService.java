package com.datamind.datamind_api.analysis.service;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Optional;
import java.util.UUID;

@Service
public class AnalysisJobService
{
    private final AnalysisJobRepository analysisJobRepository;
    private final DatasetService datasetService;
    private static final int MAX_RETRIES = 3;

    public AnalysisJobService(
            AnalysisJobRepository analysisJobRepository,
            DatasetService datasetService
    ){
        this.analysisJobRepository = analysisJobRepository;
        this.datasetService = datasetService;
    }

    public AnalysisJob createAnalysisJob(
            java.util.UUID datasetId,
            AnalysisType analysisType,
            String targetColumn
    ){
        Dataset dataset = datasetService.getDatasetById(datasetId);

        AnalysisJob analysisJob =new AnalysisJob(
                dataset,
                analysisType,
                AnalysisJobStatus.PENDING
        );

        analysisJob.setTargetColumn(targetColumn);

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

    @Transactional
    public Optional<AnalysisJob> claimNextPendingJob()
    {
        Optional<AnalysisJob> job = analysisJobRepository.findNextPendingJob(
                AnalysisJobStatus.PENDING.name()
                
        );

        job.ifPresent( analysisJob -> {
            analysisJob.markAsProcessing();
            analysisJobRepository.save(analysisJob);
        });

        return job ;
    }

    @Transactional
    public void completeJob(UUID jobId)
    {
        AnalysisJob job = getAnalysisJobById(jobId);
        job.markAsCompleted();
        analysisJobRepository.save(job);
    }

    @Transactional
    public void failJob(UUID jobId, String errorMessage)
    {
        AnalysisJob job = getAnalysisJobById(jobId);
        job.incrementRetryCount();

        if (job.getRetryCount() < MAX_RETRIES)
        {
            job.retry();
            analysisJobRepository.save(job);
            return;
        }
        job.markAsFailed(errorMessage);
        analysisJobRepository.save(job);
    }
}
