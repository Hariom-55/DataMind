package com.datamind.datamind_api.config;

import org.springframework.boot.health.contributor.Status;

@FunctionalInterface
public interface HealthStatusProvider {
    Status getStatus();
}
