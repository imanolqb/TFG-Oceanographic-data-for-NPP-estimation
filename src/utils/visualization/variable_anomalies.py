import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
from matplotlib.colors import Normalize
import argparse
from pathlib import Path

# Configuración por defecto para variables comunes
DEFAULT_CONFIG = {
    'CHL': {
        'title': 'Chlorophyll Anomaly',
        'label': r'Chlorophyll (CHL [mg/m$\mathregular{^3}$])',
        'cmap': 'RdBu_r',
        'log': False,
        'vmin': -0.4,
        'vmax': 0.4,
        'vcenter': 0
    },
    'sea_surface_temperature': {
        'title': 'SST Anomaly',
        'label': r'Sea Surface Temperature (SST [°C])',
        'cmap': 'coolwarm',
        'log': False,
        'vmin': -1.3,
        'vmax': 1.3,
        'vcenter': 0
    },
    'npp': {
        'title': 'NPP Anomaly',
        'label': r'Net Primary Production (NPP [mg C/m$\mathregular{^2}$ day$\mathregular{^{-1}}$])',
        'cmap': 'RdBu_r',
        'log': False,
        'vmin': -600,
        'vmax': 600,
        'vcenter': 0
    }
}

def calculate_period_average(ds, variable, start_year, end_year):
    """Calcula la media para un período de años específico.
    
    Args:
        ds (xarray.Dataset): Dataset cargado
        variable (str): Nombre de la variable a analizar
        start_year (int): Año inicial del período
        end_year (int): Año final del período
        
    Returns:
        xarray.DataArray: Media temporal de la variable para el período
    """
    period_data = ds[variable].sel(time=slice(f'{start_year}-01-01', f'{end_year}-12-31'))
    return period_data.mean(dim='time', skipna=True)

def plot_variable_anomaly(ds, variable, config, early_period, late_period, output_file=None):
    """Calcula y representa la anomalía entre dos períodos temporales.
    
    Args:
        ds (xarray.Dataset): Dataset cargado
        variable (str): Nombre de la variable a analizar
        config (dict): Configuración de visualización para la variable
        early_period (tuple): Tupla con (año_inicio, año_fin) para el período base
        late_period (tuple): Tupla con (año_inicio, año_fin) para el período de comparación
        output_file (str): Ruta para guardar el gráfico (opcional)
    """
    # Calcular medias de los períodos
    early_start, early_end = early_period
    late_start, late_end = late_period
    
    early_avg = calculate_period_average(ds, variable, early_start, early_end)
    late_avg = calculate_period_average(ds, variable, late_start, late_end)
    
    # Calcular anomalía
    anomaly = late_avg - early_avg
    
    # Crear figura
    fig, ax = plt.subplots(figsize=(12, 8), 
                         subplot_kw={'projection': ccrs.PlateCarree()})
    
    # Configurar extensión del mapa
    lons = ds['longitude']
    lats = ds['latitude']
    ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], 
                 crs=ccrs.PlateCarree())
    
    # Configurar normalización
    norm = Normalize(vmin=config['vmin'], vmax=config['vmax'])
    
    # Mapa de calor
    mesh = ax.pcolormesh(lons, lats, anomaly, 
                        cmap=config['cmap'], 
                        transform=ccrs.PlateCarree(), 
                        norm=norm)
    
    # Añadir detalles del mapa
    ax.set_title(f"{config['title']}\n({late_start}-{late_end} avg minus {early_start}-{early_end} avg)")
    ax.coastlines()
    
    # Barra de color
    cbar = plt.colorbar(mesh, ax=ax, shrink=0.8, pad=0.05)
    cbar.set_label(config['label'], size=10, fontweight='bold')
    
    # Líneas de grid
    gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                     linewidth=0.5, color='gray', alpha=0.5, linestyle='--')
    gl.top_labels = False
    gl.right_labels = False
    
    plt.tight_layout()
    
    # Guardar gráfico si se especifica
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Gráfico guardado en: {output_file}")
    
    plt.show()
    plt.close()

def analyze_variable_anomalies(input_file, variables, config=None, 
                             early_period=(2003, 2007), late_period=(2019, 2023),
                             output_dir=None):
    """Analiza anomalías para múltiples variables en un dataset.
    
    Args:
        input_file (str): Ruta del archivo NetCDF
        variables (list): Lista de variables a analizar
        config (dict): Configuración personalizada para variables
        early_period (tuple): Período base para comparación
        late_period (tuple): Período reciente para comparación
        output_dir (str): Directorio para guardar gráficos (opcional)
    """
    # Cargar dataset
    try:
        ds = xr.open_dataset(input_file)
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return
    
    # Combinar configuración por defecto con personalizada
    if config is None:
        config = DEFAULT_CONFIG
    
    # Verificar variables disponibles
    available_vars = [var for var in variables if var in ds]
    missing_vars = set(variables) - set(available_vars)
    
    if missing_vars:
        print(f"Advertencia: Variables no encontradas: {missing_vars}")
    
    if not available_vars:
        raise ValueError("Ninguna de las variables solicitadas está presente en el dataset")
    
    # Procesar cada variable
    for variable in available_vars:
        print(f"\nProcesando variable: {variable}")
        
        # Obtener configuración para esta variable
        var_config = config.get(variable, {
            'title': f'{variable} Anomaly',
            'label': variable,
            'cmap': 'RdBu_r',
            'log': False,
            'vmin': None,
            'vmax': None,
            'vcenter': 0
        })
        
        # Determinar ruta de salida si se especifica
        output_file = None
        if output_dir:
            output_dir = Path(output_dir)
            output_dir.mkdir(exist_ok=True)
            output_file = output_dir / f"{variable}_anomaly.png"
        
        # Generar gráfico de anomalía
        plot_variable_anomaly(
            ds=ds,
            variable=variable,
            config=var_config,
            early_period=early_period,
            late_period=late_period,
            output_file=output_file
        )

def main():
    parser = argparse.ArgumentParser(description='Análisis de anomalías de variables oceanográficas')
    parser.add_argument('input', help='Archivo NetCDF de entrada')
    parser.add_argument('variables', nargs='+', help='Variables a analizar')
    parser.add_argument('--output_dir', help='Directorio para guardar gráficos')
    parser.add_argument('--early_start', type=int, default=2003,
                       help='Año inicial del período base')
    parser.add_argument('--early_end', type=int, default=2007,
                       help='Año final del período base')
    parser.add_argument('--late_start', type=int, default=2019,
                       help='Año inicial del período reciente')
    parser.add_argument('--late_end', type=int, default=2023,
                       help='Año final del período reciente')
    
    args = parser.parse_args()
    
    analyze_variable_anomalies(
        input_file=args.input,
        variables=args.variables,
        early_period=(args.early_start, args.early_end),
        late_period=(args.late_start, args.late_end),
        output_dir=args.output_dir
    )

if __name__ == '__main__':
    main()