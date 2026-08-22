package com.datamind.datamind_api;

import org.springframework.boot.SpringApplication;
import org.springframework.boot.autoconfigure.SpringBootApplication;
import org.springframework.scheduling.annotation.EnableScheduling;

@SpringBootApplication
@EnableScheduling
public class DatamindApiApplication {

	public static void main(String[] args) {
		SpringApplication.run(DatamindApiApplication.class, args);
	}

}
