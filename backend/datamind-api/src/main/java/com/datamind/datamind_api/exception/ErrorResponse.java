package com.datamind.datamind_api.exception;

import org.slf4j.MDC;

import java.time.LocalDateTime;

public class ErrorResponse {
    private final int status;
    private final String error;
    private final String message;
    private final LocalDateTime timestamp;
    private final String requestId;

    public ErrorResponse(int status, String error, String message) {
        this.status = status;
        this.error = error;
        this.message = message;
        this.timestamp = LocalDateTime.now();
        this.requestId = MDC.get("requestId");
    }

    public int getStatus() { return status; }
    public LocalDateTime getTimestamp() { return timestamp; }
    public String getMessage() { return message; }
    public String getError() { return error; }
    public String getRequestId() { return requestId; }
}
