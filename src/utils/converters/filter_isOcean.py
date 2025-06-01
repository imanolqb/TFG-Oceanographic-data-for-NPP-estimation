import pandas as pd

def filter_isOcean_tiles(input_file, output_file, delimiter=','):
    """
    Filtra las teselas de los archivos CSV o TSV para ignorar las que no son océano
    
    Args:
        input_file (str): Ruta del archivo CSV/TSV de entrada
        output_file (str): Ruta del archivo NetCDF de salida
        delimiter (str): Delimitador (',' para CSV, '\t' para TSV)
    """
    # Leer el archivo CSV/TSV
    df = pd.read_csv(input_file, delimiter=delimiter)

    # Filtrar solo las filas donde is_ocean == 1
    df = df[df['is_ocean'] == 1]

    # Crear DataFrame de salida
    df_out = pd.DataFrame()

    # Renombrar las columnas según el esquema requerido
    if 'time' && 'grid_id' && 'sea_surface_temperature' && \
        'par' && 'fco2_ave_weighted' && 'uo' && 'vo' && \
        'CHL' && 'DIATO' && 'DINO' && 'GREEN' && 'HAPTO' && \
        'MICRO' && 'NANO' && 'PICO' && 'PROCHLO' && 'PROKAR' && \
        'npp' in df.columns:
       
        df_out["ts"] = df["time"]
        df_out["tile"] = df["grid_id"]
        df_out["env.sst"] = df["sea_surface_temperature"]
        df_out["env.par"] = df["par"]
        df_out["env.fco2"] = df["fco2_ave_weighted"]
        df_out["env.current.uo"] = df["uo"]
        df_out["env.current.vo"] = df["vo"]
        df_out["bio.chl"] = df["CHL"]
        df_out["bio.phyto.diato"] = df["DIATO"]
        df_out["bio.phyto.dino"] = df["DINO"]
        df_out["bio.phyto.green"] = df["GREEN"]
        df_out["bio.phyto.hapto"] = df["HAPTO"]
        df_out["bio.phyto.micro"] = df["MICRO"]
        df_out["bio.phyto.nano"] = df["NANO"]
        df_out["bio.phyto.pico"] = df["PICO"]
        df_out["bio.phyto.prochlo"] = df["PROCHLO"]
        df_out["bio.phyto.prokar"] = df["PROKAR"]
        df_out["bio.npp"] = df["npp"]

    # Exportar el archivo filtrado CSV/TSV
    df_out.to_csv(output_file, index=False, sep=delimiter)
    print(f"Archivo filtrado y guardado como: {output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Filtrar archivos CSV/TSV a solo océano')
    parser.add_argument('input', help='Archivo CSV/TSV de entrada')
    parser.add_argument('output', help='Archivo NetCDF de salida')
    parser.add_argument('--delimiter', default=',', 
                       help='Delimitador (usar "\\t" para TSV)')
    
    args = parser.parse_args()
    
    filter_isOcean_tiles(
        input_file=args.input,
        output_file=args.output,
        delimiter=args.delimiter
    )

if __name__ == '__main__':
    main()