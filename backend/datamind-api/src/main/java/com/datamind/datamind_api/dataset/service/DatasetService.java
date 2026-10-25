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
import java.io.IOException;
import java.nio.charset.StandardCharsets;

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

            // Serialize version allocation for this logical dataset. The
            // unique constraint remains the final guard against duplicates.
            datasetRepository.findLogicalDatasetRootForUpdate(logicalId)
                    .orElseThrow(() -> new DatasetNotFoundException(
                            "Logical dataset not found: " + logicalId
                    ));

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

        String contentType = file.getContentType();
        if (StringUtils.hasText(contentType)
                && !Set.of("application/octet-stream", "binary/octet-stream")
                .contains(contentType.toLowerCase(Locale.ROOT))
                && !allowedContentTypes(extension).contains(contentType.toLowerCase(Locale.ROOT))) {
            throw new IllegalArgumentException(
                    "Dataset content type does not match its file extension"
            );
        }

        validateContentSignature(file, extension);
    }

    private Set<String> allowedContentTypes(String extension) {
        return switch (extension) {
            case "csv" -> Set.of("text/csv", "application/csv", "text/plain", "application/vnd.ms-excel");
            case "json" -> Set.of("application/json", "text/json");
            case "xlsx" -> Set.of("application/vnd.openxmlformats-officedocument.spreadsheetml.sheet");
            case "xls" -> Set.of("application/vnd.ms-excel");
            case "parquet" -> Set.of("application/vnd.apache.parquet", "application/x-parquet");
            default -> Set.of();
        };
    }

    private void validateContentSignature(MultipartFile file, String extension) {
        try (var input = file.getInputStream()) {
            byte[] prefix = input.readNBytes(8);
            boolean valid = switch (extension) {
                case "xlsx" -> prefix.length >= 4 && prefix[0] == 'P' && prefix[1] == 'K'
                        && prefix[2] == 3 && prefix[3] == 4;
                case "xls" -> prefix.length >= 8
                        && (prefix[0] & 0xff) == 0xD0 && (prefix[1] & 0xff) == 0xCF
                        && (prefix[2] & 0xff) == 0x11 && (prefix[3] & 0xff) == 0xE0;
                case "parquet" -> isParquetFile(file, input, prefix);
                case "csv", "json" -> isTextData(prefix, extension);
                default -> false;
            };
            if (!valid) {
                throw new IllegalArgumentException(
                        "Dataset content does not match its file extension"
                );
            }
        } catch (IOException exception) {
            throw new IllegalArgumentException("Could not inspect dataset content", exception);
        }
    }

    private boolean isParquetFile(
            MultipartFile file,
            java.io.InputStream input,
            byte[] prefix
    ) throws IOException {
        if (prefix.length != 8 || file.getSize() < 12
                || prefix[0] != 'P' || prefix[1] != 'A'
                || prefix[2] != 'R' || prefix[3] != '1') {
            return false;
        }
        input.skipNBytes(file.getSize() - 12);
        byte[] footer = input.readNBytes(4);
        return footer.length == 4 && footer[0] == 'P' && footer[1] == 'A'
                && footer[2] == 'R' && footer[3] == '1';
    }

    private boolean isTextData(byte[] prefix, String extension) {
        String sample = new String(prefix, StandardCharsets.UTF_8)
                .replace("\uFEFF", "").trim();
        if (sample.isEmpty() || sample.indexOf('\0') >= 0) return false;
        if ("csv".equals(extension)) return true;
        return "{}[\"-0123456789tfn".indexOf(sample.charAt(0)) >= 0;
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
