package com.datamind.datamind_api.dataset.service;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.io.IOException;
import java.nio.file.Files;
import java.nio.file.Path;
import java.nio.file.Paths;

@Service
public class DatasetStorageService {

    private final Path storageDirectory;

    public DatasetStorageService(
            @Value("${datamind.dataset.storage-path}") String storagePath
    ) {
        this.storageDirectory = Paths.get(storagePath)
                .toAbsolutePath()
                .normalize();
    }

    public String store(
            MultipartFile file,
            String contentHash
    ) {

        try {

            Files.createDirectories(storageDirectory);

            String originalFilename = file.getOriginalFilename();

            String extension = "";

            if (originalFilename != null && originalFilename.contains(".")) {
                extension = originalFilename.substring(
                        originalFilename.lastIndexOf(".")
                );
            }

            String storedFilename = contentHash + extension;

            Path targetPath = storageDirectory.resolve(storedFilename);

            file.transferTo(targetPath);

            return targetPath.toString();

        } catch (IOException e) {

            throw new RuntimeException(
                    "Failed to store dataset file",
                    e
            );
        }
    }
}