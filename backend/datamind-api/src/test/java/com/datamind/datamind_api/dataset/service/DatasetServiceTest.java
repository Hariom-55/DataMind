package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.extension.ExtendWith;
import org.mockito.InjectMocks;
import org.mockito.Mock;
import org.mockito.junit.jupiter.MockitoExtension;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;
import org.springframework.dao.DataIntegrityViolationException;

import java.util.Optional;

import static org.junit.jupiter.api.Assertions.*;
import static org.mockito.Mockito.*;


@ExtendWith(MockitoExtension.class)
public class DatasetServiceTest
{
    @Mock
    private DatasetRepository datasetRepository;

    @Mock
    private DatasetStorageService datasetStorageService;

    @InjectMocks
    private DatasetService datasetService;

    @Test
    void shouldUploadDataset()
    {
        MultipartFile file = new MockMultipartFile(
                "file",
                "customers.csv",
                "text/csv",
                "name,age\nHariom,22".getBytes()
        );

        String storagePath ="./data/abc123.csv";

        when(datasetRepository.findByContentHash(anyString()))
                .thenReturn(Optional.empty());

        when(datasetStorageService.store(eq(file),anyString()))
                .thenReturn(storagePath);

        when(datasetRepository.save(any(Dataset.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        Dataset result = datasetService.uploadDataset(file);

        assertNotNull(result);
        assertEquals("customers.csv",result.getName());
        assertEquals("text/csv", result.getFileType());
        assertEquals((long) file.getSize() , result.getFileSize());
        assertEquals(storagePath , result.getStoragePath());
        assertNotNull(result.getContentHash());


        verify(datasetRepository)
                .findByContentHash(result.getContentHash());

        verify(datasetStorageService)
                .store(file, result.getContentHash());

        verify(datasetRepository)
                .save(result);
    }

    @Test
    void shouldReturnExistingDatasetOnDuplicateUpload()
    {
        MultipartFile file = new MockMultipartFile(
                "file",
                "customer.csv",
                "text/csv",
                "name,age\nHariom, 22".getBytes()
        );

        Dataset existingDataset = mock(Dataset.class);

        when(datasetRepository.findByContentHash(anyString()))
                .thenReturn(Optional.of(existingDataset));

        Dataset result = datasetService.uploadDataset(file);

        assertSame(existingDataset, result);

        verify(datasetRepository)
                .findByContentHash(anyString());

        verify(datasetStorageService, never())
                .store(any(MultipartFile.class), anyString());

        verify(datasetRepository, never())
                .save(any(Dataset.class));
    }

    @Test
    void shouldRecoverFromRaceConditionOnConcurrentInsert()
    {
        MultipartFile file = new MockMultipartFile(
                "file",
                "customer.csv",
                "text/csv",
                "name,age\nHariom, 22".getBytes()
        );

        Dataset existingDataset = mock(Dataset.class);

        when(datasetRepository.findByContentHash(anyString()))
                .thenReturn(
                        Optional.empty(),
                        Optional.of(existingDataset)
                );

        when(datasetRepository.save(any(Dataset.class)))
                .thenThrow(
                        new DataIntegrityViolationException(
                                "Duplicate content hash"
                        )
                );

        Dataset result = datasetService.uploadDataset(file);

        assertSame(existingDataset, result);

        verify(datasetRepository, times(2))
                .findByContentHash(anyString());

        verify(datasetStorageService)
                .store(eq(file), anyString());

        verify(datasetRepository)
                .save(any(Dataset.class));


    }

    @Test
    void shouldThrowWhenFileIsNull()
    {
        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        ()-> datasetService.uploadDataset(null)
                );

        assertEquals(
                "Dataset file is required",
                exception.getMessage()
        );

        verifyNoInteractions(
                datasetRepository,
                datasetStorageService
        );


    }

    @Test
    void shouldThrowWhenFileIsEmpty()
    {
        MultipartFile file = new MockMultipartFile(
                "file",
                "customer.csv",
                "text/csv",
                new byte[0]
        );

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        ()-> datasetService.uploadDataset(file)
                );

        assertEquals(
                "Dataset file is required",
                exception.getMessage()
        );

        verifyNoInteractions(
                datasetRepository,
                datasetStorageService
        );
    }

    @Test
    void shouldThrowWhenFilenameIsMissing()
    {
        MultipartFile file = new MockMultipartFile(
                "file",
                null,
                "text/csv",
                "name,age\nHariom, 22".getBytes()
        );

        IllegalArgumentException exception =
                assertThrows(
                        IllegalArgumentException.class,
                        () -> datasetService.uploadDataset(file)
                );

        assertEquals(
                "Dataset file name is required",
                exception.getMessage()
        );

        verifyNoInteractions(
                datasetRepository,
                datasetStorageService
        );


    }

    @Test
    void shouldDefaultFileTypeWhenContentTypeIsNull()
    {
        MultipartFile file = new MockMultipartFile(
                "file",
                "customers.csv",
                null,
                "name,age\nHariom,22".getBytes()
        );

        when(datasetRepository.findByContentHash(anyString()))
                .thenReturn(Optional.empty());

        when(datasetStorageService.store(
                any(MultipartFile.class),
                anyString()
        )).thenReturn("./data/abc123.csv");

        when(datasetRepository.save(any(Dataset.class)))
                .thenAnswer(invocation -> invocation.getArgument(0));

        Dataset result = datasetService.uploadDataset(file);

        assertEquals(
                "application/octet-stream",
                result.getFileType()
        );

        verify(datasetRepository)
                .save(any(Dataset.class));
    }


}
