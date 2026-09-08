package com.datamind.datamind_api.analysis.integration.python;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningOperation;
import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import org.junit.jupiter.api.BeforeEach;
import org.junit.jupiter.api.Test;
import org.springframework.boot.restclient.test.MockServerRestClientCustomizer;
import org.springframework.http.HttpMethod;
import org.springframework.http.HttpStatus;
import org.springframework.http.MediaType;
import org.springframework.web.client.RestClient;
import org.springframework.test.web.client.MockRestServiceServer;

import java.util.List;
import java.util.UUID;

import static org.junit.jupiter.api.Assertions.*;
import static org.springframework.test.web.client.match.MockRestRequestMatchers.*;
import static org.springframework.test.web.client.response.MockRestResponseCreators.*;
public class PythonCleaningClientTest
{
    private PythonCleaningClient pythonCleaningClient;

    private MockRestServiceServer mockServer;

    @BeforeEach
    void setup()
    {
        MockServerRestClientCustomizer customizer =
                new MockServerRestClientCustomizer();

        RestClient.Builder builder = RestClient.builder()
                .baseUrl("http://localhost:8000");

        customizer.customize(builder);

        RestClient restClient = builder.build();

        mockServer = customizer.getServer();

        pythonCleaningClient = new PythonCleaningClient(restClient);
    }


