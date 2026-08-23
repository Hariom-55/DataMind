package com.datamind.datamind_api.analysis.integration.python;

public class PythonAnalysisException extends RuntimeException
{
    public PythonAnalysisException(String message, Throwable cause)
    {
        super(message, cause);
    }

    public PythonAnalysisException(String message)
    {
        super(message);
    }
}
