package com.datamind.datamind_api.config;

import org.junit.jupiter.api.Test;
import org.springframework.boot.health.contributor.Status;
import org.springframework.http.ResponseEntity;

import java.util.Map;

import static org.assertj.core.api.Assertions.assertThat;

class HealthControllerTest {

    @Test
    void shouldReturn200WhenHealthIsUp() {
        HealthController controller = new HealthController(() -> Status.UP);
        ResponseEntity<Map<String, String>> response = controller.health();

        assertThat(response.getStatusCode().value()).isEqualTo(200);
        assertThat(response.getBody()).containsEntry("status", "UP");
    }

    @Test
    void shouldReturn503WhenHealthIsDown() {
        HealthController controller = new HealthController(() -> Status.DOWN);
        ResponseEntity<Map<String, String>> response = controller.health();

        assertThat(response.getStatusCode().value()).isEqualTo(503);
        assertThat(response.getBody()).containsEntry("status", "DOWN");
    }
}
