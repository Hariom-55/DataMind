package com.datamind.datamind_api.exception;

import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.analysis.exception.AnalysisResultNotFoundException;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.http.converter.HttpMessageNotReadableException;
import org.springframework.web.bind.annotation.*;
import org.springframework.web.bind.MethodArgumentNotValidException;
import org.springframework.web.multipart.support.MissingServletRequestPartException;

@RestControllerAdvice
public class GlobalExceptionHandler
{
    @ExceptionHandler(DatasetNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleDatasetNotFound(DatasetNotFoundException exception)
    {
        return new ErrorResponse(
                404,
                "DATASET_NOT_FOUND",
                exception.getMessage()
        );
    }

    @ExceptionHandler(AnalysisJobNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleAnalysisJobNotFound(
            AnalysisJobNotFoundException exception
    ){
        return new ErrorResponse(
                404,
                "ANALYSIS_JOB_NOT_FOUND",
                exception.getMessage()
        );
    }

    @ExceptionHandler(IllegalArgumentException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleIllegalArgument(IllegalArgumentException exception)
    {

        return new ErrorResponse(
                400,
                "INVALID_REQUEST",
                exception.getMessage()
        );
    }

    @ExceptionHandler(MissingServletRequestPartException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleMissingServletRequestPart(
            MissingServletRequestPartException exception
    ){
        return new ErrorResponse(
                400,
                "INVALID_REQUEST",
                "Dataset file is required"
        );
    }

    @ExceptionHandler(AnalysisResultNotFoundException.class)
    @ResponseStatus(HttpStatus.NOT_FOUND)
    public ErrorResponse handleAnalysisResultNotFound(
            AnalysisResultNotFoundException exception
    ){
        return new ErrorResponse(
                404,
                "ANALYSIS_RESULT_NOT_FOUND",
                exception.getMessage()
        );
    }

    @ExceptionHandler(MethodArgumentNotValidException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleValidationException(
            MethodArgumentNotValidException exception
    ){
        String message = exception.getBindingResult()
                .getFieldErrors()
                .stream()
                .map(error -> error.getField()+ ": "+error.getDefaultMessage())
                .findFirst()
                .orElse("Validation Failed");

        return new ErrorResponse(
                400,
                "VALIDATION_ERROR",
                message
        );
    }

    @ExceptionHandler(HttpMessageNotReadableException.class)
    @ResponseStatus(HttpStatus.BAD_REQUEST)
    public ErrorResponse handleMessageNotReadable(
            HttpMessageNotReadableException exception
    ){
        return new ErrorResponse(
                400,
                "INVALID_REQUEST",
                "Request body contains invalid or malformed data"
        );
    }

    @ExceptionHandler(Exception.class)
    @ResponseStatus(HttpStatus.INTERNAL_SERVER_ERROR)
    public ErrorResponse handleUnexpectedException(Exception exception)
    {
        return new ErrorResponse(
                500,
                "INTERNAL_SERVER_ERROR",
                "An unexpected error occurred"
        );
    }
}
