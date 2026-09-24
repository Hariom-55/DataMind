package com.datamind.datamind_api.dataset.controller;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningAssessmentResponse;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningPreviewResponse;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import com.datamind.datamind_api.dataset.service.DatasetCleaningExecution;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.service.DatasetCleaningOrchestrationService;
import com.datamind.datamind_api.dataset.service.DatasetLineageService;
import com.datamind.datamind_api.dataset.service.DatasetService;
import com.datamind.datamind_api.exception.GlobalExceptionHandler;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.context.annotation.Import;
import org.springframework.http.MediaType;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.util.List;
import java.util.Map;
import java.util.UUID;

import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.post;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(DatasetCleaningController.class)
@Import(GlobalExceptionHandler.class)
class DatasetCleaningControllerTest {
    @Autowired MockMvc mockMvc;
    @MockitoBean DatasetService datasetService;
    @MockitoBean DatasetCleaningOrchestrationService cleaningService;
    @MockitoBean DatasetLineageService lineageService;

    @Test
    void returnsRecommendationsForTheRequestedVersion() throws Exception {
        UUID logicalId = UUID.randomUUID();
        UUID versionId = UUID.randomUUID();
        Dataset version = version(logicalId, versionId);
        when(datasetService.getDatasetById(logicalId)).thenReturn(version);
        when(datasetService.getDatasetById(versionId)).thenReturn(version);
        when(cleaningService.assessDataset(version)).thenReturn(
                new PythonCleaningAssessmentResponse(4, 2, 1, List.of(),
                        List.of(Map.of("operation", "REMOVE_DUPLICATES")))
        );

        mockMvc.perform(get("/api/datasets/{logical}/versions/{version}/cleaning/recommendations", logicalId, versionId))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.totalRows").value(4))
                .andExpect(jsonPath("$.issueCount").value(1))
                .andExpect(jsonPath("$.recommendations[0].operation").value("REMOVE_DUPLICATES"));
    }

    @Test
    void previewsCleaningAgainstThePinnedVersion() throws Exception {
        UUID logicalId = UUID.randomUUID();
        UUID versionId = UUID.randomUUID();
        Dataset version = version(logicalId, versionId);
        when(datasetService.getDatasetById(logicalId)).thenReturn(version);
        when(datasetService.getDatasetById(versionId)).thenReturn(version);
        when(cleaningService.previewDataset(eq(version), anyList())).thenReturn(
                new PythonCleaningPreviewResponse(4, 3, 2, 2, 1, List.of())
        );

        mockMvc.perform(post("/api/datasets/{logical}/versions/{version}/cleaning/preview", logicalId, versionId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"operations\":[{\"operation\":\"REMOVE_DUPLICATES\"}]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.logicalDatasetId").value(logicalId.toString()))
                .andExpect(jsonPath("$.datasetVersionId").value(versionId.toString()))
                .andExpect(jsonPath("$.originalRows").value(4))
                .andExpect(jsonPath("$.cleanedRows").value(3));
    }

    @Test
    void rejectsEmptyCleaningOperations() throws Exception {
        UUID logicalId = UUID.randomUUID();
        UUID versionId = UUID.randomUUID();
        mockMvc.perform(post("/api/datasets/{logical}/versions/{version}/cleaning/preview", logicalId, versionId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"operations\":[]}"))
                .andExpect(status().isBadRequest());
        verifyNoInteractions(cleaningService);
    }

    @Test
    void applyResponseReportsCanonicalCsvMetadata() throws Exception {
        UUID logicalId = UUID.randomUUID();
        UUID versionId = UUID.randomUUID();
        Dataset parent = version(logicalId, versionId);
        Dataset child = mock(Dataset.class);
        when(child.getId()).thenReturn(UUID.randomUUID());
        when(child.getLogicalDatasetId()).thenReturn(logicalId);
        when(child.getVersionNumber()).thenReturn(2);
        when(child.getName()).thenReturn("customers.csv");
        when(child.getFileType()).thenReturn("text/csv");
        when(datasetService.getDatasetById(logicalId)).thenReturn(parent);
        when(datasetService.getDatasetById(versionId)).thenReturn(parent);
        when(cleaningService.cleanDatasetWithResult(eq(parent), anyList())).thenReturn(
                new DatasetCleaningExecution(child, new PythonCleaningResponse(
                        "", "hash", "csv", 4, 3, 2, 2, 1, List.of()
                ))
        );
        when(lineageService.getLineage(child.getId())).thenReturn(List.of());

        mockMvc.perform(post("/api/datasets/{logical}/versions/{version}/cleaning", logicalId, versionId)
                        .contentType(MediaType.APPLICATION_JSON)
                        .content("{\"operations\":[{\"operation\":\"REMOVE_DUPLICATES\"}]}"))
                .andExpect(status().isOk())
                .andExpect(jsonPath("$.format").value("CSV"))
                .andExpect(jsonPath("$.extension").value("csv"))
                .andExpect(jsonPath("$.contentType").value("text/csv"))
                .andExpect(jsonPath("$.dataset.name").value("customers.csv"))
                .andExpect(jsonPath("$.dataset.fileType").value("text/csv"));
    }

    private Dataset version(UUID logicalId, UUID versionId) {
        Dataset dataset = mock(Dataset.class);
        when(dataset.getId()).thenReturn(versionId);
        when(dataset.getLogicalDatasetId()).thenReturn(logicalId);
        when(dataset.getVersionNumber()).thenReturn(2);
        return dataset;
    }
}
