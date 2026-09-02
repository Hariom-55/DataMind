from pathlib import Path

import pandas as pd
import pytest

from app.loaders.dataset_loader import DatasetLoader


class TestDatasetLoader:

    def setup_method(self):
        self.loader = DatasetLoader()

    def test_should_load_csv(self, tmp_path):
        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,age\nHariom,22\nRahul,23\n"
        )

        df = self.loader.load(str(dataset_path))

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["name", "age"]
        assert len(df) == 2

    def test_should_raise_when_file_does_not_exist(self, tmp_path):
        dataset_path = tmp_path / "missing.csv"

        with pytest.raises(FileNotFoundError):
            self.loader.load(str(dataset_path))

    def test_should_raise_for_unsupported_format(self, tmp_path):
        dataset_path = tmp_path / "customers.txt"

        dataset_path.write_text(
            "name,age\nHariom,22\n"
        )

        with pytest.raises(ValueError, match="Unsupported dataset format"):
            self.loader.load(str(dataset_path))

    def test_should_load_xlsx(self, tmp_path):
        dataset_path = tmp_path / "customers.xlsx"

        expected_df = pd.DataFrame({
            "name": ["Hariom", "Rahul"],
            "age": [22, 23],
        })

        expected_df.to_excel(
            dataset_path,
            index=False
        )

        df = self.loader.load(str(dataset_path))

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["name", "age"]
        assert len(df) == 2
        assert df["name"].tolist() == ["Hariom", "Rahul"]
        assert df["age"].tolist() == [22, 23]

    def test_should_load_json(self, tmp_path):
        dataset_path = tmp_path / "customers.json"

        dataset_path.write_text(
            """
            [
                {"name": "Hariom", "age": 22},
                {"name": "Rahul", "age": 23}
            ]
            """
        )

        df = self.loader.load(str(dataset_path))

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["name", "age"]
        assert len(df) == 2
        assert df["name"].tolist() == ["Hariom", "Rahul"]
        assert df["age"].tolist() == [22, 23]

    def test_should_load_parquet(self, tmp_path):
        dataset_path = tmp_path / "customers.parquet"

        expected_df = pd.DataFrame({
            "name": ["Hariom", "Rahul"],
            "age": [22, 23],
        })

        expected_df.to_parquet(
            dataset_path,
            index=False
        )

        df = self.loader.load(str(dataset_path))

        assert isinstance(df, pd.DataFrame)
        assert list(df.columns) == ["name", "age"]
        assert len(df) == 2
        assert df["name"].tolist() == ["Hariom", "Rahul"]
        assert df["age"].tolist() == [22, 23]

    def test_should_load_csv_using_mime_type(self, tmp_path):
        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,age\nHariom,22\nRahul,23\n"
        )

        df = self.loader.load(str(dataset_path), file_type="text/csv")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2


    def test_should_fallback_to_extension_for_unknown_mime_type(self, tmp_path):
        dataset_path = tmp_path / "customers.csv"

        dataset_path.write_text(
            "name,age\nHariom,22\nRahul,23\n"
        )

        df = self.loader.load(str(dataset_path), file_type="unknown/mime")

        assert isinstance(df, pd.DataFrame)
        assert len(df) == 2