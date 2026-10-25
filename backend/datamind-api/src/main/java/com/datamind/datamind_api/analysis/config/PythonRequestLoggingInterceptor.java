package com.datamind.datamind_api.analysis.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpHeaders;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;

import java.io.IOException;

public class PythonRequestLoggingInterceptor implements ClientHttpRequestInterceptor {

    private static final Logger log =
            LoggerFactory.getLogger(PythonRequestLoggingInterceptor.class);

    private static final String INTERNAL_API_KEY = "X-Internal-API-Key";

    @Override
    public ClientHttpResponse intercept(
            HttpRequest request,
            byte[] body,
            ClientHttpRequestExecution execution
    ) throws IOException {

        HttpHeaders safeHeaders = new HttpHeaders();
        safeHeaders.putAll(request.getHeaders());
        safeHeaders.set(INTERNAL_API_KEY, "[REDACTED]");

        log.debug("--> {} {}", request.getMethod(), request.getURI());
        log.debug("--> headers: {}", safeHeaders);
        // Request bodies can contain user data and internal filesystem paths.
        // Log only the byte count so sensitive values never enter application logs.
        log.debug("--> body ({} bytes)", body.length);

        ClientHttpResponse response = execution.execute(request, body);

        log.debug("<-- status: {}", response.getStatusCode());

        return response;
    }
}
