package com.datamind.datamind_api.config;

import org.springframework.boot.health.actuate.endpoint.HealthDescriptor;
import org.springframework.boot.health.actuate.endpoint.HealthEndpoint;
import org.springframework.boot.health.contributor.Status;
import org.springframework.http.ResponseEntity;
import org.springframework.stereotype.Component;
import org.springframework.web.bind.annotation.GetMapping;
import org.springframework.web.bind.annotation.RestController;

import java.util.Map;

@RestController
public class HealthController {

    private final HealthStatusProvider healthStatusProvider;

    public HealthController(HealthStatusProvider healthStatusProvider) {
        this.healthStatusProvider = healthStatusProvider;
    }

    @GetMapping("/health")
    public ResponseEntity<Map<String, String>> health() {
        Status status = healthStatusProvider != null ? healthStatusProvider.getStatus() : Status.UNKNOWN;
        boolean isUp = Status.UP.equals(status);

        return ResponseEntity
                .status(isUp ? 200 : 503)
                .body(Map.of("status", status != null ? status.getCode() : "UNKNOWN"));
    }

    @Component
    public static class DefaultHealthStatusProvider implements HealthStatusProvider {
        private final HealthEndpoint healthEndpoint;

        public DefaultHealthStatusProvider(HealthEndpoint healthEndpoint) {
            this.healthEndpoint = healthEndpoint;
        }

        @Override
        public Status getStatus() {
            if (healthEndpoint == null) {
                return Status.UP;
            }
            HealthDescriptor descriptor = healthEndpoint.health();
            return descriptor != null ? descriptor.getStatus() : Status.UNKNOWN;
        }
    }
}
