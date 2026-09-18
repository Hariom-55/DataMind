package com.datamind.datamind_api.analysis.integration.python;

import java.util.Map;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.assertEquals;
import static org.junit.jupiter.api.Assertions.assertNotNull;
import static org.junit.jupiter.api.Assertions.assertNull;
import static org.junit.jupiter.api.Assertions.assertThrows;
import static org.junit.jupiter.api.Assertions.assertTrue;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.restclient.test.MockServerRestClientCustomizer;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.test.web.client.MockRestServiceServer;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.header;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.method;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.requestTo;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withStatus;
import static org.springframework.test.web.client.response.MockRestResponseCreators.withSuccess;
import org.springframework.web.client.RestClient;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonAnalysisResponse;

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
                        "./data/test.csv",
                        "text/csv"
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
                        "./data/test.csv",
                        "text/csv"
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
                                "./data/test.csv",
                                "text/csv"
                        )
                );

        assertTrue(
                exception.getMessage()
                        .contains("Call to Python analysis service failed")
        );

        mockServer.verify();
    }

    @Test
    void shouldSuccessfullyCallPythonInsightAnalysisService()
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
                                        "analysis": {
                                            "eda": {
                                                "overview": {
                                                    "rowCount": 100
                                                }
                                            },
                                            "statistical": {
                                                "correlations": {}
                                            }
                                        },
                                        "insights": {
                                            "summary": {
                                                "totalInsights": 2,
                                                "high": 1,
                                                "medium": 1,
                                                "low": 0,
                                                "info": 0
                                            },
                                            "insights": [
                                                {
                                                    "id": "INSIGHT-001",
                                                    "category": "DATA_QUALITY",
                                                    "severity": "HIGH",
                                                    "source": "EDA",
                                                    "title": "High missing-value rate"
                                                },
                                                {
                                                    "id": "INSIGHT-002",
                                                    "category": "STATISTICAL",
                                                    "severity": "INFO",
                                                    "source": "STATISTICS",
                                                    "title": "Strong correlation detected"
                                                }
                                            ]
                                        }
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
                        "INSIGHT",
                        "./data/test.csv",
                        "text/csv"
                );

        assertNotNull(response);
        assertEquals("COMPLETED", response.getStatus());
        assertNull(response.getError());
        assertNotNull(response.getResult());

        assertTrue(response.getResult().containsKey("insights"));

        Map<String, Object> insights =
                (Map<String, Object>) response.getResult().get("insights");

        assertNotNull(insights);
        assertTrue(insights.containsKey("summary"));
        assertTrue(insights.containsKey("insights"));

        mockServer.verify();
    }

    
}