"""
Functions to preprocess dataframes from parquet files to be read as inputs to the model
"""

import pandas as pd
import pyarrow.parquet as pq

def get_pq_df(filepath):
    """
    Reads parquet file from filepath
    filepath: str of parquet file location
    returns: pd.DataFrame
    """
    tbl = pq.read_table(filepath)
    return tbl.to_pandas()


def convert_type(df, int_cols=None, float_cols=None):
    """
    Converts datatype of given dataframe to int or float types
    df: pd.DataFrame
    int_cols: list of column names to convert to type int
    float_cols: list of column names to convert to type float
    """
    if not(int_cols)==None:
        for col in int_cols:
            df[col] = df[col].astype(int)
    if not(float_cols)==None:
        for col in float_cols:
            df[col] = df[col].astype(float)
    return df