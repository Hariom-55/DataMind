import pandas as pd


def safe_float(value):
    if pd.isna(value):
        return None
    return float(value)
