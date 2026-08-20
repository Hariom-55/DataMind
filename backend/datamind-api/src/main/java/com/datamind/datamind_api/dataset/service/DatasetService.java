package com.datamind.datamind_api.dataset.service;

import org.springframework.stereotype.Service;
import com.datamind.datamind_api.dataset.entity.Dataset;
import com.datamind.datamind_api.dataset.repository.DatasetRepository;
import java.util.Optional;

@Service // Specifies ye Class application ki business/Service Layer ka component hai iska Object spring Khud Manage Kare
public class DatasetService 
{
    private final DatasetRepository datasetRepository;

    public DatasetService(DatasetRepository datasetRepository)
    {
        this.datasetRepository = datasetRepository ;
    }
    
    public Dataset createDataset(
        String name,
        String contentHash,
        Long fileSize,
        String fileType
    ){
        Optional<Dataset> existingDataset = datasetRepository.findByContentHash(contentHash);

        if(existingDataset.isPresent()){
            return existingDataset.get();
        }
        
        Dataset dataset = new Dataset(name, contentHash, fileSize, fileType) ;

        return datasetRepository.save(dataset);
    }
}
