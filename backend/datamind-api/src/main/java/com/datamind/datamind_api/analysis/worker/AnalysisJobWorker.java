package com.datamind.datamind_api.analysis.worker;


import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.repository.AnalysisJobRepository;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class AnalysisJobWorker
{
    private final AnalysisJobService analysisJobService ;

    public AnalysisJobWorker(AnalysisJobService analysisJobService)
    {
        this.analysisJobService = analysisJobService ;
    }

    @Scheduled(fixedDelay = 5000)
    public void processPendingJob()
    {
        analysisJobService
                .claimNextPendingJob()
                .ifPresent(this::processJob);
    }

    private void processJob(AnalysisJob job)
    {
        //python Integration 
    }
}
