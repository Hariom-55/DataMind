package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.analysis.integration.python.PythonCleaningClient;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningChange;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningOperation;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningPreviewResponse;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningAssessmentResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.security.MessageDigest;
import java.security.NoSuchAlgorithmException;
import java.util.HexFormat;
import java.util.List;
import java.util.UUID;
import java.util.Map;
import java.util.LinkedHashMap;
import java.util.stream.Collectors;

@Service
public class DatasetCleaningOrchestrationService
{
    private final PythonCleaningClient pythonCleaningClient;
    private final DatasetStorageService datasetStorageService;
    private final DatasetVersionService datasetVersionService;

    public DatasetCleaningOrchestrationService(
            PythonCleaningClient pythonCleaningClient,
            DatasetStorageService datasetStorageService,
            DatasetVersionService datasetVersionService
    )
    {
        this.pythonCleaningClient = pythonCleaningClient;
        this.datasetStorageService = datasetStorageService;
        this.datasetVersionService = datasetVersionService;
    }

    @Transactional
    public Dataset cleanDataset(
            Dataset parentDataset,
            List<PythonCleaningOperation> operations
    )
    {
        return cleanDatasetWithResult(parentDataset, operations).dataset();
    }

    public PythonCleaningAssessmentResponse assessDataset(Dataset dataset)
    {
        return pythonCleaningClient.assess(dataset.getId(), dataset.getStoragePath());
    }

    public PythonCleaningPreviewResponse previewDataset(
            Dataset dataset,
            List<PythonCleaningOperation> operations
    )
    {
        if (operations == null || operations.isEmpty())
        {
            throw new IllegalArgumentException("At least one cleaning operation is required");
        }
        return pythonCleaningClient.preview(
                dataset.getId(), dataset.getStoragePath(), operations, "csv"
        );
    }

    @Transactional
    public DatasetCleaningExecution cleanDatasetWithResult(
            Dataset parentDataset,
            List<PythonCleaningOperation> operations
    )
    {
        if (parentDataset == null)
        {
            throw new IllegalArgumentException("Dataset version is required");
        }
        if (operations == null || operations.isEmpty())
        {
            throw new IllegalArgumentException("At least one cleaning operation is required");
        }
        PythonCleaningResponse response =
                pythonCleaningClient.clean(
                        parentDataset.getId(),
                        parentDataset.getStoragePath(),
                        operations,
                        "csv"
                );

        if (!"CSV".equals(response.format())
                || !"csv".equalsIgnoreCase(response.extension())
                || !"text/csv".equalsIgnoreCase(response.content_type()))
        {
            throw new IllegalArgumentException(
                    "Python cleaning service returned an unsupported output format"
            );
        }

        if (response.sha256() == null || response.sha256().isBlank())
        {
            throw new IllegalArgumentException("Python cleaning service returned no content hash");
        }

        byte[] cleanedContent = pythonCleaningClient.downloadArtifact(response.artifact_id());
        if (response.size_bytes() >= 0 && response.size_bytes() != cleanedContent.length)
        {
            throw new IllegalArgumentException("Python cleaning artifact size does not match metadata");
        }
        if (response.size_bytes() >= 0 && !response.sha256().equals(sha256(cleanedContent)))
        {
            throw new IllegalArgumentException("Python cleaning artifact hash does not match metadata");
        }
        if (response.sha256().equals(parentDataset.getContentHash())) {
            return new DatasetCleaningExecution(parentDataset, response);
        }

        String storagePath =
                datasetStorageService.storeBytes(
                        cleanedContent,
                        response.sha256(),
                        response.extension()
                );

        String operation =
                buildOperationSummary(response);

        String details =
                buildDetails(response);

        Dataset cleanedDataset = datasetVersionService.createVersion(
                parentDataset,
                buildVersionName(parentDataset),
                response.sha256(),
                (long) cleanedContent.length,
                response.content_type(),
                storagePath,
                operation,
                null,
                calculateRowsAffected(response),
                details,
                operations.stream().map(this::toOperationConfig).toList()
        );
        return new DatasetCleaningExecution(cleanedDataset, response);
    }

    private Map<String, Object> toOperationConfig(PythonCleaningOperation operation) {
        Map<String, Object> config = new LinkedHashMap<>();
        config.put("operation", operation.operation());
        if (operation.column() != null) config.put("column", operation.column());
        config.put("parameters", operation.parameters() == null ? Map.of() : operation.parameters());
        return config;
    }

    private String sha256(byte[] content)
    {
        try
        {
            return HexFormat.of().formatHex(
                    MessageDigest.getInstance("SHA-256").digest(content)
            );
        } catch (NoSuchAlgorithmException ex) {
            throw new IllegalStateException("SHA-256 is unavailable", ex);
        }
    }

    private String buildVersionName(
            Dataset parentDataset
    )
    {
        String name = parentDataset.getName();
        int extensionIndex = name.lastIndexOf('.');
        String baseName = extensionIndex > 0 ? name.substring(0, extensionIndex) : name;
        return baseName + ".csv";
    }

    private String buildOperationSummary(
            PythonCleaningResponse response
    )
    {
        if (response.changes() == null || response.changes().isEmpty())
        {
            return "CLEAN_DATASET";
        }

        return response.changes()
                .stream()
                .map(PythonCleaningChange::operation)
                .distinct()
                .collect(Collectors.joining(","));
    }

    private Integer calculateRowsAffected(
            PythonCleaningResponse response
    )
    {
        if (response.changes() == null)
        {
            return 0;
        }

        return response.changes()
                .stream()
                .map(PythonCleaningChange::rowsAffected)
                .filter(value -> value != null)
                .reduce(0, Integer::sum);
    }

    private String buildDetails(
            PythonCleaningResponse response
    )
    {
        if (response.changes() == null ||
                response.changes().isEmpty())
        {
            return "Cleaning completed with no recorded changes";
        }

        return response.changes()
                .stream()
                .map(change ->
                        String.format(
                                "operation=%s, column=%s, rowsAffected=%d, details=%s",
                                change.operation(),
                                change.column(),
                                change.rowsAffected(),
                                change.details()
                        )
                )
                .collect(Collectors.joining("; "));
    }
}
