import os
import numpy as np
import xarray as xr
from typing import List, Tuple, Optional
import argparse

class GridInterpolator:
    def __init__(self, input_files: List[str], output_dir: Optional[str] = None):
        """
        Inicializa el interpolador de mallas
        
        Args:
            input_files (List[str]): Lista de rutas a archivos NetCDF
            output_dir (str, optional): Directorio de salida (None para mismo directorio que entrada)
        """
        self.input_files = input_files
        self.output_dir = output_dir
        
        # Crear directorio de salida si se especifica
        if self.output_dir is not None:
            os.makedirs(self.output_dir, exist_ok=True)
    
    def interpolate_grid(self, lon_range: Tuple[float, float], lat_range: Tuple[float, float], 
                       n_points: int = 480, method: str = "linear") -> None:
        """
        Interpola los datasets a una nueva malla definida
        
        Args:
            lon_range (Tuple[float, float]): Rango de longitudes (min, max)
            lat_range (Tuple[float, float]): Rango de latitudes (min, max)
            n_points (int): Número de puntos en cada dimensión
            method (str): Método de interpolación ('linear', 'nearest', etc.)
        """
        for input_file in self.input_files:
            try:
                # Determinar archivo de salida
                base_name = os.path.basename(input_file)
                name, ext = os.path.splitext(base_name)
                output_filename = f"{name}_interpolated{ext}"
                
                if self.output_dir is not None:
                    output_path = os.path.join(self.output_dir, output_filename)
                else:
                    output_path = os.path.join(os.path.dirname(input_file), output_filename)
                
                print(f"Procesando: {input_file} -> {output_path}")
                
                # Cargar dataset
                ds = xr.open_dataset(input_file)
                
                # Crear nuevas coordenadas
                new_lons = np.linspace(lon_range[0], lon_range[1], n_points)
                new_lats = np.linspace(lat_range[0], lat_range[1], n_points)
                
                # Interpolar
                ds_interp = ds.interp(
                    longitude=new_lons,
                    latitude=new_lats,
                    method=method
                )
                
                # Guardar resultado
                ds_interp.to_netcdf(output_path)
                print(f"✓ Interpolación completada. Dimensiones resultantes: {ds_interp.dims}")
                
            except Exception as e:
                print(f"✗ Error procesando {input_file}: {str(e)}")
    
    @classmethod
    def from_command_line(cls):
        """Método de fábrica para crear instancia desde línea de comandos"""
        parser = argparse.ArgumentParser(description='Herramienta para redefinir mallas de datos geoespaciales')
        parser.add_argument('input_files', nargs='+', help='Archivos NetCDF de entrada')
        parser.add_argument('--output_dir', help='Directorio de salida (opcional)')
        parser.add_argument('--lon_min', type=float, required=True, help='Longitud mínima')
        parser.add_argument('--lon_max', type=float, required=True, help='Longitud máxima')
        parser.add_argument('--lat_min', type=float, required=True, help='Latitud mínima')
        parser.add_argument('--lat_max', type=float, required=True, help='Latitud máxima')
        parser.add_argument('--n_points', type=int, default=480, help='Número de puntos por dimensión')
        parser.add_argument('--method', default='linear', 
                          choices=['linear', 'nearest', 'cubic', 'quadratic'],
                          help='Método de interpolación')
        
        args = parser.parse_args()
        
        return cls(
            input_files=args.input_files,
            output_dir=args.output_dir
        ).interpolate_grid(
            lon_range=(args.lon_min, args.lon_max),
            lat_range=(args.lat_min, args.lat_max),
            n_points=args.n_points,
            method=args.method
        )

def main():
    # Ejemplos de uso programático
    interpolator = GridInterpolator(
        input_files=["datos1.nc", "datos2.nc"],
        output_dir="datos_interpolados"
    )
    
    interpolator.interpolate_grid(
        lon_range=(-27, -7),
        lat_range=(13, 33),
        n_points=480,
        method="linear"
    )

if __name__ == '__main__':
    GridInterpolator.from_command_line()