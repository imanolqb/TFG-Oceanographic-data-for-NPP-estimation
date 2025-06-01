import pandas as pd
import xarray as xr
from data_pipeline import ingest
import os

def clean_data(df: pd.DataFrame) -> pd.DataFrame:
    df = df.dropna(how="any")  # Elimina filas con cualquier NaN
    return df

def normalize_column(df: pd.DataFrame, column: str) -> pd.DataFrame:
    if column not in df.columns:
        raise ValueError(f"Columna no encontrada: {column}")
    df[column] = (df[column] - df[column].mean()) / df[column].std()
    return df

def filter_by_date(df: pd.DataFrame, date_column: str, start_date: str, end_date: str) -> pd.DataFrame:
    if date_column not in df.columns:
        raise ValueError(f"Columna de fecha no encontrada: {date_column}")
    df[date_column] = pd.to_datetime(df[date_column])
    mask = (df[date_column] >= start_date) & (df[date_column] <= end_date)
    return df.loc[mask]

def aggregate_data(df: pd.DataFrame, group_by: str, agg_func: str) -> pd.DataFrame:
    if group_by not in df.columns:
        raise ValueError(f"Columna de agrupación no encontrada: {group_by}")
    if agg_func not in ['mean', 'sum', 'count']:
        raise ValueError(f"Función de agregación no soportada: {agg_func}")
    
    return df.groupby(group_by).agg(agg_func).reset_index()