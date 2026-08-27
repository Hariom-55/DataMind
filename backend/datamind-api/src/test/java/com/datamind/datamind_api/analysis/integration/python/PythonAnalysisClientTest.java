package com.datamind.datamind_api.analysis.integration.python;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.restclient.test.MockServerRestClientCustomizer;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;
import org.springframework.test.web.client.MockRestServiceServer;

import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;

class PythonAnalysisClientTest
{
    private PythonAnalysisClient pythonAnalysisClient;

    private MockRestServiceServer mockServer;

    @BeforeEach
    void setUp()
    {
        MockServerRestClientCustomizer customizer =
                new MockServerRestClientCustomizer();

        RestClient.Builder builder =
                RestClient.builder()
                        .baseUrl("http://localhost:8000");

        customizer.customize(builder);

        RestClient restClient = builder.build();

        mockServer = customizer.getServer();

        pythonAnalysisClient =
                new PythonAnalysisClient(restClient);
    }

    @Test
    void shouldSuccessfullyCallPythonAnalysisService()
    {
        UUID jobId = UUID.randomUUID();
        UUID datasetId = UUID.randomUUID();

        mockServer
                .expect(requestTo("http://localhost:8000/internal/analyze"))
                .andExpect(method(org.springframework.http.HttpMethod.POST))
                .andExpect(header(
                        "Content-Type",
                        MediaType.APPLICATION_JSON_VALUE
                ))
                .andRespond(
                        withSuccess(
                                """
                                {
                                    "status": "COMPLETED",
                                    "result": {
                                        "rows": 100,
                                        "columns": 5
                                    },
                                    "error": null
                                }
                                """,
                                MediaType.APPLICATION_JSON
                        )
                );

        PythonAnalysisResponse response =
                pythonAnalysisClient.analyze(
                        jobId,
                        datasetId,
                        "EDA",
                        "./data/test.csv"
                );

        assertNotNull(response);
        assertEquals("COMPLETED", response.getStatus());
        assertNull(response.getError());
        assertNotNull(response.getResult());

        mockServer.verify();
    }

    @Test
    void shouldReturnFailedResponseFromPythonService()
    {
        UUID jobId = UUID.randomUUID();
        UUID datasetId = UUID.randomUUID();

        mockServer
                .expect(requestTo("http://localhost:8000/internal/analyze"))
                .andExpect(method(org.springframework.http.HttpMethod.POST))
                .andRespond(
                        withSuccess(
                                """
                                {
                                    "status": "FAILED",
                                    "result": null,
                                    "error": "Dataset analysis failed"
                                }
                                """,
                                MediaType.APPLICATION_JSON
                        )
                );

        PythonAnalysisResponse response =
                pythonAnalysisClient.analyze(
                        jobId,
                        datasetId,
                        "EDA",
                        "./data/test.csv"
                );

        assertNotNull(response);
        assertEquals("FAILED", response.getStatus());
        assertEquals(
                "Dataset analysis failed",
                response.getError()
        );
        assertNull(response.getResult());

        mockServer.verify();
    }

    @Test
    void shouldThrowPythonAnalysisExceptionWhenPythonServiceFails()
    {
        UUID jobId = UUID.randomUUID();
        UUID datasetId = UUID.randomUUID();

        mockServer
                .expect(requestTo("http://localhost:8000/internal/analyze"))
                .andExpect(method(org.springframework.http.HttpMethod.POST))
                .andRespond(
                        withStatus(HttpStatus.INTERNAL_SERVER_ERROR)
                );

        PythonAnalysisException exception =
                assertThrows(
                        PythonAnalysisException.class,
                        () -> pythonAnalysisClient.analyze(
                                jobId,
                                datasetId,
                                "EDA",
                                "./data/test.csv"
                        )
                );

        assertTrue(
                exception.getMessage()
                        .contains("Call to Python analysis service failed")
        );

        mockServer.verify();
    }
}