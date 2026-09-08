package com.datamind.datamind_api.dataset.service;

import org.junit.jupiter.api.Test;
import org.junit.jupiter.api.io.TempDir;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Files;
import java.nio.file.Path;

import static org.junit.jupiter.api.Assertions.*;

class DatasetStorageServiceTest
{
    @TempDir
    Path tempDirectory;


    @Test
    void shouldStoreFileWithHashAsFilename()
    {
        DatasetStorageService storageService =
                new DatasetStorageService(tempDirectory.toString());

        String contentHash =
                "abc123def456";

        MultipartFile file = new MockMultipartFile(
                "file",
                "customers.csv",
                "text/csv",
                "name,age\nHariom,22".getBytes()
        );

        String storedPath =
                storageService.store(file, contentHash);

        Path expectedPath =
                tempDirectory.resolve("abc123def456.csv");

        assertEquals(
                expectedPath.toString(),
                storedPath
        );

        assertTrue(Files.exists(expectedPath));
    }


    @Test
    void shouldPreserveFileExtension()
    {
        DatasetStorageService storageService =
                new DatasetStorageService(tempDirectory.toString());

        String contentHash =
                "abc123def456";

        MultipartFile file = new MockMultipartFile(
                "file",
                "customers.csv",
                "text/csv",
                "name,age\nHariom,22".getBytes()
        );

        String storedPath =
                storageService.store(file, contentHash);

        assertTrue(
                storedPath.endsWith(
                        contentHash + ".csv"
                )
        );
    }


    @Test
    void shouldHandleFilenameWithNoExtension()
    {
        DatasetStorageService storageService =
                new DatasetStorageService(tempDirectory.toString());

        String contentHash =
                "abc123def456";

        MultipartFile file = new MockMultipartFile(
                "file",
                "customers",
                "text/plain",
                "sample data".getBytes()
        );

        String storedPath =
                assertDoesNotThrow(
                        () -> storageService.store(
                                file,
                                contentHash
                        )
                );

        Path expectedPath =
                tempDirectory.resolve(contentHash);

        assertEquals(
                expectedPath.toString(),
                storedPath
        );

        assertTrue(Files.exists(expectedPath));
    }

    @Test
    void shouldStoreBytesWithHashAsFilename()
    {
        DatasetStorageService storageService =
                new DatasetStorageService(tempDirectory.toString());

        String contentHash =
                "cleaned123456";

        byte[] content =
                "name,age\nHariom,22".getBytes();

        String storedPath =
                storageService.storeBytes(
                        content,
                        contentHash,
                        ".csv"
                );

        Path expectedPath =
                tempDirectory.resolve(
                        "cleaned123456.csv"
                );

        assertEquals(
                expectedPath.toString(),
                storedPath
        );

        assertTrue(
                Files.exists(expectedPath)
        );
    }

    @Test
    void shouldPreserveStoredByteContent()
            throws Exception
    {
        DatasetStorageService storageService =
                new DatasetStorageService(tempDirectory.toString());

        String contentHash =
                "cleaned123456";

        byte[] content =
                "name,age\nHariom,22".getBytes();

        String storedPath =
                storageService.storeBytes(
                        content,
                        contentHash,
                        ".csv"
                );

        byte[] storedContent =
                Files.readAllBytes(
                        Path.of(storedPath)
                );

        assertArrayEquals(
                content,
                storedContent
        );
    }

    @Test
    void shouldNormalizeExtension()
    {
        DatasetStorageService storageService =
                new DatasetStorageService(tempDirectory.toString());

        String contentHash =
                "cleaned123456";

        byte[] content =
                "sample data".getBytes();

        String storedPath =
                storageService.storeBytes(
                        content,
                        contentHash,
                        "csv"
                );

        Path expectedPath =
                tempDirectory.resolve(
                        "cleaned123456.csv"
                );

        assertEquals(
                expectedPath.toString(),
                storedPath
        );

        assertTrue(
                Files.exists(expectedPath)
        );
    }
}