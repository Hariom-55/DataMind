package com.datamind.datamind_api.config;

import org.springframework.beans.factory.annotation.Value;
import org.springframework.context.annotation.Configuration;
import org.springframework.web.servlet.config.annotation.CorsRegistry;
import org.springframework.web.servlet.config.annotation.WebMvcConfigurer;
import jakarta.annotation.PostConstruct;

import java.util.Arrays;

@Configuration
public class WebConfig implements WebMvcConfigurer {

    @Value("${datamind.cors.allowed-origins:http://localhost:5173,http://127.0.0.1:5173}")
    private String allowedOrigins;

    @Value("${spring.profiles.active:}")
    private String activeProfiles;

    @PostConstruct
    void validateProductionOrigins() {
        boolean production = Arrays.stream(activeProfiles.split(","))
                .map(String::trim)
                .anyMatch("prod"::equals);
        boolean wildcard = Arrays.stream(allowedOrigins.split(","))
                .map(String::trim)
                .anyMatch("*"::equals);
        if (production && wildcard) {
            throw new IllegalStateException(
                    "DATAMIND_CORS_ALLOWED_ORIGINS must not contain a wildcard in production"
            );
        }
    }

    @Override
    public void addCorsMappings(CorsRegistry registry) {
        registry.addMapping("/**")
                .allowedOrigins(Arrays.stream(allowedOrigins.split(","))
                        .map(String::trim)
                        .filter(origin -> !origin.isEmpty())
                        .toArray(String[]::new))
                .allowedMethods(
                        "GET",
                        "POST",
                        "PUT",
                        "DELETE",
                        "OPTIONS"
                )
                .allowedHeaders("*");
    }
}
