package com.datamind.datamind_api.analysis.repository;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import org.springframework.data.jpa.repository.JpaRepository;

import java.util.Optional;
import java.util.UUID;

public interface AnalysisJobRepository extends JpaRepository<AnalysisJob, UUID>
{
    Optional<AnalysisJob> findFirstByStatusOrderByCreatedAtAsc(
            AnalysisJobStatus status
    );

}
