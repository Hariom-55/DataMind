package com.datamind.datamind_api.analysis.integration.python;

public record PythonAnalysisResponse(
        String status,
        Object result,
        Object error
)
{
}
