import xarray as xr
import numpy as np
from scipy.interpolate import RBFInterpolator
import argparse
from pathlib import Path

def rbf_interpolation(input_file, output_file, variable_name, 
                      lat_dim='latitude', lon_dim='longitude',
                      mask_var='is_ocean', max_points=5000, 
                      smoothing=1e-2, kernel='thin_plate_spline',
                      time_dim='time', verbose=True):
    """
    Realiza interpolación RBF para rellenar valores faltantes en datos geoespaciales.
    
    Args:
        input_file (str): Ruta del archivo NetCDF de entrada
        output_file (str): Ruta del archivo NetCDF de salida
        variable_name (str): Nombre de la variable a interpolar
        lat_dim (str): Nombre de la dimensión de latitud (default: 'latitude')
        lon_dim (str): Nombre de la dimensión de longitud (default: 'longitude')
        mask_var (str): Nombre de la variable máscara (default: 'is_ocean')
        max_points (int): Máximo de puntos válidos a usar (default: 5000)
        smoothing (float): Parámetro de suavizado (default: 1e-2)
        kernel (str): Tipo de kernel RBF (default: 'thin_plate_spline')
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
    mask = ds[mask_var].values.astype(bool) if mask_var in ds else None
    lat = ds[lat_dim].values
    lon = ds[lon_dim].values
    
    # Crear mallas 2D de coordenadas
    lon2d, lat2d = np.meshgrid(lon, lat)
    
    # Copia para almacenar datos interpolados
    filled_data = data.copy()
    
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
            slice_data = data[t]
        else:
            slice_data = data
        
        # Determinar máscara de valores válidos y faltantes
        if mask is not None:
            valid_mask = mask & ~np.isnan(slice_data)
            missing_mask = mask & np.isnan(slice_data)
        else:
            valid_mask = ~np.isnan(slice_data)
            missing_mask = np.isnan(slice_data)
        
        if np.sum(valid_mask) < 10:
            log("  ⚠️ Muy pocos datos válidos. Se omite este paso.")
            continue
        
        # Coordenadas y valores válidos
        valid_points = np.column_stack((lon2d[valid_mask], lat2d[valid_mask]))
        valid_values = slice_data[valid_mask]
        
        # Puntos faltantes
        target_points = np.column_stack((lon2d[missing_mask], lat2d[missing_mask]))
        
        # Submuestreo si hay demasiados puntos válidos
        if len(valid_points) > max_points:
            indices = np.random.choice(len(valid_points), max_points, replace=False)
            sample_points = valid_points[indices]
            sample_values = valid_values[indices]
        else:
            sample_points = valid_points
            sample_values = valid_values
        
        # Crear interpolador RBF
        try:
            rbf = RBFInterpolator(sample_points, sample_values, 
                                 kernel=kernel, smoothing=smoothing)
            interp_values = rbf(target_points)
        except Exception as e:
            log(f"  ⚠️ Error en la interpolación RBF: {e}")
            continue
        
        # Asignar valores interpolados
        filled_slice = slice_data.copy()
        filled_slice[missing_mask] = interp_values
        
        # Aplicar máscara si existe
        if mask is not None:
            filled_slice[~mask] = np.nan
        
        # Almacenar el slice interpolado
        if has_time:
            filled_data[t] = filled_slice
        else:
            filled_data = filled_slice
    
    # Reemplazar los datos en el dataset original
    ds[variable_name].values = filled_data
    
    # Guardar el dataset interpolado
    ds.to_netcdf(output_file)
    log(f"\n✅ Interpolación finalizada. Archivo guardado en: {output_file}")

def main():
    parser = argparse.ArgumentParser(description='Interpolación RBF para datos geoespaciales')
    parser.add_argument('input', help='Archivo NetCDF de entrada')
    parser.add_argument('output', help='Archivo NetCDF de salida')
    parser.add_argument('variable', help='Nombre de la variable a interpolar')
    parser.add_argument('--lat_dim', default='latitude', 
                       help='Nombre de la dimensión de latitud')
    parser.add_argument('--lon_dim', default='longitude', 
                       help='Nombre de la dimensión de longitud')
    parser.add_argument('--mask_var', default='is_ocean', 
                       help='Nombre de la variable máscara')
    parser.add_argument('--max_points', type=int, default=5000,
                       help='Máximo de puntos válidos a usar')
    parser.add_argument('--smoothing', type=float, default=1e-2,
                       help='Parámetro de suavizado')
    parser.add_argument('--kernel', default='thin_plate_spline',
                       help='Tipo de kernel RBF')
    parser.add_argument('--time_dim', default='time',
                       help='Nombre de la dimensión temporal')
    parser.add_argument('--quiet', action='store_false', dest='verbose',
                       help='Silenciar mensajes de progreso')
    
    args = parser.parse_args()
    
    rbf_interpolation(
        input_file=args.input,
        output_file=args.output,
        variable_name=args.variable,
        lat_dim=args.lat_dim,
        lon_dim=args.lon_dim,
        mask_var=args.mask_var,
        max_points=args.max_points,
        smoothing=args.smoothing,
        kernel=args.kernel,
        time_dim=args.time_dim,
        verbose=args.verbose
    )

if __name__ == '__main__':
    main()