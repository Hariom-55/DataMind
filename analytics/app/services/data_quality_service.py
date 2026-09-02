import pandas as pd

class DataQualityService:

    def analyze(
            self,
            df: pd.DataFrame,
            duplicate_rows: int | None = None
    ) -> dict :

        row_count = len(df)
        column_count = len(df.columns)
        total_cells = row_count * column_count 

        missing_cells = int(df.isnull().sum().sum())

        if total_cells > 0 :
            completeness = (
                (total_cells - missing_cells) / total_cells
            )* 100

        else:
            completeness = 0.0 

        if duplicate_rows is None:
            duplicate_rows = int(df.duplicated().sum())

        if row_count > 0 :
            duplicate_percentage = (
                duplicate_rows /row_count
            )* 100

        else :
            duplicate_percentage = 0.0 

        duplicate_free_pecentage = (
            100.0 - duplicate_percentage
        )

        if row_count == 0 :
            overall_score = 0.0
        else:
            overall_score = (
                completeness * 0.70
                + duplicate_free_pecentage * 0.30
            )

        return {
            "score": round(overall_score, 2),
            "completeness": round(completeness,2),
            "missingCells": missing_cells,
            "duplicateRows": int(duplicate_rows),
            "duplicatePercentage": round(duplicate_percentage,2),
            "duplicateFreePercentage": round(duplicate_free_pecentage,2),
        }