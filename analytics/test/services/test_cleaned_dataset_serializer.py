import pandas as pd

from app.services.cleaned_dataset_serializer import CleanedDatasetSerializer


class TestCleanedDatasetSerializer:

    def test_should_serialize_dataframe_to_csv_bytes(self):

        df = pd.DataFrame({
            "name": ["Hariom", "Alice"],
            "age": [22, 25]
        })

        serializer = CleanedDatasetSerializer()

        result = serializer.to_csv_bytes(df)

        assert isinstance(result, bytes)

        assert result == (
            b"name,age\n"
            b"Hariom,22\n"
            b"Alice,25\n"
        )


    def test_should_not_include_dataframe_index(self):

        df = pd.DataFrame({
            "name": ["Hariom"],
            "age": [22]
        })

        serializer = CleanedDatasetSerializer()

        result = serializer.to_csv_bytes(df)

        csv_content = result.decode("utf-8")

        assert csv_content == (
            "name,age\n"
            "Hariom,22\n"
        )


    def test_should_preserve_original_dataframe(self):

        df = pd.DataFrame({
            "name": ["Hariom", "Alice"],
            "age": [22, 25]
        })

        original_df = df.copy(deep=True)

        serializer = CleanedDatasetSerializer()

        serializer.to_csv_bytes(df)

        pd.testing.assert_frame_equal(
            df,
            original_df
        )


    def test_should_handle_empty_dataframe(self):

        df = pd.DataFrame(
            columns=["name", "age"]
        )

        serializer = CleanedDatasetSerializer()

        result = serializer.to_csv_bytes(df)

        assert isinstance(result, bytes)

        assert result == b"name,age\n"