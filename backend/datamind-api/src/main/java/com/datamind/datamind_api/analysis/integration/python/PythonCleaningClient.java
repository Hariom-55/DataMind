package com.datamind.datamind_api.analysis.integration.python;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningOperation;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningRequest;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningPreviewResponse;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningAssessmentResponse;
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
    private static final String PREVIEW_PATH = "/internal/clean/preview";
    private static final String ASSESSMENT_PATH = "/internal/clean/assessment";
    private static final String ARTIFACT_PATH = "/internal/artifacts/{artifactId}";

    private final RestClient pythonRestClient;

    public PythonCleaningClient(RestClient pythonRestClient)
    {
        this.pythonRestClient = pythonRestClient;
    }

    public PythonCleaningResponse clean(
            UUID datasetVersionId,
            String datasetPath,
            List<PythonCleaningOperation> operations,
            String extension)
    {
        PythonCleaningRequest request = new PythonCleaningRequest(
                datasetVersionId,
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
                    "Call to Python cleaning service failed for datasetVersionId="
                            + datasetVersionId,
                    ex
            );
        }
    }

    public byte[] downloadArtifact(String artifactId)
    {
        try
        {
            byte[] content = pythonRestClient.get()
                    .uri(ARTIFACT_PATH, artifactId)
                    .accept(MediaType.ALL)
                    .retrieve()
                    .body(byte[].class);
            if (content == null)
            {
                throw new PythonCleaningException(
                        "Python cleaning artifact was empty",
                        new IllegalStateException("Empty artifact response")
                );
            }
            return content;
        }
        catch (RestClientException ex)
        {
            throw new PythonCleaningException(
                    "Could not download cleaning artifact " + artifactId,
                    ex
            );
        }
    }

    public PythonCleaningPreviewResponse preview(
            UUID datasetVersionId,
            String datasetPath,
            List<PythonCleaningOperation> operations,
            String extension)
    {
        PythonCleaningRequest request = new PythonCleaningRequest(
                datasetVersionId, datasetPath, operations, extension
        );
        try
        {
            return pythonRestClient.post()
                    .uri(PREVIEW_PATH)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(PythonCleaningPreviewResponse.class);
        }
        catch (RestClientException ex)
        {
            throw new PythonCleaningException(
                    "Call to Python cleaning preview failed for datasetVersionId=" + datasetVersionId,
                    ex
            );
        }
    }

    public PythonCleaningAssessmentResponse assess(UUID datasetVersionId, String datasetPath)
    {
        PythonCleaningRequest request = new PythonCleaningRequest(
                datasetVersionId, datasetPath, List.of(), "csv"
        );
        try
        {
            return pythonRestClient.post()
                    .uri(ASSESSMENT_PATH)
                    .contentType(MediaType.APPLICATION_JSON)
                    .body(request)
                    .retrieve()
                    .body(PythonCleaningAssessmentResponse.class);
        }
        catch (RestClientException ex)
        {
            throw new PythonCleaningException(
                    "Call to Python cleaning assessment failed for datasetVersionId=" + datasetVersionId,
                    ex
            );
        }
    }
}
