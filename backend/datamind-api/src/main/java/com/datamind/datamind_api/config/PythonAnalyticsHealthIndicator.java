package com.datamind.datamind_api.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.beans.factory.annotation.Value;
import org.springframework.boot.autoconfigure.condition.ConditionalOnProperty;
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.HealthIndicator;
import org.springframework.http.client.SimpleClientHttpRequestFactory;
import org.springframework.stereotype.Component;
import org.springframework.web.client.RestClient;

import java.time.Duration;
import java.util.Map;

@Component
@ConditionalOnProperty(name = "datamind.health.python.enabled", havingValue = "true", matchIfMissing = true)
public class PythonAnalyticsHealthIndicator implements HealthIndicator {

    private static final Logger log = LoggerFactory.getLogger(PythonAnalyticsHealthIndicator.class);

    private final RestClient healthRestClient;
    private final String pythonBaseUrl;

    public PythonAnalyticsHealthIndicator(
            @Value("${datamind.python.base-url:http://127.0.0.1:8000}") String pythonBaseUrl,
            @Value("${datamind.python.health-check-timeout:2s}") Duration timeout
    ) {
        this.pythonBaseUrl = pythonBaseUrl;
        SimpleClientHttpRequestFactory requestFactory = new SimpleClientHttpRequestFactory();
        requestFactory.setConnectTimeout(timeout);
        requestFactory.setReadTimeout(timeout);

        this.healthRestClient = RestClient.builder()
                .baseUrl(pythonBaseUrl)
                .requestFactory(requestFactory)
                .build();
    }

    @Override
    public Health health() {
        try {
            @SuppressWarnings("unchecked")
            Map<String, Object> response = healthRestClient.get()
                    .uri("/health")
                    .retrieve()
                    .body(Map.class);

            if (response != null && "UP".equalsIgnoreCase(String.valueOf(response.get("status")))) {
                return Health.up()
                        .withDetail("url", pythonBaseUrl)
                        .withDetail("service", response.getOrDefault("service", "datamind-analysis"))
                        .build();
            }

            return Health.down()
                    .withDetail("url", pythonBaseUrl)
                    .withDetail("error", "Unexpected response from Python analytics service: " + response)
                    .build();
        } catch (Exception ex) {
            log.debug("Python analytics health check failed: {}", ex.getMessage());
            return Health.down()
                    .withDetail("url", pythonBaseUrl)
                    .withDetail("error", ex.getMessage())
                    .build();
        }
    }
}
