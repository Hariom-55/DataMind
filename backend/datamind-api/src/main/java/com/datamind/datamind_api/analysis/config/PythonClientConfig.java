package com.datamind.datamind_api.analysis.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class PythonClientConfig {

    @Bean
    public RestClient pythonRestClient(
            RestClient.Builder builder,
            @Value("${datamind.python.base-url}") String baseUrl
    ) {
        return builder
                .baseUrl(baseUrl)
                .build();
    }
}