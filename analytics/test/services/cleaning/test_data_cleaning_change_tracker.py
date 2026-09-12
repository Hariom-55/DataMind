import pandas as pd

from app.services.cleaning.cleaning_change_tracker import (
    DataCleaningChangeTracker
)


class TestDataCleaningChangeTracker:

    def setup_method(self):

        self.tracker = (
            DataCleaningChangeTracker()
        )

    def test_should_track_removed_duplicates(self):

        before = pd.DataFrame({
            "name": [
                "Hariom",
                "Rahul",
                "Hariom"
            ]
        })

        after = before.drop_duplicates(
            ignore_index=True
        )

        result = self.tracker.track(
            before,
            after,
            "REMOVE_DUPLICATES"
        )

        assert result["operation"] == "REMOVE_DUPLICATES"
        assert result["column"] is None
        assert result["rowsAffected"] == 1

    def test_should_track_imputed_missing_values(self):

        before = pd.DataFrame({
            "age": [
                20,
                None,
                24
            ]
        })

        after = before.copy()

        after["age"] = (
            after["age"]
            .fillna(after["age"].median())
        )

        result = self.tracker.track(
            before,
            after,
            "IMPUTE_MISSING_VALUES",
            "age"
        )

        assert result["operation"] == "IMPUTE_MISSING_VALUES"
        assert result["column"] == "age"
        assert result["rowsAffected"] == 1

    def test_should_track_replaced_invalid_values(self):

        before = pd.DataFrame({
            "age": [
                20,
                float("inf"),
                float("-inf")
            ]
        })

        after = before.copy()

        after["age"] = (
            after["age"]
            .replace(
                [float("inf"), float("-inf")],
                pd.NA
            )
        )

        result = self.tracker.track(
            before,
            after,
            "REPLACE_INVALID_VALUES",
            "age"
        )

        assert result["rowsAffected"] == 2

    def test_should_track_normalized_categories(self):

        before = pd.DataFrame({
            "city": [
                " Delhi ",
                "DELHI",
                "Mumbai"
            ]
        })

        after = before.copy()

        after["city"] = (
            after["city"]
            .astype("string")
            .str.strip()
            .str.lower()
        )

        result = self.tracker.track(
            before,
            after,
            "NORMALIZE_CATEGORIES",
            "city"
        )

        assert result["operation"] == (
            "NORMALIZE_CATEGORIES"
        )

        assert result["column"] == "city"

        assert result["rowsAffected"] == 3

    def test_should_track_removed_feature(self):

        before = pd.DataFrame({
            "age": [20, 21, 22],
            "constant": ["A", "A", "A"]
        })

        after = before.drop(
            columns=["constant"]
        )

        result = self.tracker.track(
            before,
            after,
            "REMOVE_FEATURE",
            "constant"
        )

        assert result["operation"] == "REMOVE_FEATURE"
        assert result["column"] == "constant"
        assert result["rowsAffected"] == 3

    def test_should_return_zero_changes_for_untracked_operation(self):

        before = pd.DataFrame({
            "age": [20, 21, 22]
        })

        after = before.copy()

        result = self.tracker.track(
            before,
            after,
            "UNKNOWN_OPERATION",
            "age"
        )

        assert result["rowsAffected"] == 0