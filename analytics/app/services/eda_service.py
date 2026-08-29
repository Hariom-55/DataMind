import pandas as pd 

class EDAService :
    def analyze(self, dataset_path: str)->dict:

        #1.Load Dataset
        df = pd.read_csv(dataset_path)

        #2. Dataset overview 
        overview = {
            "rowCount": int(df.shape[0]),
            "columnCount": int(df.shape[1]),
        }

        #3. Column information
        columns = list(df.columns)

        data_types = {
            column :str(dtype)
            for column , dtype in df.dtypes.items()
        }

        #4. Missing Values 
        missing_values = {
            column: int(count)
            for column, count in df.isnull().sum().items()
        }

        #5.Missing Value Percentage
        row_count = len(df)

        missing_percentages = {
            column : ( 
                float(round((count/row_count)*100,2))
                if row_count > 0
                else 0.0
            )
            for column, count in df.isnull().sum().items()
        }

        #6. Unique Value Counts 
        unique_value_counts = {
            column: int(df[column].nunique(dropna=True))
            for column in df.columns
        }

        #7. Duplicate rows
        duplicate_rows = int(df.duplicated().sum())

        #8. Numerical statistics
        numeric_df = df.select_dtypes(include="number")

        numeric_statistics = {}

        if not numeric_df.empty:
            statistics = numeric_df.describe()

            numeric_statistics = {
                column : {
                    statistics : float(value)
                    for statistics , value 
                    in statistics[column].items()
                    if pd.notna(value)
                }
                for column in numeric_df.columns
            }

        #9. Categorical Statistics 
        categorical_df = df.select_dtypes(
            include=["object","str", "category","bool"]
        )

        categorical_statistics = {} 

        for column in categorical_df.columns:

            value_counts = (df[column].value_counts(dropna=False)
                            .head(10)
                            )

            top_values = {
                str(value): int(count)
                for value, count in value_counts.items()
            }

            categorical_statistics[column] = {
                "uniqueCount" : int(df[column].nunique(dropna=True)),
                "topValues": top_values
            }

        return {
            "overview": overview,
            "columns":columns,
            "dataTypes": data_types,
            "missingValues": missing_values,
            "missingPercentages": missing_percentages,
            "uniqueValueCounts": unique_value_counts,
            "duplicateRows": duplicate_rows,
            "numericStatistics": numeric_statistics,
            "categoricalStatistics": categorical_statistics,
        }