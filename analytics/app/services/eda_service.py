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

        #5. Duplicate rows
        duplicate_rows = int(df.duplicated().sum())

        #6. Numerical statistics
        numeric_df = df.select_dtypes(include="number")

        numeric_statistics = {}

        if not numeric_df.empty:
            statistics = numeric_df.describe()

            numeric_statistics = {
                column : {
                    statistics : float(value)
                    for statistics , value in statistics[column].items()
                }
                for column in numeric_df.columns
            }

        return {
            "overview": overview,
            "columns":columns,
            "dataTypes": data_types,
            "missingValues": missing_values,
            "duplicateRows": duplicate_rows,
            "numericStatistics": numeric_statistics,
        }