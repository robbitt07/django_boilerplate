import pandas as pd


def assert_unique(df: pd.DataFrame, unique_col: str, file: str = None) -> None:
    try:
        assert len(df) == df[unique_col].nunique(), f"{len(df)} != {df[unique_col].nunique()}"
    except AssertionError as e:
        if file is None:
            raise e

        temp_df = df.groupby(unique_col)[unique_col].count()
        temp_index = temp_df[temp_df > 1].index
        df[df[unique_col].isin(temp_index)].to_csv(file, index=False)

        raise e
