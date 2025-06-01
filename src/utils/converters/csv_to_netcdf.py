import xarray as xr
import pandas as pd
import numpy as np
from data_pipeline import ingest
from pathlib import Path

def csv_to_netcdf(input_file, output_file, delimiter=',', time_column=None, 
                  time_format=None, variable_columns=None, global_attrs=None):
    """
    Convierte un archivo CSV o TSV a NetCDF
    
    Args:
        input_file (str): Ruta del archivo CSV/TSV de entrada
        output_file (str): Ruta del archivo NetCDF de salida
        delimiter (str): Delimitador (',' para CSV, '\t' para TSV)
        time_column (str): Nombre de la columna con datos de tiempo (opcional)
        time_format (str): Formato del tiempo (ej. '%Y-%m-%d') si time_column se especifica
        variable_columns (list): Lista de columnas a incluir como variables (None para todas)
        global_attrs (dict): Atributos globales para agregar al NetCDF
    """
    # Leer el archivo CSV/TSV
    df = ingest.load_measurements(input_file)
    if df.empty:
        raise ValueError(f"El archivo {input_file} está vacío o no contiene datos válidos.")
    
    # Procesar columna de tiempo si se especifica
    if time_column is not None:
        df[time_column] = pd.to_datetime(df[time_column], format=time_format)
        df = df.set_index(time_column)
    
    # Filtrar columnas si se especifica
    if variable_columns is not None:
        df = df[variable_columns]
    
    # Convertir a xarray Dataset
    ds = xr.Dataset.from_dataframe(df)
    
    # Agregar atributos globales si se especifican
    if global_attrs is not None:
        ds.attrs.update(global_attrs)
    
    # Guardar como NetCDF
    ds.to_netcdf(output_file)
    print(f"Archivo convertido y guardado como: {output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convertir CSV/TSV a NetCDF')
    parser.add_argument('input', help='Archivo CSV/TSV de entrada')
    parser.add_argument('output', help='Archivo NetCDF de salida')
    parser.add_argument('--delimiter', default=',', 
                       help='Delimitador (usar "\\t" para TSV)')
    parser.add_argument('--time_column', 
                       help='Nombre de la columna de tiempo')
    parser.add_argument('--time_format', 
                       help='Formato del tiempo (ej. %%Y-%%m-%%d)')
    parser.add_argument('--variables', nargs='+',
                       help='Lista de variables a incluir')
    
    args = parser.parse_args()
    
    csv_to_netcdf(
        input_file=args.input,
        output_file=args.output,
        delimiter=args.delimiter,
        time_column=args.time_column,
        time_format=args.time_format,
        variable_columns=args.variables
    )

if __name__ == '__main__':
    main()