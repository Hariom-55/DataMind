package com.datamind.datamind_api.dataset.util;

import org.springframework.web.multipart.MultipartFile;

import java.io.InputStream;
import java.security.MessageDigest;

public final class FileHashUtil {

    private FileHashUtil() {
    }

    public static String sha256(MultipartFile file) {

        try {

            MessageDigest digest =
                    MessageDigest.getInstance("SHA-256");

            try (InputStream inputStream = file.getInputStream()) {

                byte[] buffer = new byte[8192];

                int bytesRead;

                while ((bytesRead = inputStream.read(buffer)) != -1) {

                    digest.update(buffer, 0, bytesRead);
                }
            }

            byte[] hash = digest.digest();

            StringBuilder hexString = new StringBuilder();

            for (byte b : hash) {

                hexString.append(
                        String.format("%02x", b)
                );
            }

            return hexString.toString();

        } catch (Exception e) {

            throw new RuntimeException(
                    "Failed to calculate file hash",
                    e
            );
        }
    }
}