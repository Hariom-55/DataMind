package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.analysis.integration.python.PythonCleaningClient;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningChange;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningOperation;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;
import org.springframework.stereotype.Service;
import org.springframework.transaction.annotation.Transactional;

import java.util.Base64;
import java.util.List;
import java.util.UUID;
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
        PythonCleaningResponse response =
                pythonCleaningClient.clean(
                        parentDataset.getId(),
                        parentDataset.getStoragePath(),
                        operations,
                        "csv"
                );

        if (response.content_hash() !=null
        && response.content_hash().equals(parentDataset.getContentHash())) {
            return parentDataset;
        }

        byte[] cleanedContent = decodeContent(
                response.content()
        );

        String storagePath =
                datasetStorageService.storeBytes(
                        cleanedContent,
                        response.content_hash(),
                        response.extension()
                );

        String operation =
                buildOperationSummary(response);

        String details =
                buildDetails(response);

        return datasetVersionService.createVersion(
                parentDataset,
                buildVersionName(parentDataset),
                response.content_hash(),
                (long) cleanedContent.length,
                response.extension(),
                storagePath,
                operation,
                null,
                calculateRowsAffected(response),
                details
        );
    }

    private byte[] decodeContent(String content)
    {
        try
        {
            return Base64.getDecoder().decode(content);
        }
        catch (IllegalArgumentException ex)
        {
            throw new IllegalArgumentException(
                    "Invalid Base64 content returned by Python cleaning service",
                    ex
            );
        }
    }

    private String buildVersionName(
            Dataset parentDataset
    )
    {
        return parentDataset.getName() + "_cleaned";
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