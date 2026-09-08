import io

import pandas as pd


class CleanedDatasetSerializer:

    def to_csv_bytes(self, df: pd.DataFrame) -> bytes:
        """
        Serialize a DataFrame into CSV bytes.

        The original DataFrame is not modified.
        """

        buffer = io.StringIO()

        df.to_csv(
            buffer,
            index=False,
            lineterminator="\n"
        )

        return buffer.getvalue().encode("utf-8")