    @Test
    void shouldSuccessfullyCallPythonCleaningService()
    {
        UUID datasetId = UUID.randomUUID();

        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "IMPUTE_MISSING_VALUES",
                                "age"
                        )
                );

        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/internal/clean"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andExpect(
                        header(
                                "Content-Type",
                                MediaType.APPLICATION_JSON_VALUE
                        )
                )
                .andRespond(
                        withSuccess(
                                """
                                {
                                    "content": "bmFtZSxhZ2UKSGFyaW9tLDIyCg==",
                                    "content_hash": "abc123",
                                    "extension": "csv",
                                    "original_rows": 10,
                                    "cleaned_rows": 10,
                                    "original_columns": 3,
                                    "cleaned_columns": 3,
                                    "operations_applied": 1,
                                    "changes": [
                                        {
                                            "operation": "IMPUTE_MISSING_VALUES",
                                            "column": "age",
                                            "rowsAffected": 1,
                                            "details": "1 missing value imputed"
                                        }
                                    ]
                                }
                                """,
                                MediaType.APPLICATION_JSON
                        )
                );

        PythonCleaningResponse response =
                pythonCleaningClient.clean(
                        datasetId,
                        "./data/test.csv",
                        operations,
                        "csv"
                );

        assertNotNull(response);

        assertEquals(
                "abc123",
                response.content_hash()
        );

        assertEquals(
                "csv",
                response.extension()
        );

        assertEquals(
                10,
                response.original_rows()
        );

        assertEquals(
                10,
                response.cleaned_rows()
        );

        assertEquals(
                3,
                response.original_columns()
        );

        assertEquals(
                3,
                response.cleaned_columns()
        );

        assertEquals(
                1,
                response.operations_applied()
        );

        assertNotNull(response.content());

        assertNotNull(response.changes());

        assertEquals(
                1,
                response.changes().size()
        );

        assertEquals(
                "IMPUTE_MISSING_VALUES",
                response.changes().get(0).operation()
        );

        assertEquals(
                "age",
                response.changes().get(0).column()
        );

        assertEquals(
                1,
                response.changes().get(0).rowsAffected()
        );

        mockServer.verify();
    }


    @Test
    void shouldReturnCleaningResponseWithMultipleChanges()
    {
        UUID datasetId = UUID.randomUUID();

        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "NORMALIZE_CATEGORIES",
                                "city"
                        ),
                        new PythonCleaningOperation(
                                "IMPUTE_MISSING_VALUES",
                                "age"
                        )
                );

        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/internal/clean"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(
                        withSuccess(
                                """
                                {
                                    "content": "Y2l0eSxhZ2UKZGVsaGksMjIK",
                                    "content_hash": "def456",
                                    "extension": "csv",
                                    "original_rows": 20,
                                    "cleaned_rows": 20,
                                    "original_columns": 4,
                                    "cleaned_columns": 4,
                                    "operations_applied": 2,
                                    "changes": [
                                        {
                                            "operation": "NORMALIZE_CATEGORIES",
                                            "column": "city",
                                            "rowsAffected": 3,
                                            "details": "3 categorical values normalized"
                                        },
                                        {
                                            "operation": "IMPUTE_MISSING_VALUES",
                                            "column": "age",
                                            "rowsAffected": 2,
                                            "details": "2 missing values imputed"
                                        }
                                    ]
                                }
                                """,
                                MediaType.APPLICATION_JSON
                        )
                );

        PythonCleaningResponse response =
                pythonCleaningClient.clean(
                        datasetId,
                        "./data/test.csv",
                        operations,
                        "csv"
                );

        assertNotNull(response);

        assertEquals(
                2,
                response.operations_applied()
        );

        assertEquals(
                2,
                response.changes().size()
        );

        assertEquals(
                "NORMALIZE_CATEGORIES",
                response.changes().get(0).operation()
        );

        assertEquals(
                "IMPUTE_MISSING_VALUES",
                response.changes().get(1).operation()
        );

        mockServer.verify();
    }


    @Test
    void shouldThrowPythonCleaningExceptionWhenPythonServiceFails()
    {
        UUID datasetId = UUID.randomUUID();

        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "REMOVE_DUPLICATES",
                                null
                        )
                );

        mockServer
                .expect(
                        requestTo(
                                "http://localhost:8000/internal/clean"
                        )
                )
                .andExpect(
                        method(HttpMethod.POST)
                )
                .andRespond(
                        withStatus(
                                HttpStatus.INTERNAL_SERVER_ERROR
                        )
                );

        PythonCleaningException exception =
                assertThrows(
                        PythonCleaningException.class,
                        () -> pythonCleaningClient.clean(
                                datasetId,
                                "./data/test.csv",
                                operations,
                                "csv"
                        )
                );

        assertTrue(
                exception.getMessage()
                        .contains(
                                "Call to Python cleaning service failed"
                        )
        );

        mockServer.verify();
    }

    @Test
    void shouldSendCleaningRequestUsingPythonFieldNames() {
        UUID datasetId =
                UUID.fromString("11111111-1111-1111-1111-111111111111");

        String datasetPath = "C:\\temp\\dataset.csv";

        List<PythonCleaningOperation> operations =
                List.of(
                        new PythonCleaningOperation(
                                "IMPUTE_MISSING_VALUES",
                                "age"
                        )
                );

        mockServer.expect(
                        requestTo("http://localhost:8000/internal/clean")
                )
                .andExpect(method(HttpMethod.POST))
                .andExpect(content().contentType(MediaType.APPLICATION_JSON))
                .andExpect(
                        content().json(
                                """
                                {
                                  "dataset_id": "11111111-1111-1111-1111-111111111111",
                                  "dataset_path": "C:\\\\temp\\\\dataset.csv",
                                  "operations": [
                                    {
                                      "operation": "IMPUTE_MISSING_VALUES",
                                      "column": "age"
                                    }
                                  ],
                                  "extension": "csv"
                                }
                                """
                        )
                )
                .andRespond(
                        withSuccess(
                                """
                                {
                                  "content": "dGVzdA==",
                                  "content_hash": "test-hash",
                                  "extension": "csv",
                                  "original_rows": 1,
                                  "cleaned_rows": 1,
                                  "original_columns": 2,
                                  "cleaned_columns": 2,
                                  "operations_applied": 1,
                                  "changes": []
                                }
                                """,
                                MediaType.APPLICATION_JSON
                        )
                );

        pythonCleaningClient.clean(
                datasetId,
                datasetPath,
                operations,
                "csv"
        );

        mockServer.verify();
    }
}

