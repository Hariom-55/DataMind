package com.datamind.datamind_api.dataset.controller;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import com.datamind.datamind_api.dataset.service.DatasetService;
import org.junit.jupiter.api.Test;
import org.springframework.beans.factory.annotation.Autowired;
import org.springframework.boot.webmvc.test.autoconfigure.WebMvcTest;
import org.springframework.test.context.bean.override.mockito.MockitoBean;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.test.web.servlet.MockMvc;

import java.util.UUID;

import static org.mockito.ArgumentMatchers.any;
import static org.mockito.Mockito.*;
import static org.springframework.test.web.servlet.request.MockMvcRequestBuilders.*;
import static org.springframework.test.web.servlet.result.MockMvcResultMatchers.*;

@WebMvcTest(DatasetController.class)
class DatasetControllerTest
{
    @Autowired
    private MockMvc mockMvc;

    @MockitoBean
    private DatasetService datasetService;


    @Test
    void shouldReturn200OnSuccessfulUpload() throws Exception
    {
        Dataset dataset = new Dataset(
                "customers.csv",
                "abc123",
                100L,
                "text/csv"
        );

        dataset.setStoragePath("/data/abc123.csv");

        when(datasetService.uploadDataset(any()))
                .thenReturn(dataset);

        MockMultipartFile file = new MockMultipartFile(
                "file",
                "customers.csv",
                "text/csv",
                "name,age\nHariom,22".getBytes()
        );

        mockMvc.perform(
                        multipart("/api/datasets")
                                .file(file)
                )
                .andExpect(status().isOk());

        verify(datasetService)
                .uploadDataset(any());
    }


    @Test
    void shouldReturn400WhenNoFileProvided() throws Exception
    {
        when(datasetService.uploadDataset(any()))
                .thenThrow(
                        new IllegalArgumentException(
                                "Dataset file is required"
                        )
                );

        mockMvc.perform(
                        multipart("/api/datasets")
                )
                .andExpect(status().isBadRequest());

        verify(datasetService, never())
                .uploadDataset(any());
    }


    @Test
    void shouldReturn404WhenDatasetNotFound() throws Exception
    {
        UUID datasetId = UUID.randomUUID();

        when(datasetService.getDatasetById(datasetId))
                .thenThrow(
                        new DatasetNotFoundException(
                                "Dataset not found with id: " + datasetId
                        )
                );

        mockMvc.perform(
                        get("/api/datasets/{id}", datasetId)
                )
                .andExpect(status().isNotFound());

        verify(datasetService)
                .getDatasetById(datasetId);
    }
}