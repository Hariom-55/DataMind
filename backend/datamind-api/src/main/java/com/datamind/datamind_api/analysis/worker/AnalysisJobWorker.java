package com.datamind.datamind_api.analysis.worker;


import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class AnalysisJobWorker
{
    private final AnalysisJobRepository analysisJobRepository;

    public AnalysisJobWorker(
            AnalysisJobRepository analysisJobRepository
    ){
        this.analysisJobRepository = analysisJobRepository;
    }

    @Scheduled(fixedDelay = 5000)
    public void processPendingJobs()
    {
        analysisJobRepository
                .findFirstByStatusOrderByCreatedAtAsc(
                        AnalysisJobStatus.PENDING
                )
                .ifPresent(this::processJob);
    }

    private void processJob(AnalysisJob job)
    {
        job.markAsProcessing();

        analysisJobRepository.save(job);
    }
}
