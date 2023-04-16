import numpy as np
import pandas as pd


def clean_dataframe(df):
    for index in df.index:
        df.loc[index] = df.loc[index].apply(lambda x: x.replace("%", ""))
        df.loc[index] = df.loc[index].apply(lambda x: x.replace(",", ""))
        df.loc[index] = df.loc[index].apply(lambda x: np.nan if x == "" else x)
        df.loc[index] = df.loc[index].apply(lambda x: float(x))
        df.loc[index] = df.loc[index].apply(pd.to_numeric)
    return df.astype(float)
