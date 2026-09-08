package com.datamind.datamind_api.analysis.integration.python;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningOperation;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningRequest;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;
import org.springframework.web.client.RestClientException;

import java.util.List;
import java.util.UUID;

@Component
public class PythonCleaningClient
{
    private static final String CLEAN_PATH = "/internal/clean";

    private final RestClient pythonRestClient;

    public PythonCleaningClient(RestClient pythonRestClient)
    {
        this.pythonRestClient = pythonRestClient;
    }

    public PythonCleaningResponse clean(
            UUID datasetId,
            String datasetPath,
            List<PythonCleaningOperation> operations,
            String extension)
    {
        PythonCleaningRequest request = new PythonCleaningRequest(
                datasetId,
                datasetPath,
                operations,
                extension
        );

        try
        {
            return pythonRestClient
                    .post()
                    .uri(CLEAN_PATH)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(PythonCleaningResponse.class);
        }
        catch (RestClientException ex)
        {
            throw new PythonCleaningException(
                    "Call to Python cleaning service failed for datasetId="
                            + datasetId,
                    ex
            );
        }
    }
}