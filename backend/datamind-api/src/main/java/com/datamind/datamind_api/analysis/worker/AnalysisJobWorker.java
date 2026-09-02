package com.datamind.datamind_api.analysis.worker;


import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisClient;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisException;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;
import com.datamind.datamind_api.analysis.service.AnalysisExecutionService;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import com.datamind.datamind_api.analysis.service.AnalysisResultService;
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
    private final AnalysisExecutionService analysisExecutionService;
    public AnalysisJobWorker(
            AnalysisJobService analysisJobService,
            PythonAnalysisClient pythonAnalysisClient,
            AnalysisExecutionService analysisExecutionService
    )
    {
        this.analysisJobService = analysisJobService ;
        this.pythonAnalysisClient = pythonAnalysisClient;
        this.analysisExecutionService = analysisExecutionService;
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
                    job.getAnalysisType().toString(),
                    job.getDataset().getStoragePath(),
                    job.getDataset().getFileType()
            );

            if ("COMPLETED".equals(response.getStatus())
            && response.getError() == null
            && response.getResult() != null)
            {
                analysisExecutionService.completeJob(
                        job.getId(),
                        response.getResult()
                );
                
                log.info(
                        "Analysis job {} completed successfully",
                        job.getId()
                );
            }else {
                String failureReason = response.getError() != null
                        ? response.getError()
                        : "Python Service did not return a completed result" ;
                analysisJobService.failJob(job.getId(), failureReason);
                log.warn(
                        "Analysis job {} failed: {}",
                        job.getId(),
                        failureReason
                );
            }


        }
        catch (PythonAnalysisException ex)
        {
            analysisJobService.failJob(job.getId(), ex.getMessage());
            log.error(
                    "Analysis job {} failed calling Python service",
                    job.getId(),
                    ex);
        }
    }
}
