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
import org.springframework.transaction.annotation.Transactional;

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
            @Value("${datamind.dataset.allowed-extensions:csv,json,xlsx,xls,parquet}") String allowedExtensions
    ) {
        this.datasetRepository = datasetRepository;
        this.datasetStorageService = datasetStorageService;
        this.maxFileSizeBytes = maxFileSize.toBytes();
        this.allowedExtensions = Set.of(allowedExtensions.toLowerCase(Locale.ROOT).split(","));
    }

    /**
     * Upload without a logical dataset id creates a new logical dataset family.
     * Supplying datasetId appends to that family only when the content hash changed.
     */
    @Transactional
    public Dataset uploadDataset(MultipartFile file) {
        return uploadDataset(file, null);
    }

    @Transactional
    public Dataset uploadDataset(MultipartFile file, UUID datasetId) {
        validateFile(file);

        String contentHash = FileHashUtil.sha256(file);
        String originalFilename = file.getOriginalFilename().trim();
        Long fileSize = file.getSize();
        String fileType = StringUtils.hasText(file.getContentType())
                ? file.getContentType()
                : "application/octet-stream";

        if (datasetId != null) {
            Dataset requested = getDatasetById(datasetId);
            UUID logicalId = requested.getLogicalDatasetId() != null
                    ? requested.getLogicalDatasetId()
                    : requested.getId();

            Optional<Dataset> existing = datasetRepository
                    .findByLogicalDatasetIdAndContentHash(logicalId, contentHash);

            if (existing.isPresent()) {
                return existing.get();
            }

            int nextVersion = Optional.ofNullable(
                    datasetRepository.findMaxVersionNumber(logicalId)
            ).orElse(0) + 1;

            Dataset version = new Dataset(
                    originalFilename,
                    contentHash,
                    fileSize,
                    fileType
            );
            version.configureAsVersion(logicalId, nextVersion);

            String storagePath = datasetStorageService.store(file, contentHash);
            version.setStoragePath(storagePath);

            Dataset saved;
            try {
                saved = datasetRepository.saveAndFlush(version);
            } catch (DataIntegrityViolationException exception) {
                return datasetRepository
                        .findByLogicalDatasetIdAndContentHash(logicalId, contentHash)
                        .orElseThrow(() -> exception);
            }

            pointRootToCurrentVersion(logicalId, saved.getId());
            return saved;
        }

        // Backward-compatible global idempotency for callers that do not
        // explicitly select a logical dataset. Version-aware callers should
        // provide datasetId.
        Optional<Dataset> globallyExisting = datasetRepository.findByContentHash(contentHash);
        if (globallyExisting.isPresent()) {
            return globallyExisting.get();
        }

        Dataset dataset = new Dataset(
                originalFilename,
                contentHash,
                fileSize,
                fileType
        );

        String storagePath = datasetStorageService.store(file, contentHash);
        dataset.setStoragePath(storagePath);

        try {
            Dataset saved = datasetRepository.save(dataset);
            if (saved.getId() != null) {
                saved.initializeAsRootVersion();
                return datasetRepository.save(saved);
            }
            // Mockito/unit-test friendly fallback; real JPA always assigns the UUID
            // before the transaction returns.
            saved.setLogicalDatasetId(UUID.randomUUID());
            saved.setVersionNumber(1);
            return saved;
        } catch (DataIntegrityViolationException exception) {
            return datasetRepository.findByContentHash(contentHash)
                    .orElseThrow(() -> exception);
        }
    }

    @Transactional
    public void pointRootToCurrentVersion(UUID logicalDatasetId, UUID versionId) {
        Dataset root = datasetRepository.findLogicalDatasetRoot(logicalDatasetId)
                .orElse(null);

        if (root != null) {
            root.pointCurrentVersionTo(versionId);
            datasetRepository.save(root);
        }
    }

    private void validateFile(MultipartFile file) {
        if (file == null || file.isEmpty()) {
            throw new IllegalArgumentException("Dataset file is required");
        }
        if (file.getSize() > maxFileSizeBytes) {
            throw new IllegalArgumentException(
                    "Dataset file exceeds the maximum allowed size of " + maxFileSizeBytes + " bytes"
            );
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
                .orElseThrow(() -> new DatasetNotFoundException("Dataset version not found with id: " + id));
    }

    public Dataset getCurrentVersion(UUID logicalDatasetId) {
        Dataset root = datasetRepository.findLogicalDatasetRoot(logicalDatasetId)
                .orElseThrow(() -> new DatasetNotFoundException(
                        "Logical dataset not found: " + logicalDatasetId
                ));

        return datasetRepository.findById(root.getCurrentVersionId())
                .orElseThrow(() -> new DatasetNotFoundException(
                        "Current dataset version not found for logical dataset: " + logicalDatasetId
                ));
    }

    public List<Dataset> getVersions(UUID logicalDatasetId) {
        return datasetRepository.findByLogicalDatasetIdOrderByVersionNumberAsc(logicalDatasetId);
    }

    public Dataset getVersion(UUID logicalDatasetId, int versionNumber) {
        return datasetRepository.findByLogicalDatasetIdAndVersionNumber(
                        logicalDatasetId,
                        versionNumber
                )
                .orElseThrow(() -> new DatasetNotFoundException(
                        "Dataset version not found: " + logicalDatasetId + "/v" + versionNumber
                ));
    }

    public List<Dataset> getAllDatasets() {
        return datasetRepository.findAll()
                .stream()
                .filter(d -> d.getId().equals(d.getLogicalDatasetId()))
                .toList();
    }
}
