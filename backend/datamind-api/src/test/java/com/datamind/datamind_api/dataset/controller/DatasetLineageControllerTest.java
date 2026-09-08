package com.datamind.datamind_api.dataset.controller;

import com.datamind.datamind_api.dataset.dto.DatasetLineageResponse;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import com.datamind.datamind_api.dataset.service.DatasetLineageService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.test.web.servlet.MockMvc;

import java.time.LocalDateTime;
import java.util.List;
import java.util.UUID;

import static org.mockito.Mockito.when;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.get;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.jsonPath;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.status;

@WebMvcTest(DatasetLineageController.class)
class DatasetLineageControllerTest {

    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private DatasetLineageService lineageService;


    @Test
    void shouldReturnDatasetLineage() throws Exception {

        UUID datasetId = UUID.randomUUID();
        UUID parentDatasetId = UUID.randomUUID();

        DatasetLineageResponse response =
                new DatasetLineageResponse(
                        datasetId,
                        parentDatasetId,
                        "REMOVE_DUPLICATES",
                        null,
                        5,
                        "5 duplicate rows removed",
                        LocalDateTime.now()
                );

        when(
                lineageService.getLineage(datasetId)
        ).thenReturn(
                List.of(response)
        );

        mockMvc.perform(
                        get(
                                "/api/datasets/{datasetId}/lineage",
                                datasetId
                        )
                )
                .andExpect(status().isOk())
                .andExpect(
                        jsonPath("$").isArray()
                )
                .andExpect(
                        jsonPath("$.length()").value(1)
                )
                .andExpect(
                        jsonPath("$[0].datasetId")
                                .value(datasetId.toString())
                )
                .andExpect(
                        jsonPath("$[0].parentDatasetId")
                                .value(parentDatasetId.toString())
                )
                .andExpect(
                        jsonPath("$[0].operation")
                                .value("REMOVE_DUPLICATES")
                )
                .andExpect(
                        jsonPath("$[0].columnName")
                                .doesNotExist()
                )
                .andExpect(
                        jsonPath("$[0].rowsAffected")
                                .value(5)
                )
                .andExpect(
                        jsonPath("$[0].details")
                                .value("5 duplicate rows removed")
                )
                .andExpect(
                        jsonPath("$[0].createdAt")
                                .exists()
                );
    }

    @Test
    void shouldReturnEmptyLineageForOriginalDataset()
            throws Exception {

        UUID datasetId = UUID.randomUUID();

        when(
                lineageService.getLineage(datasetId)
        ).thenReturn(
                List.of()
        );

        mockMvc.perform(
                        get(
                                "/api/datasets/{datasetId}/lineage",
                                datasetId
                        )
                )
                .andExpect(status().isOk())
                .andExpect(
                        jsonPath("$").isArray()
                )
                .andExpect(
                        jsonPath("$.length()").value(0)
                );
    }

    @Test
    void shouldReturnMultipleLineageEntries()
            throws Exception {

        UUID originalId = UUID.randomUUID();
        UUID versionOneId = UUID.randomUUID();
        UUID versionTwoId = UUID.randomUUID();

        DatasetLineageResponse first =
                new DatasetLineageResponse(
                        versionOneId,
                        originalId,
                        "REMOVE_DUPLICATES",
                        null,
                        5,
                        "5 duplicate rows removed",
                        LocalDateTime.now()
                );

        DatasetLineageResponse second =
                new DatasetLineageResponse(
                        versionTwoId,
                        versionOneId,
                        "IMPUTE_MISSING_VALUES",
                        "age",
                        10,
                        "10 missing values imputed",
                        LocalDateTime.now()
                );

        when(
                lineageService.getLineage(versionTwoId)
        ).thenReturn(
                List.of(first, second)
        );

        mockMvc.perform(
                        get(
                                "/api/datasets/{datasetId}/lineage",
                                versionTwoId
                        )
                )
                .andExpect(status().isOk())
                .andExpect(
                        jsonPath("$.length()").value(2)
                )
                .andExpect(
                        jsonPath("$[0].operation")
                                .value("REMOVE_DUPLICATES")
                )
                .andExpect(
                        jsonPath("$[1].operation")
                                .value("IMPUTE_MISSING_VALUES")
                )
                .andExpect(
                        jsonPath("$[1].columnName")
                                .value("age")
                )
                .andExpect(
                        jsonPath("$[1].rowsAffected")
                                .value(10)
                );
    }

    @Test
    void shouldReturn404WhenDatasetDoesNotExist() throws Exception {

        UUID datasetId = UUID.randomUUID();

        when(lineageService.getLineage(datasetId))
                .thenThrow(
                        new DatasetNotFoundException(
                                "Dataset not found: " + datasetId
                        )
                );

        mockMvc.perform(
                        get("/api/datasets/{datasetId}/lineage", datasetId)
                )
                .andExpect(status().isNotFound())
                .andExpect(jsonPath("$.status").value(404))
                .andExpect(jsonPath("$.error").value("DATASET_NOT_FOUND"))
                .andExpect(
                        jsonPath("$.message")
                                .value("Dataset not found: " + datasetId)
                )
                .andExpect(jsonPath("$.timestamp").exists());
    }
}