package com.datamind.datamind_api.analysis.integration.python;

import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisResponse;
import org.springframework.http.MediaType;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

@Component
public class PythonAnalysisClient {

    private final RestClient restClient;

    public PythonAnalysisClient(RestClient restClient){
        this.restClient = restClient;
    }

    public PythonAnalysisResponse analyze(
            PythonAnalysisRequest request
    ){
        return restClient
                .post()
                .uri("/internal/analyze")
                .contentType(MediaType.APPLICATION_JSON)
                .body(request)
                .retrieve()
                .body(PythonAnalysisResponse.class);

    }
}
