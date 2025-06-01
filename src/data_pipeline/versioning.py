import pandas as pd
from datetime import datetime
import os

def save_versioned(df: pd.DataFrame, name: str, folder="results/") -> str:
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    filename = f"{name}_{timestamp}.csv"
    full_path = os.path.join(folder, filename)
    os.makedirs(folder, exist_ok=True)
    df.to_csv(full_path, index=False)
    return full_path
