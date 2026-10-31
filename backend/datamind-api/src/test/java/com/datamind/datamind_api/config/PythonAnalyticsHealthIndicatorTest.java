package com.datamind.datamind_api.config;

import org.junit.jupiter.api.Test;
import org.springframework.boot.health.contributor.Health;
import org.springframework.boot.health.contributor.Status;

import java.time.Duration;

import static org.assertj.core.api.Assertions.assertThat;

class PythonAnalyticsHealthIndicatorTest {

    @Test
    void shouldReportDownWhenServiceUnreachable() {
        PythonAnalyticsHealthIndicator indicator = new PythonAnalyticsHealthIndicator(
                "http://127.0.0.1:59999",
                Duration.ofMillis(100)
        );

        Health health = indicator.health();
        assertThat(health.getStatus()).isEqualTo(Status.DOWN);
        assertThat(health.getDetails()).containsKey("url");
        assertThat(health.getDetails()).containsKey("error");
    }
}
