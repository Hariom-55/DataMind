package com.datamind.datamind_api.dataset.util;

import org.junit.jupiter.api.Test;
import org.springframework.mock.web.MockMultipartFile;
import org.springframework.web.multipart.MultipartFile;

import static org.junit.jupiter.api.Assertions.*;

class FileHashUtilTest
{
    @Test
    void shouldProduceSameHashForSameContent()
    {
        MultipartFile firstFile = new MockMultipartFile(
                "file",
                "first.txt",
                "text/plain",
                "Hello DataMind".getBytes()
        );

        MultipartFile secondFile = new MockMultipartFile(
                "file",
                "second.txt",
                "text/plain",
                "Hello DataMind".getBytes()
        );

        String firstHash = FileHashUtil.sha256(firstFile);
        String secondHash = FileHashUtil.sha256(secondFile);

        assertEquals(firstHash, secondHash);
    }


    @Test
    void shouldProduceDifferentHashForDifferentContent()
    {
        MultipartFile firstFile = new MockMultipartFile(
                "file",
                "first.txt",
                "text/plain",
                "Hello DataMind".getBytes()
        );

        MultipartFile secondFile = new MockMultipartFile(
                "file",
                "second.txt",
                "text/plain",
                "Hello World".getBytes()
        );

        String firstHash = FileHashUtil.sha256(firstFile);
        String secondHash = FileHashUtil.sha256(secondFile);

        assertNotEquals(firstHash, secondHash);
    }


    @Test
    void shouldHashEmptyFileWithoutError()
    {
        MultipartFile file = new MockMultipartFile(
                "file",
                "empty.txt",
                "text/plain",
                new byte[0]
        );

        String hash = assertDoesNotThrow(
                () -> FileHashUtil.sha256(file)
        );

        assertNotNull(hash);
        assertEquals(64, hash.length());
    }
}