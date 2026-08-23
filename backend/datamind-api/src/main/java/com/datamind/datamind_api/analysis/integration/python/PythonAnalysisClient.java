package com.datamind.datamind_api.analysis.integration.python;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisRequest;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.UUID;

@Component
public class PythonAnalysisClient
{
    private static final String ANALYZE_PATH = "/internal/analyze";

    private final RestClient pythonRestClient;

    public PythonAnalysisClient(RestClient pythonRestClient)
    {
        this.pythonRestClient = pythonRestClient;
    }

    public PythonAnalysisResponse analyze(UUID jobId, UUID datasetId, String analysisType)
    {
        PythonAnalysisRequest request = new PythonAnalysisRequest(jobId, datasetId, analysisType);

        try
        {
            return pythonRestClient
                    .post()
                    .uri(ANALYZE_PATH)
                    .contentType(org.springframework.http.MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(PythonAnalysisResponse.class);
        }
        catch (RestClientException ex)
        {
            // Covers connection refused, timeout, 4xx/5xx from the Python service.
            throw new PythonAnalysisException(
                    "Call to Python analysis service failed for jobId=" + jobId, ex
            );
        }
    }
}
