import pandas as pd

def check_required_columns(df: pd.DataFrame, required: list) -> bool:
    missing = [col for col in required if col not in df.columns]
    if missing:
        raise ValueError(f"Faltan columnas requeridas: {missing}")
    return True

def check_value_ranges(df: pd.DataFrame, column: str, min_val: float, max_val: float) -> bool:
    if not df[column].between(min_val, max_val).all():
        raise ValueError(f"Valores fuera de rango en columna {column}")
    return True
