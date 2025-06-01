import pandas as pd
import xarray as xr
import os

def load_measurements(file_path: str) -> pd.DataFrame:
    if file_path.endswith(".tsv"):
        return pd.read_csv(file_path, sep='\t')
    elif file_path.endswith(".csv"):
        return pd.read_csv(file_path)
    else:
        raise ValueError(f"Formato no soportado: {file_path}")

def load_metadata(metadata_path: str) -> dict:
    import json
    with open(metadata_path, 'r') as f:
        return json.load(f)

def load_netcdf(file_path: str):
    return xr.open_dataset(file_path)

def save_measurements(df: pd.DataFrame, output_path: str, delimiter: str = ',') -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    if output_path.endswith(".tsv"):
        df.to_csv(output_path, sep='\t', index=False)
    elif output_path.endswith(".csv"):
        df.to_csv(output_path, sep=delimiter, index=False)
    else:
        raise ValueError(f"Formato no soportado para guardar: {output_path}")
    print(f"DataFrame guardado en: {output_path}")

def save_netcdf(ds: xr.Dataset, output_path: str) -> None:
    os.makedirs(os.path.dirname(output_path), exist_ok=True)
    ds.to_netcdf(output_path)
    print(f"Dataset NetCDF guardado en: {output_path}")