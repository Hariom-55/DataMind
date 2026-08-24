package com.datamind.datamind_api.analysis.config;

import org.slf4j.Logger;
import org.slf4j.LoggerFactory;
import org.springframework.http.HttpRequest;
import org.springframework.http.client.ClientHttpRequestExecution;
import org.springframework.http.client.ClientHttpRequestInterceptor;
import org.springframework.http.client.ClientHttpResponse;

import java.io.IOException;
import java.nio.charset.StandardCharsets;


public class PythonRequestLoggingInterceptor implements ClientHttpRequestInterceptor
{
    private static final Logger log = LoggerFactory.getLogger(PythonRequestLoggingInterceptor.class);

    @Override
    public ClientHttpResponse intercept(
            HttpRequest request, byte[] body, ClientHttpRequestExecution execution
    ) throws IOException
    {
        log.debug("--> {} {}", request.getMethod(), request.getURI());
        log.debug("--> headers: {}", request.getHeaders());
        log.debug("--> body ({} bytes): {}", body.length, new String(body, StandardCharsets.UTF_8));

        ClientHttpResponse response = execution.execute(request, body);

        log.debug("<-- status: {}", response.getStatusCode());
        return response;
    }
}
