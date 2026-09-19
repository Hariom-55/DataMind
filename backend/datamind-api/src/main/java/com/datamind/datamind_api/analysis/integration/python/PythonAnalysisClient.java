package com.datamind.datamind_api.analysis.integration.python;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisRequest;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.UUID;

@Component
public class PythonAnalysisClient {
    private static final String ANALYZE_PATH = "/internal/analyze";
    private final RestClient pythonRestClient;

    public PythonAnalysisClient(RestClient pythonRestClient) {
        this.pythonRestClient = pythonRestClient;
    }

    public PythonAnalysisResponse analyze(
            UUID jobId,
            UUID datasetId,
            String analysisType,
            String datasetPath,
            String fileType
    ) {
        return analyze(jobId, datasetId, analysisType, datasetPath, fileType, null);
    }

    public PythonAnalysisResponse analyze(
            UUID jobId,
            UUID datasetId,
            String analysisType,
            String datasetPath,
            String fileType,
            String targetColumn
    ) {
        PythonAnalysisRequest request = new PythonAnalysisRequest(
                jobId, datasetId, analysisType, datasetPath, fileType, targetColumn
        );

        try {
            PythonAnalysisResponse response = pythonRestClient
                    .post()
                    .uri(ANALYZE_PATH)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(PythonAnalysisResponse.class);

            if (response == null) {
                throw new PythonAnalysisException(
                        "Python analysis service returned an empty response for jobId=" + jobId
                );
            }
            return response;
        } catch (RestClientException ex) {
            throw new PythonAnalysisException(
                    "Call to Python analysis service failed for jobId=" + jobId, ex
            );
        }
    }
}
