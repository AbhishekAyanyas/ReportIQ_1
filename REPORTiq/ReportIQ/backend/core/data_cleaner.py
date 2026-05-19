import pandas as pd
import numpy as np

def clean_dataset(df):
    dfc = df.copy()

    dfc = dfc.dropna(axis=1, how="all")

    for col in dfc.select_dtypes(include=[np.number]):
        dfc[col] = dfc[col].fillna(dfc[col].median())

    for col in dfc.select_dtypes(include=["object"]):
        dfc[col] = dfc[col].fillna("Unknown")

    return {
        "cleaned_df": dfc,
        "summary": {
            "original_shape": df.shape,
            "cleaned_shape": dfc.shape
        }
    }

def get_data_quality_score(df):
    missing = df.isnull().sum().sum()
    total = df.size
    score = round((1 - (missing / total)) * 100, 2)
    return {"missing": int(missing), "quality_score": score}
