import xarray as xr
import pandas as pd
from data_pipeline import ingest
from pathlib import Path

def netcdf_to_csv(input_file, output_file, delimiter=',', time_index=True):
    """
    Convierte un archivo NetCDF a CSV o TSV
    
    Args:
        input_file (str): Ruta del archivo NetCDF de entrada
        output_file (str): Ruta del archivo CSV/TSV de salida
        delimiter (str): Delimitador (',' para CSV, '\t' para TSV)
        time_index (bool): Si True, usa la dimensión de tiempo como índice
    """
    # Leer el archivo NetCDF
    ds = ingest.load_netcdf(input_file)
    
    # Convertir a DataFrame de pandas
    df = ds.to_dataframe()
    
    # Resetear índice si se solicita
    if time_index and 'time' in df.index.names:
        df = df.reset_index(level='time')
    
    # Guardar como CSV/TSV
    df.to_csv(output_file, sep=delimiter, index=False)
    print(f"Archivo convertido y guardado como: {output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Convertir NetCDF a CSV/TSV')
    parser.add_argument('input', help='Archivo NetCDF de entrada')
    parser.add_argument('output', help='Archivo CSV/TSV de salida')
    parser.add_argument('--delimiter', default=',', 
                       help='Delimitador (usar "\\t" para TSV)')
    parser.add_argument('--no_time_index', action='store_false', dest='time_index',
                       help='No usar tiempo como índice')
    
    args = parser.parse_args()
    
    netcdf_to_csv(
        input_file=args.input,
        output_file=args.output,
        delimiter=args.delimiter,
        time_index=args.time_index
    )

if __name__ == '__main__':
    main()