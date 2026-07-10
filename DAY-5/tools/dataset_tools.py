from utils.mcp import mcp
import pandas as pd


@mcp.tool()
def dataset_summary(csv_path: str):
    """
    Summarize a CSV dataset.
    """

    df = pd.read_csv(csv_path)

    return {
        "rows": len(df),
        "columns": len(df.columns),
        "column_names": list(df.columns),
        "missing_values": df.isnull().sum().to_dict(),
        "duplicates": int(df.duplicated().sum()),
    }


@mcp.tool()
def detect_target_column(csv_path: str):
    """
    Guess the target column.
    """

    df = pd.read_csv(csv_path)

    return {
        "suggested_target": df.columns[-1]
    }