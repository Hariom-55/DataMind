package com.datamind.datamind_api.analysis.integration.python;

import java.util.UUID;

public record PythonAnalysisRequest(
        UUID jobId,
        UUID datasetId,
        String analysisType
){}
