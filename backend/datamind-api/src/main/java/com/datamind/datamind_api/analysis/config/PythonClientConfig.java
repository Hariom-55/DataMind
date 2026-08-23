package com.datamind.datamind_api.analysis.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.client.RestClient;

@Configuration
public class PythonClientConfig
{
    @Value("${datamind.python.base-url}")
    private String pythonBaseUrl;

    @Bean
    public RestClient pythonRestClient(RestClient.Builder restClientBuilder)
    {
        return restClientBuilder
                .baseUrl(pythonBaseUrl)
                .requestFactory(new org.springframework.http.client.SimpleClientHttpRequestFactory())
                .requestInterceptor(new PythonRequestLoggingInterceptor())
                .build();
    }
}
