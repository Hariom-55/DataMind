package com.datamind.datamind_api.dataset.repository;

import com.datamind.datamind_api.dataset.entity.Dataset;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.Lock;

import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface DatasetRepository extends JpaRepository<Dataset, UUID> {

    Optional<Dataset> findByContentHash(String contentHash);

    Optional<Dataset> findByLogicalDatasetIdAndContentHash(
            UUID logicalDatasetId,
            String contentHash
    );

    List<Dataset> findByLogicalDatasetIdOrderByVersionNumberAsc(UUID logicalDatasetId);

    Optional<Dataset> findByLogicalDatasetIdAndVersionNumber(
            UUID logicalDatasetId,
            Integer versionNumber
    );

    @Query("""
            select d
            from Dataset d
            where d.logicalDatasetId = :logicalDatasetId
              and d.id = d.logicalDatasetId
            """)
    Optional<Dataset> findLogicalDatasetRoot(
            @Param("logicalDatasetId") UUID logicalDatasetId
    );

    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("""
            select d
            from Dataset d
            where d.logicalDatasetId = :logicalDatasetId
              and d.id = d.logicalDatasetId
            """)
    Optional<Dataset> findLogicalDatasetRootForUpdate(
            @Param("logicalDatasetId") UUID logicalDatasetId
    );

    @Query("""
            select max(d.versionNumber)
            from Dataset d
            where d.logicalDatasetId = :logicalDatasetId
            """)
    Integer findMaxVersionNumber(@Param("logicalDatasetId") UUID logicalDatasetId);
}
