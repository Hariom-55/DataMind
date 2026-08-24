package com.datamind.datamind_api.exception;

import com.datamind.datamind_api.analysis.exception.AnalysisJobNotFoundException;
import com.datamind.datamind_api.dataset.exception.DatasetNotFoundException;
import org.springframework.http.HttpStatus;
import org.springframework.web.bind.annotation.*;

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
}
