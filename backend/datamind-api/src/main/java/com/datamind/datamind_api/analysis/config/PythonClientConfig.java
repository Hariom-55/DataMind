package com.datamind.datamind_api.analysis.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Bean;
import org.springframework.context.annotation.Configuration;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.web.client.RestClient;

import java.time.Duration;

@Configuration
public class PythonClientConfig {

    @Value("${datamind.python.base-url}")
    private String pythonBaseUrl;

    @Value("${datamind.python.connect-timeout:5s}")
    private Duration connectTimeout;

    @Value("${datamind.python.read-timeout:10m}")
    private Duration readTimeout;

    @Bean
    public RestClient pythonRestClient(RestClient.Builder restClientBuilder) {
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(connectTimeout);
        requestFactory.setReadTimeout(readTimeout);

        return restClientBuilder
                .baseUrl(pythonBaseUrl)
                .requestFactory(requestFactory)
                .requestInterceptor(new PythonRequestLoggingInterceptor())
                .build();
    }
}
