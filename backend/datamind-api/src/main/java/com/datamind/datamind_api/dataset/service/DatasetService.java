package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import com.datamind.datamind_api.dataset.util.FileHashUtil;
import org.springframework.dao.DataIntegrityViolationException;
import org.springframework.stereotype.Service;
import org.springframework.web.multipart.MultipartFile;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

@Service
public class DatasetService
{
    private final DatasetRepository datasetRepository;
    private final DatasetStorageService datasetStorageService;

    public DatasetService(
            DatasetRepository datasetRepository,
            DatasetStorageService datasetStorageService
    ){
        this.datasetRepository = datasetRepository;
        this.datasetStorageService = datasetStorageService;
    }

    public Dataset uploadDataset(MultipartFile file)
    {
        validateFile(file);

        String contentHash = FileHashUtil.sha256(file);

        Optional<Dataset> existingDataset = datasetRepository.findByContentHash(contentHash);
        if (existingDataset.isPresent())
        {
            return existingDataset.get();
        }

        String originalFilename = file.getOriginalFilename();
        Long fileSize = file.getSize();
        String fileType = file.getContentType();
        if (fileType == null)
        {
            fileType = "application/octet-stream";
        }

        Dataset dataset = new Dataset(
                originalFilename,
                contentHash,
                fileSize,
                fileType
        );

        String storagePath = datasetStorageService.store(file, contentHash);
        dataset.setStoragePath(storagePath);

        try
        {
            return datasetRepository.save(dataset);
        }
        catch (DataIntegrityViolationException exception)
        {
            return datasetRepository.findByContentHash(contentHash)
                    .orElseThrow(() -> exception);
        }
    }

    private void validateFile(MultipartFile file)
    {
        if (file == null || file.isEmpty())
        {
            throw new IllegalArgumentException(
                    "Dataset file is required"
            );
        }

        if (file.getOriginalFilename() == null || file.getOriginalFilename().isBlank())
        {
            throw new IllegalArgumentException(
                    "Dataset file name is required"
            );
        }
    }

    public Dataset getDatasetById(UUID id)
    {
        return datasetRepository.findById(id)
                .orElseThrow(
                        () -> new DatasetNotFoundException(
                                "Dataset not found with id: " + id
                        )
                );
    }

    public List<Dataset> getAllDatasets()
    {
        return datasetRepository.findAll();
    }
}
