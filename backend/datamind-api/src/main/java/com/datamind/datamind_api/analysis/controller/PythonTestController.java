package com.datamind.datamind_api.analysis.controller;


import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisClient;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisResponse;
import com.datamind.datamind_api.analysis.integration.python.PythonAnalysisRequest;
import org.springframework.web.bind.annotation.PostMapping;
import org.springframework.web.bind.annotation.RequestBody;
import org.springframework.web.bind.annotation.RequestMapping;
import org.springframework.web.bind.annotation.RestController;

@RestController
@RequestMapping("/api/test/python")
public class PythonTestController
{
    private final PythonAnalysisClient pythonAnalysisClient;

    public PythonTestController(
            PythonAnalysisClient pythonAnalysisClient
    ){
        this.pythonAnalysisClient = pythonAnalysisClient;
    }

    @PostMapping
    public PythonAnalysisResponse testPython(
            @RequestBody PythonAnalysisRequest request
    ){
        System.out.println("JAVA REQUEST = " + request); 
        return pythonAnalysisClient.analyze(request);
    }
}
