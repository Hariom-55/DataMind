package com.datamind.datamind_api.analysis.repository;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.domain.Pageable;
import org.springframework.data.repository.query.Param;

import java.time.LocalDateTime;
import java.util.List;
import java.util.Optional;
import java.util.UUID;

public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, UUID> {

    @Query(value = """
            SELECT *
            FROM analysis_jobs
            WHERE status = :status
            ORDER BY created_at ASC, id ASC
            LIMIT 1
            FOR UPDATE SKIP LOCKED
            """, nativeQuery = true)
    Optional<AnalysisJob> findNextPendingJob(@Param("status") String status);

    List<AnalysisJob> findByStatusAndStartedAtBefore(
            AnalysisJobStatus status,
            LocalDateTime cutoff
    );

    @Query("""
            select job from AnalysisJob job
            join fetch job.dataset dataset
            join fetch job.datasetVersion version
            where dataset.logicalDatasetId = :logicalDatasetId
              and (:datasetVersionId is null or version.id = :datasetVersionId)
              and (:analysisType is null or job.analysisType = :analysisType)
              and (:status is null or job.status = :status)
            order by job.createdAt desc
            """)
    List<AnalysisJob> findHistory(
            @Param("logicalDatasetId") UUID logicalDatasetId,
            @Param("datasetVersionId") UUID datasetVersionId,
            @Param("analysisType") AnalysisType analysisType,
            @Param("status") AnalysisJobStatus status,
            Pageable pageable
    );
}
