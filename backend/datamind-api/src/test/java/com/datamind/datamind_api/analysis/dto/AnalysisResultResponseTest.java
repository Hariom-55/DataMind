package com.datamind.datamind_api.analysis.dto;

import com.datamind.datamind_api.analysis.entity.AnalysisJob;
import com.datamind.datamind_api.analysis.entity.AnalysisResult;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisJobStatus;
import com.datamind.datamind_api.analysis.entity.enums.AnalysisType;
import com.datamind.datamind_api.dataset.entity.Dataset;
import org.junit.jupiter.api.Test;

import java.util.Map;

import static org.junit.jupiter.api.Assertions.*;

class AnalysisResultResponseTest {

    @Test
    void shouldExposeAnalysisTypeInResponse() {
        Dataset dataset = new Dataset("customers.csv", "hash", 10L, "text/csv");
        AnalysisJob job = new AnalysisJob(dataset, AnalysisType.INSIGHT, AnalysisJobStatus.COMPLETED);
        AnalysisResult result = new AnalysisResult(job, Map.of("insights", Map.of("total", 2)));

        AnalysisResultResponse response = new AnalysisResultResponse(result);

        assertEquals(AnalysisType.INSIGHT, response.getAnalysisType());
        assertEquals(job.getId(), response.getJobId());
        assertEquals(result.getResultData(), response.getResult());
        assertEquals(result.getCreatedAt(), response.getCreatedAt());
    }
}
