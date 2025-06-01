import xarray as xr
import numpy as np
from scipy.interpolate import griddata
from pathlib import Path

def nearest_interpolation(input_file, output_file, variable_name, 
                         lat_dim='latitude', lon_dim='longitude',
                         mask_var='is_ocean', method='nearest',
                         fill_nans=True, time_dim='time', verbose=True):
    """
    Realiza interpolación por vecino más cercano para rellenar valores faltantes en datos geoespaciales.
    
    Args:
        input_file (str): Ruta del archivo NetCDF de entrada
        output_file (str): Ruta del archivo NetCDF de salida
        variable_name (str): Nombre de la variable a interpolar
        lat_dim (str): Nombre de la dimensión de latitud (default: 'latitude')
        lon_dim (str): Nombre de la dimensión de longitud (default: 'longitude')
        mask_var (str): Nombre de la variable máscara (default: 'is_ocean')
        method (str): Método de interpolación ('nearest', 'linear' o 'cubic')
        fill_nans (bool): Rellenar NaNs restantes con nearest (default: True)
        time_dim (str): Nombre de la dimensión temporal (default: 'time')
        verbose (bool): Mostrar progreso (default: True)
    """
    # Cargar dataset
    ds = xr.open_dataset(input_file)
    
    # Verificar que la variable existe
    if variable_name not in ds:
        raise ValueError(f"Variable '{variable_name}' no encontrada en el dataset")
    
    # Extraer datos
    data = ds[variable_name].values
    mask = ds[mask_var].values if mask_var in ds else None
    lat = ds[lat_dim].values
    lon = ds[lon_dim].values
    
    # Crear mallas 2D de coordenadas
    lon_grid, lat_grid = np.meshgrid(lon, lat)
    
    # Determinar si hay dimensión temporal
    has_time = time_dim in ds[variable_name].dims
    time_steps = data.shape[0] if has_time else 1
    
    # Función para imprimir mensajes
    def log(message):
        if verbose:
            print(message)
    
    # Iterar sobre cada paso temporal (o una sola vez si no hay tiempo)
    for t in range(time_steps):
        if has_time:
            log(f"🕒 Procesando tiempo {t+1}/{time_steps}")
            data_slice = data[t]
        else:
            data_slice = data
        
        # Determinar máscara de valores válidos y faltantes
        if mask is not None:
            valid_mask = (mask == 1) & ~np.isnan(data_slice)
            missing_mask = (mask == 1) & np.isnan(data_slice)
        else:
            valid_mask = ~np.isnan(data_slice)
            missing_mask = np.isnan(data_slice)
        
        if not np.any(missing_mask):
            log("  ✅ No hay valores faltantes. Continuando...")
            continue
        
        if not np.any(valid_mask):
            log("  ⚠️ No hay datos válidos para interpolar. Omitiendo...")
            continue
        
        # Coordenadas y valores válidos
        points = np.column_stack((lat_grid[valid_mask], lon_grid[valid_mask]))
        values = data_slice[valid_mask]
        
        # Puntos a interpolar
        interp_points = np.column_stack((lat_grid[missing_mask], lon_grid[missing_mask]))
        
        # Interpolación principal
        interpolated_values = griddata(
            points, values, interp_points, 
            method=method if method in ['nearest', 'linear', 'cubic'] else 'nearest'
        )
        
        # Rellenar NaNs restantes con nearest si es necesario
        if fill_nans and np.any(np.isnan(interpolated_values)):
            still_nan = np.isnan(interpolated_values)
            interpolated_values[still_nan] = griddata(
                points, values, interp_points[still_nan], 
                method='nearest'
            )
        
        # Asignar valores interpolados
        filled_slice = data_slice.copy()
        filled_slice[missing_mask] = interpolated_values
        
        # Aplicar máscara si existe
        if mask is not None:
            filled_slice[mask != 1] = np.nan
        
        # Almacenar el slice interpolado
        if has_time:
            data[t] = filled_slice
        else:
            data = filled_slice
    
    # Actualizar los datos en el dataset original
    ds[variable_name].values = data
    
    # Guardar el dataset interpolado
    ds.to_netcdf(output_file)
    log(f"\n✅ Interpolación finalizada. Archivo guardado en: {output_file}")

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Interpolación por vecino más cercano')
    parser.add_argument('input', help='Archivo NetCDF de entrada')
    parser.add_argument('output', help='Archivo NetCDF de salida')
    parser.add_argument('variable', help='Nombre de la variable a interpolar')
    parser.add_argument('--lat_dim', default='latitude', 
                       help='Nombre de la dimensión de latitud')
    parser.add_argument('--lon_dim', default='longitude', 
                       help='Nombre de la dimensión de longitud')
    parser.add_argument('--mask_var', default='is_ocean', 
                       help='Nombre de la variable máscara')
    parser.add_argument('--method', default='nearest',
                       choices=['nearest', 'linear', 'cubic'],
                       help='Método de interpolación principal')
    parser.add_argument('--no_fill_nans', action='store_false', dest='fill_nans',
                       help='No rellenar NaNs restantes con nearest')
    parser.add_argument('--time_dim', default='time',
                       help='Nombre de la dimensión temporal')
    parser.add_argument('--quiet', action='store_false', dest='verbose',
                       help='Silenciar mensajes de progreso')
    
    args = parser.parse_args()
    
    nearest_interpolation(
        input_file=args.input,
        output_file=args.output,
        variable_name=args.variable,
        lat_dim=args.lat_dim,
        lon_dim=args.lon_dim,
        mask_var=args.mask_var,
        method=args.method,
        fill_nans=args.fill_nans,
        time_dim=args.time_dim,
        verbose=args.verbose
    )

if __name__ == '__main__':
    main()