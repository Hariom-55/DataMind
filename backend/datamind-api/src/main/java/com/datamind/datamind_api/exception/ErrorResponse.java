package com.datamind.datamind_api.exception;

import java.time.LocalDateTime;

public class ErrorResponse
{
    private int status ;
    private String error;
    private String message;
    private LocalDateTime timestamp;

    public ErrorResponse(
            int status,
            String error,
            String message
    )
    {
        this.status = status;
        this.error = error ;
        this.message = message;
        this.timestamp = LocalDateTime.now();
    }

    public int getStatus() {
        return status;
    }

    public LocalDateTime getTimestamp() {
        return timestamp;
    }

    public String getMessage() {
        return message;
    }

    public String getError() {
        return error;
    }
}
