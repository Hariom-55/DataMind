package com.datamind.datamind_api.dataset.repository;


import org.springframework.data.jpa.repository.JpaRepository;
import com.datamind.datamind_api.dataset.entity.Dataset;
import java.util.UUID;
import java.util.Optional;

public interface  DatasetRepository extends JpaRepository<Dataset, UUID>
{
    Optional<Dataset> findByContentHash(String contentHash);
}
