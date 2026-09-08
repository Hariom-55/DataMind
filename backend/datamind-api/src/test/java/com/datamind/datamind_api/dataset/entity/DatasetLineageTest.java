package com.datamind.datamind_api.dataset.entity;

import org.junit.jupiter.api.Test;

import static org.junit.jupiter.api.Assertions.*;

class DatasetLineageTest {

    @Test
    void shouldCreateDatasetLineage() {

        Dataset parent = new Dataset(
                "customers.csv",
                "parent-hash",
                100L,
                "text/csv"
        );

        Dataset child = new Dataset(
                "customers_cleaned.csv",
                "child-hash",
                90L,
                "text/csv"
        );

        DatasetLineage lineage = new DatasetLineage(
                parent,
                child,
                "REMOVE_DUPLICATES",
                null,
                10,
                "10 duplicate rows removed"
        );

        assertSame(
                parent,
                lineage.getParentDataset()
        );

        assertSame(
                child,
                lineage.getChildDataset()
        );

        assertEquals(
                "REMOVE_DUPLICATES",
                lineage.getOperation()
        );

        assertNull(
                lineage.getColumnName()
        );

        assertEquals(
                10,
                lineage.getRowsAffected()
        );

        assertEquals(
                "10 duplicate rows removed",
                lineage.getDetails()
        );

        assertNotNull(
                lineage.getCreatedAt()
        );
    }
}