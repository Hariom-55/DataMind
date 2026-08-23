package com.datamind.datamind_api.analysis.repository;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import jakarta.persistence.LockModeType;
import org.springframework.data.jpa.repository.JpaRepository;
import org.springframework.data.jpa.repository.Lock;
import org.springframework.data.jpa.repository.Query;
import org.springframework.data.repository.query.Param;

import java.util.Optional;
import java.util.UUID;

public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, UUID>
{
    @Lock(LockModeType.PESSIMISTIC_WRITE)
    @Query("""
            SELECT job 
            FROM AnalysisJob job
            WHERE job.status = :status
            ORDER BY job.createdAt ASC
            """)
    Optional<AnalysisJob> findNextPendingJob(
            @Param("status") AnalysisJobStatus status
    );


}
