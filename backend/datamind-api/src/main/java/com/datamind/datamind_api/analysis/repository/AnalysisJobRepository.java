package com.datamind.datamind_api.analysis.repository;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;
import java.util.UUID;

public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, UUID>
{
    @Query(
            value = """
                    SELECT *
                    FROM analysis_jobs
                    WHERE status = :status
                    ORDER BY created_at ASC, id ASC
                    LIMIT 1
                    FOR UPDATE SKIP LOCKED
                    """,
            nativeQuery = true
    )
    Optional<AnalysisJob> findNextPendingJob(
            @Param("status") String status
    );
}