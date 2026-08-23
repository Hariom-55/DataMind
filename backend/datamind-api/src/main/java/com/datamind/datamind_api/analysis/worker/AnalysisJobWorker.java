package com.datamind.datamind_api.analysis.worker;


import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisClient;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisException;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class AnalysisJobWorker
{
    private static final Logger log = LoggerFactory.getLogger(AnalysisJobWorker.class);

    private final AnalysisJobService analysisJobService ;
    private final PythonAnalysisClient pythonAnalysisClient;

    public AnalysisJobWorker(
            AnalysisJobService analysisJobService,
            PythonAnalysisClient pythonAnalysisClient
    )
    {
        this.analysisJobService = analysisJobService ;
        this.pythonAnalysisClient = pythonAnalysisClient;
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
        try
        {
            PythonAnalysisResponse response = pythonAnalysisClient.analyze(
                    job.getId(),
                    job.getDataset().getId(),
                    job.getAnalysisType().toString()
            );

            if ("RECEIVED".equals(response.getStatus()) || response.getError() == null)
            {
                analysisJobService.completeJob(job.getId());
                log.info("Analysis job {} completed", job.getId());
            }
            else
            {
                analysisJobService.failJob(job.getId());
                log.warn("Analysis job {} failed: {}", job.getId(), response.getError());
            }
        }
        catch (PythonAnalysisException ex)
        {
            analysisJobService.failJob(job.getId());
            log.error("Analysis job {} failed calling Python service", job.getId(), ex);
        }
    }
}
