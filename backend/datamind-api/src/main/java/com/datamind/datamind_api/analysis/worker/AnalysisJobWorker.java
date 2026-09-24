package com.datamind.datamind_api.analysis.worker;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisClient;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisException;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;
import com.datamind.datamind_api.analysis.service.AnalysisExecutionService;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.scheduling.annotation.Scheduled;
import org.springframework.stereotype.Component;

@Component
public class AnalysisJobWorker {
    private static final Logger log = LoggerFactory.getLogger(AnalysisJobWorker.class);

    private final AnalysisJobService analysisJobService;
    private final PythonAnalysisClient pythonAnalysisClient;
    private final AnalysisExecutionService analysisExecutionService;

    public AnalysisJobWorker(
            AnalysisJobService analysisJobService,
            PythonAnalysisClient pythonAnalysisClient,
            AnalysisExecutionService analysisExecutionService
    ) {
        this.analysisJobService = analysisJobService;
        this.pythonAnalysisClient = pythonAnalysisClient;
        this.analysisExecutionService = analysisExecutionService;
    }

    @Scheduled(fixedDelayString = "${datamind.jobs.worker-delay:5s}")
    public void processPendingJob() {
        int recovered = analysisJobService.recoverStaleJobs();
        if (recovered > 0) {
            log.warn("Recovered {} stale analysis jobs", recovered);
        }
        analysisJobService.claimNextPendingJob().ifPresent(this::processJob);
    }

    private void processJob(AnalysisJob job) {
        var version = job.getDatasetVersion() != null
                ? job.getDatasetVersion()
                : job.getDataset();

        try {
            PythonAnalysisResponse response;
            if (job.getHypothesisTests() == null || job.getHypothesisTests().isEmpty()) {
                response = pythonAnalysisClient.analyze(
                        job.getId(), version.getId(), job.getAnalysisType().toString(),
                        version.getStoragePath(), version.getFileType(), job.getTargetColumn(),
                        job.isEnableHyperparameterTuning()
                );
            } else {
                response = pythonAnalysisClient.analyze(
                        job.getId(), version.getId(), job.getAnalysisType().toString(),
                        version.getStoragePath(), version.getFileType(), job.getTargetColumn(),
                        job.isEnableHyperparameterTuning(), job.getHypothesisTests()
                );
            }

            if ("COMPLETED".equals(response.getStatus())
                    && response.getError() == null
                    && response.getResult() != null) {
                analysisExecutionService.completeJob(job.getId(), response.getResult());
                log.info(
                        "Analysis job {} completed for dataset version {}",
                        job.getId(),
                        version.getVersionNumber()
                );
            } else {
                String failureReason = response.getError() != null
                        ? response.getError()
                        : "Python service did not return a completed result";
                analysisJobService.failJob(job.getId(), failureReason);
                log.warn("Analysis job {} failed: {}", job.getId(), failureReason);
            }
        } catch (PythonAnalysisException ex) {
            analysisJobService.failJob(job.getId(), ex.getMessage());
            log.error("Analysis job {} failed calling Python service", job.getId(), ex);
        } catch (Exception ex) {
            analysisJobService.failJob(job.getId(), "Unexpected worker failure");
            log.error(
                    "Unexpected failure while processing analysis job {}",
                    job.getId(),
                    ex
            );
        }
    }
}
