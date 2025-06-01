import xarray as xr
import numpy as np
from data_pipeline import ingest

def normalize_netcdf_dimensions(ds: xr.Dataset) -> xr.Dataset:
    """
    Normaliza las dimensiones de un dataset NetCDF.
    
    Args:
        ds (xarray.Dataset): Dataset NetCDF a normalizar.
    """
    # Verificar si las dimensiones lat y lon existen
    if 'lat' not in ds.dims or 'lon' not in ds.dims:
        raise ValueError("El dataset NetCDF debe contener dimensiones 'lat' y 'lon'.")
    # Verificar si la dimensión time existe
    if 'time' not in ds.dims:
        raise ValueError("El dataset NetCDF debe contener la dimensión 'time'.")
    # Renombrar dimensiones y coordenadas
    ds = ds.rename({
        "lat": "latitude",
        "lon": "longitude"
    })

    # Añadir atributos a latitude
    if "latitude" in ds:
        ds.latitude.attrs = {
            "units": "degrees_north",
            "standard_name": "latitude",
            "long_name": "latitude",
            "axis": "Y"
        }

    # Añadir atributos a longitude
    if "longitude" in ds:
        ds.longitude.attrs = {
            "units": "degrees_east",
            "standard_name": "longitude",
            "long_name": "longitude",
            "axis": "X"
        }

    # Modificar atributos de time
    if "time" in ds:
        ds.time.attrs.update({
            "standard_name": "time",
            "long_name": "Time",
            "axis": "T",
            "unit_long": "Days Since 1900-01-01"
        })
        ds.time.attrs.pop("units", None)
        ds.time.attrs.pop("calendar", None)

    return ds

def normalize_netcdf_variables(ds: xr.Dataset, variable: str, attributes: dict) -> xr.Dataset:
    """
    Normaliza las variables de un dataset NetCDF.
    
    Args:
        ds (xarray.Dataset): Dataset NetCDF a normalizar.
        variable (str): Nombre de la variable a normalizar.
        attributes (dict): Atributos a añadir a la variable.
    
    Returns:
        xarray.Dataset: Dataset NetCDF con la variable normalizada.
    """
    if variable not in ds:
        raise ValueError(f"Variable no encontrada: {variable}")
    
    ds[variable].attrs.update(attributes)
    return ds

def concat_netcdfs_by_time(file_list, output_path):
    """
    Concatena una lista de archivos NetCDF por la dimensión 'time'.
    Args:
        file_list (list): Lista de rutas de archivos NetCDF.
    Returns:
        xarray.Dataset: Dataset concatenado.
    """
    datasets = [xr.open_dataset(file) for file in file_list]
    combined = xr.concat(datasets, dim='time')
    ingest.save_netcdf(combined, output_path)
    return combined

def add_grid_id_to_netcdf(input_path, output_path, lat_dim='latitude', lon_dim='longitude', var_name='grid_id'):
    """
    Añade una variable grid_id alfanumérica (tipo 'A1', 'B3', 'AA25', ...) a un NetCDF 2D.

    Args:
        input_path (str): Ruta del archivo NetCDF de entrada.
        output_path (str): Ruta del archivo NetCDF de salida.
        lat_dim (str): Nombre de la dimensión de latitud.
        lon_dim (str): Nombre de la dimensión de longitud.
        var_name (str): Nombre de la variable grid_id a crear.
    """
    def number_to_letters(n):
        letters = []
        while n > 0:
            n -= 1
            letters.append(chr(ord('A') + (n % 26)))
            n = n // 26
        return ''.join(reversed(letters))

    ds = xr.open_dataset(input_path)

    n_rows = ds.sizes[lat_dim]
    n_cols = ds.sizes[lon_dim]
    grid_ids_alfa = np.empty((n_rows, n_cols), dtype=object)

    for i in range(n_rows):
        for j in range(n_cols):
            letras = number_to_letters(j + 1)
            grid_ids_alfa[i, j] = f"{letras}{i + 1}"

    ds[var_name] = ((lat_dim, lon_dim), grid_ids_alfa)
    ds[var_name].attrs = {
        'long_name': 'Unique grid cell identifier (Hundir la flota style)',
        'units': '1',
        'description': 'Unique alphanumeric ID for each grid point (e.g., A1, B3, AA25)'
    }

    ds.to_netcdf(output_path, encoding={var_name: {'dtype': 'str'}})
    ds.close()

