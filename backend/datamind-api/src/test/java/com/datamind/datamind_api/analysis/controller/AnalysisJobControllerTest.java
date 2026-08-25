package com.datamind.datamind_api.analysis.controller;


import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.service.AnalysisJobService;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.exception.GlobalExceptionHandler;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;
import org.springframework.http.MediaType;
import org.springframework.test.web.servlet.result.MockMvcResultHandlers;

import java.time.LocalDateTime;
import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;
@WebMvcTest(AnalysisJobController.class)
@Import(GlobalExceptionHandler.class)
public class AnalysisJobControllerTest
{
    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private AnalysisJobService analysisJobService;

    @Test
    void shouldCreateAnalysisJob() throws Exception
    {
        UUID datasetId = UUID.randomUUID();

        Dataset dataset = mock(Dataset.class);
        when(dataset.getId()).thenReturn(datasetId);

        AnalysisJob analysisJob = new AnalysisJob(
                dataset,
                AnalysisType.EDA,
                AnalysisJobStatus.PENDING
        );

        when(analysisJobService.createAnalysisJob(
                datasetId,
                AnalysisType.EDA
        )).thenReturn(analysisJob);

        mockMvc.perform(
                        post("/api/analysis/jobs")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                            {
                                "datasetId": "%s",
                                "analysisType": "EDA"
                            }
                            """.formatted(datasetId))
                )
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isAccepted());

        verify(analysisJobService).createAnalysisJob(
                datasetId,
                AnalysisType.EDA
        );
    }

    @Test
    void shouldRejectRequestWhenDatasetIdIsMissing() throws Exception
    {
        mockMvc.perform(
                        post("/api/analysis/jobs")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                            {
                                "analysisType": "EDA"
                            }
                            """)
                )
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error").value("VALIDATION_ERROR"))
                .andExpect(jsonPath("$.message").value("datasetId: must not be null"))
                .andExpect(jsonPath("$.timestamp").exists());
    }

    @Test
    void shouldRejectRequestWhenAnalysisTypeIsMissing() throws Exception
    {
        UUID datasetId = UUID.randomUUID();

        mockMvc.perform(
                        post("/api/analysis/jobs")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                            {
                                "datasetId": "%s"
                            }
                            """.formatted(datasetId))
                )
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error").value("VALIDATION_ERROR"))
                .andExpect(jsonPath("$.message").value("analysisType: must not be null"))
                .andExpect(jsonPath("$.timestamp").exists());
    }

    @Test
    void shouldRejectRequestWhenAnalysisTypeIsInvalid() throws Exception
    {
        UUID datasetId = UUID.randomUUID();

        mockMvc.perform(
                        post("/api/analysis/jobs")
                                .contentType(MediaType.APPLICATION_JSON)
                                .content("""
                            {
                                "datasetId": "%s",
                                "analysisType": "INVALID"
                            }
                            """.formatted(datasetId))
                )
                .andExpect(status().isBadRequest())
                .andExpect(jsonPath("$.status").value(400))
                .andExpect(jsonPath("$.error").value("INVALID_REQUEST"))
                .andExpect(jsonPath("$.message")
                        .value("Request body contains invalid or malformed data"))
                .andExpect(jsonPath("$.timestamp").exists());
    }

    @Test
    void shouldGetAnalysisJobById() throws Exception
    {
        UUID jobId = UUID.randomUUID();
        UUID datasetId = UUID.randomUUID();

        Dataset dataset = mock(Dataset.class);
        when(dataset.getId()).thenReturn(datasetId);

        AnalysisJob analysisJob = mock(AnalysisJob.class);

        when(analysisJob.getId()).thenReturn(jobId);
        when(analysisJob.getDataset()).thenReturn(dataset);
        when(analysisJob.getAnalysisType()).thenReturn(AnalysisType.EDA);
        when(analysisJob.getStatus()).thenReturn(AnalysisJobStatus.PENDING);
        when(analysisJob.getCreatedAt()).thenReturn(LocalDateTime.now());
        when(analysisJob.getStartedAt()).thenReturn(null);
        when(analysisJob.getCompletedAt()).thenReturn(null);
        when(analysisJob.getErrorMessage()).thenReturn(null);
        when(analysisJob.getRetryCount()).thenReturn(0);

        when(analysisJobService.getAnalysisJobById(jobId))
                .thenReturn(analysisJob);

        mockMvc.perform(
                        get("/api/analysis/jobs/{id}", jobId)
                )
                .andDo(MockMvcResultHandlers.print())
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.id").value(jobId.toString()))
                .andExpect(jsonPath("$.datasetId").value(datasetId.toString()))
                .andExpect(jsonPath("$.analysisType").value("EDA"))
                .andExpect(jsonPath("$.status").value("PENDING"))
                .andExpect(jsonPath("$.retryCount").value(0));

        verify(analysisJobService)
                .getAnalysisJobById(jobId);
    }

    @Test
    void shouldReturnNotFoundWhenAnalysisJobDoesNotExist() throws Exception
    {
        UUID jobId = UUID.randomUUID();

        when(analysisJobService.getAnalysisJobById(jobId))
                .thenThrow(
                        new AnalysisJobNotFoundException(
                                "Analysis job not Found with Id: " + jobId
                        )
                );

        mockMvc.perform(
                        get("/api/analysis/jobs/{id}", jobId)
                )
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error")
                        .value("ANALYSIS_JOB_NOT_FOUND"))
                .andExpect(jsonPath("$.message")
                        .value("Analysis job not Found with Id: " + jobId))
                .andExpect(jsonPath("$.timestamp").exists());
    }


}
