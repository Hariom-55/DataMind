package com.datamind.datamind_api.dataset.service;

import com.datamind.datamind_api.analysis.integration.python.dto.PythonCleaningResponse;
import com.datamind.datamind_api.dataset.entity.Dataset;

public record DatasetCleaningExecution(
        Dataset dataset,
        PythonCleaningResponse cleaningResult
) {
}