def select_netcdf_by_time_range(ds: xr.Dataset, start_time: str, end_time: str) -> xr.Dataset:
    """
    Selecciona un rango de tiempo específico de un dataset NetCDF.
    
    Args:
        ds (xarray.Dataset): Dataset NetCDF a filtrar.
        start_time (str): Fecha de inicio en formato 'YYYY-MM-DD'.
        end_time (str): Fecha de fin en formato 'YYYY-MM-DD'.
    
    Returns:
        xarray.Dataset: Dataset filtrado por el rango de tiempo.
    """
    if not np.issubdtype(ds['time'].dtype, np.datetime64):
        ds['time'] = xr.conventions.times.decode_cf_datetime(ds['time'], ds['time'].attrs.get('units', None))
    ds_sel = ds.sel(time=slice(start_time, end_time))
    if ds_sel['time'].size == 0:
        raise ValueError(f"No hay datos en el rango de tiempo {start_time} a {end_time}.")
    return ds_sel

def filter_netcdf_by_grid_id(ds: xr.Dataset, grid_id: str) -> xr.Dataset:
    """
    Filtra un dataset NetCDF por un grid_id específico.
    
    Args:
        ds (xarray.Dataset): Dataset NetCDF a filtrar.
        grid_id (str): Grid ID a filtrar.
    
    Returns:
        xarray.Dataset: Dataset filtrado por el grid_id.
    """
    if 'grid_id' not in ds:
        raise ValueError("El dataset NetCDF no contiene la variable 'grid_id'.")
    
    ds_filtered = ds.where(ds['grid_id'] == grid_id, drop=True)
    
    if ds_filtered['grid_id'].size == 0:
        raise ValueError(f"No hay datos para el grid_id {grid_id}.")
    return ds_filtered



def filter_netcdf_by_lat_lon_range(ds: xr.Dataset, lat_min: float, lat_max: float, lon_min: float, lon_max: float, tolerance: float = 0.01) -> xr.Dataset:
    """
    Filtra un dataset NetCDF por un rango de latitud y longitud.
    
    Args:
        ds (xarray.Dataset): Dataset NetCDF a filtrar.
        lat_min (float): Latitud mínima del filtro.
        lat_max (float): Latitud máxima del filtro.
        lon_min (float): Longitud mínima del filtro.
        lon_max (float): Longitud máxima del filtro.
        tolerance (float): Tolerancia para el filtrado de latitud y longitud.
    
    Returns:
        xarray.Dataset: Dataset filtrado por el rango de latitud y longitud.
    """
    if 'latitude' not in ds or 'longitude' not in ds:
        raise ValueError("El dataset NetCDF debe contener las dimensiones 'latitude' y 'longitude'.")
    
    ds_filtered = ds.where(
        (ds['latitude'] >= lat_min - tolerance) & (ds['latitude'] <= lat_max + tolerance) &
        (ds['longitude'] >= lon_min - tolerance) & (ds['longitude'] <= lon_max + tolerance),
        drop=True
    )
    
    if ds_filtered['latitude'].size == 0 or ds_filtered['longitude'].size == 0:
        raise ValueError(f"No hay datos en el rango de latitud {lat_min} a {lat_max} y longitud {lon_min} a {lon_max}.")
    
    return ds_filtered



def filter_netcdf_by_variable(ds: xr.Dataset, variable: str, min_value: float, max_value: float) -> xr.Dataset:
    """
    Filtra un dataset NetCDF por un rango de valores de una variable específica.
    
    Args:
        ds (xarray.Dataset): Dataset NetCDF a filtrar.
        variable (str): Nombre de la variable a filtrar.
        min_value (float): Valor mínimo del filtro.
        max_value (float): Valor máximo del filtro.
    
    Returns:
        xarray.Dataset: Dataset filtrado por el rango de valores de la variable.
    """
    if variable not in ds:
        raise ValueError(f"Variable no encontrada: {variable}")
    
    ds_filtered = ds.where((ds[variable] >= min_value) & (ds[variable] <= max_value), drop=True)
    if ds_filtered.isnull().all():
        raise ValueError(f"No hay datos en el rango de valores {min_value} a {max_value} para la variable {variable}.")
    
    return ds_filtered