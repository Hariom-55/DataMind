package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import com.datamind.datamind_api.dataset.util.FileHashUtil;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.util.StringUtils;
import org.springframework.web.multipart.MultipartFile;

import java.nio.file.Path;
import java.util.List;
import java.util.Locale;
import java.util.Optional;
import java.util.Set;
import java.util.UUID;

@Service
public class DatasetService {
    private final DatasetRepository datasetRepository;
    private final DatasetStorageService datasetStorageService;
    private final long maxFileSizeBytes;
    private final Set<String> allowedExtensions;

    public DatasetService(
            DatasetRepository datasetRepository,
            DatasetStorageService datasetStorageService,
            @Value("${datamind.dataset.max-file-size:50MB}") org.springframework.util.unit.DataSize maxFileSize,
            @Value("${datamind.dataset.allowed-extensions:csv,xlsx,xls,json,parquet}") String allowedExtensions
    ) {
        this.datasetRepository = datasetRepository;
        this.datasetStorageService = datasetStorageService;
        this.maxFileSizeBytes = maxFileSize.toBytes();
        this.allowedExtensions = Set.of(allowedExtensions.toLowerCase(Locale.ROOT).split(","));
    }

    public Dataset uploadDataset(MultipartFile file) {
        validateFile(file);

        String contentHash = FileHashUtil.sha256(file);
        Optional<Dataset> existingDataset = datasetRepository.findByContentHash(contentHash);
        if (existingDataset.isPresent()) {
            return existingDataset.get();
        }

        String originalFilename = file.getOriginalFilename().trim();
        Long fileSize = file.getSize();
        String fileType = StringUtils.hasText(file.getContentType())
                ? file.getContentType()
                : "application/octet-stream";

        Dataset dataset = new Dataset(originalFilename, contentHash, fileSize, fileType);
        String storagePath = datasetStorageService.store(file, contentHash);
        dataset.setStoragePath(storagePath);

        try {
            return datasetRepository.save(dataset);
        } catch (DataIntegrityViolationException exception) {
            return datasetRepository.findByContentHash(contentHash)
                    .orElseThrow(() -> exception);
        }
    }

    private void validateFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Dataset file is required");
        }
        if (file.getSize() > maxFileSizeBytes) {
            throw new IllegalArgumentException("Dataset file exceeds the maximum allowed size of "
                    + maxFileSizeBytes + " bytes");
        }

        String filename = file.getOriginalFilename();
        if (!StringUtils.hasText(filename)) {
            throw new IllegalArgumentException("Dataset file name is required");
        }
        if (filename.indexOf('\0') >= 0) {
            throw new IllegalArgumentException("Dataset file name contains an invalid character");
        }

        String normalizedFilename = filename.replace('\\', '/');
        if (!Path.of(normalizedFilename).getFileName().toString().equals(normalizedFilename)
                || normalizedFilename.contains("..")) {
            throw new IllegalArgumentException("Dataset file name contains an invalid path");
        }

        int dot = filename.lastIndexOf('.');
        if (dot <= 0 || dot == filename.length() - 1) {
            throw new IllegalArgumentException("Dataset file must have a supported extension");
        }

        String extension = filename.substring(dot + 1).toLowerCase(Locale.ROOT);
        if (!allowedExtensions.contains(extension)) {
            throw new IllegalArgumentException("Unsupported dataset file type: " + extension);
        }
    }

    public Dataset getDatasetById(UUID id) {
        return datasetRepository.findById(id)
                .orElseThrow(() -> new DatasetNotFoundException("Dataset not found with id: " + id));
    }

    public List<Dataset> getAllDatasets() {
        return datasetRepository.findAll();
    }
}
