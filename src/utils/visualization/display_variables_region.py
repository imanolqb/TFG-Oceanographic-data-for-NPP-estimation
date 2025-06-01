import xarray as xr
import matplotlib.pyplot as plt
import numpy as np
import cartopy.crs as ccrs
from matplotlib.colors import LogNorm, Normalize
from ipywidgets import interact, Dropdown, FloatSlider, IntSlider
import cmocean as cmo

# Configuración de variables con rangos y propiedades específicas
VARIABLE_CONFIG = {
    'CHL': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Chlorophyll',
        'label': r'Chlorophyll (CHL [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'DIATO': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Diatoms',
        'label': r'Diatoms (DIATO [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'DINO': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Dinoflagellates',
        'label': r'Dinoflagellates (DINO [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'GREEN': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Green Algae',
        'label': r'Green Algae (GREEN [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'HAPTO': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Haptophytes',
        'label': r'Haptophytes (HAPTO [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'MICRO': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Microphytoplankton',
        'label': r'Microphytoplankton (MICRO [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'NANO': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Nanophytoplankton',
        'label': r'Nanophytoplankton (NANO [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'PICO': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Picophytoplankton',
        'label': r'Picophytoplankton (PICO [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'PROCHLO': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Prochlorococcus',
        'label': r'Prochlorococcus (PROCHLO [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'PROKAR': {
        'vmin': 0.01,
        'vmax': 10,
        'log': True,
        'title': 'Prokaryotes',
        'label': r'Prokaryotes (PROKAR [mg/m$\mathregular{^3}$])',
        'default_cmap': 'cmo.algae'
    },
    'fco2_ave_weighted': {
        'vmin': 300,
        'vmax': 500,
        'log': False,
        'title': 'Fugacity of CO2',
        'label': r'Fugacity of CO$\mathregular{^2}$ (fco2 [µatm])',
        'default_cmap': 'cmo.thermal'
    },
    'par': {
        'vmin': 500,
        'vmax': 20000,
        'log': True,
        'title': 'PAR',
        'label': r'Photosynthetically active radiation (PAR [µmol photons/m$\mathregular{^2}$ s$\mathregular{^{-1}}$])',
        'default_cmap': 'cmo.solar'
    },
    'npp': {
        'vmin': 350,
        'vmax': 2600,
        'log': True,
        'title': 'Net Primary Production',
        'label': r'Net primary production (NPP [mg C/m$\mathregular{^2}$ día$\mathregular{^{-1}}$])',
        'default_cmap': 'cmo.algae'
    },
    'uo': {
        'vmin': -0.5,
        'vmax': 0.5,
        'log': False,
        'title': 'East-west Current',
        'label': r'East-west speed (UO [m/s])',
        'default_cmap': 'cmo.balance'
    },
    'vo': {
        'vmin': -0.5,
        'vmax': 0.5,
        'log': False,
        'title': 'North-south Current',
        'label': r'North-south speed (VO [m/s])',
        'default_cmap': 'cmo.balance'
    },
    'sea_surface_temperature': {
        'vmin': 18,
        'vmax': 28,
        'log': False,
        'title': 'Sea Surface Temperature',
        'label': r'Sea Surface Temperature (SST [°C])',
        'default_cmap': 'cmo.thermal'
    }
}

# Colormaps disponibles
AVAILABLE_CMAPS = [
    'viridis', 'plasma', 'inferno', 'magma', 'cividis',
    'cmo.algae', 'cmo.thermal', 'cmo.haline', 'cmo.solar',
    'cmo.balance', 'cmo.dense', 'cmo.curl', 'cmo.diff'
]

class VariableVisualizer:
    def __init__(self, file_path, variable=None):
        self.file_path = file_path
        self.ds = xr.open_dataset(file_path)
        self.available_dates = [str(date.values)[:10] for date in self.ds['time']]
        # self.current_variable = variables[0] if variables else 'CHL'
        self.current_variable = variable
        
    def update_sliders(self, variable):
        """Actualiza los sliders según la variable seleccionada"""
        config = VARIABLE_CONFIG.get(variable, VARIABLE_CONFIG[self.current_variable])
        self.vmin_slider.min = config['vmin'] * 0.1
        self.vmin_slider.max = config['vmin'] * 10
        self.vmin_slider.value = config['vmin']
        self.vmin_slider.step = (config['vmax'] - config['vmin']) / 100
        
        self.vmax_slider.min = config['vmax'] * 0.1
        self.vmax_slider.max = config['vmax'] * 10
        self.vmax_slider.value = config['vmax']
        self.vmax_slider.step = (config['vmax'] - config['vmin']) / 100
        
        self.current_variable = variable
        
    def plot_variable(self, variable, target_date, vmin, vmax, colormap, n_divisions):
        """Visualiza la variable seleccionada"""
        # Actualizar configuración si cambió la variable
        if variable != self.current_variable:
            self.update_sliders(variable)
            vmin = VARIABLE_CONFIG[variable]['vmin']
            vmax = VARIABLE_CONFIG[variable]['vmax']
        
        config = VARIABLE_CONFIG.get(variable, VARIABLE_CONFIG[variable])
        
        try:
            # Seleccionar datos
            var_data = self.ds[variable].sel(time=target_date, method='nearest')
            lons = self.ds['longitude']
            lats = self.ds['latitude']
            
            # Crear figura
            fig, ax = plt.subplots(figsize=(10, 8), 
                                 subplot_kw={'projection': ccrs.PlateCarree()})
            ax.set_extent([lons.min(), lons.max(), lats.min(), lats.max()], 
                         crs=ccrs.PlateCarree())
            
            # Seleccionar normalización
            norm = LogNorm(vmin, vmax) if config['log'] else Normalize(vmin, vmax)
            
            # Crear mapa de calor
            cmap = plt.get_cmap(colormap)
            mesh = ax.pcolormesh(lons, lats, var_data, 
                                cmap=cmap, 
                                transform=ccrs.PlateCarree(),
                                norm=norm)
            
            # Configurar título y detalles
            ax.set_title(f'{config["title"]} - {target_date}')
            ax.coastlines()
            
            # Crear colorbar
            cbar = plt.colorbar(mesh, ax=ax, shrink=0.9, pad=0.075)
            cbar.set_label(config['label'], size=8, fontweight='bold')
            cbar.ax.tick_params(labelsize=6)
            
            # Configurar gridlines
            gl = ax.gridlines(crs=ccrs.PlateCarree(), draw_labels=True,
                             linewidth=0.5, color='gray', alpha=0.35, linestyle='--')
            gl.top_labels = False
            gl.right_labels = False
            
            plt.tight_layout()
            plt.show()
            
        except Exception as e:
            print(f"Error al generar el gráfico: {e}")
    
    def create_widgets(self):
        """Crea los widgets interactivos"""
        # Dropdown para selección de variable
        self.variable_dropdown = Dropdown(
            options=list(VARIABLE_CONFIG.keys()),
            value=self.current_variable,
            description='Variable:'
        )
        
        # Dropdown para fechas
        self.date_dropdown = Dropdown(
            options=self.available_dates,
            value=self.available_dates[0],
            description='Fecha:'
        )
        
        # Sliders para vmin y vmax (valores iniciales para CHL)
        self.vmin_slider = FloatSlider(
            value=VARIABLE_CONFIG[self.current_variable]['vmin'],
            min=VARIABLE_CONFIG[self.current_variable]['vmin'] * 0.1,
            max=VARIABLE_CONFIG[self.current_variable]['vmin'] * 10,
            step=0.01,
            description='vmin:'
        )
        
        self.vmax_slider = FloatSlider(
            value=VARIABLE_CONFIG[self.current_variable]['vmax'],
            min=VARIABLE_CONFIG[self.current_variable]['vmax'] * 0.1,
            max=VARIABLE_CONFIG[self.current_variable]['vmax'] * 10,
            step=0.1,
            description='vmax:'
        )
        
        # Dropdown para colormap
        self.cmap_dropdown = Dropdown(
            options=AVAILABLE_CMAPS,
            value=VARIABLE_CONFIG[self.current_variable]['default_cmap'],
            description='Colormap:'
        )
        
        # Slider para divisiones del colorbar
        self.divisions_slider = IntSlider(
            value=5,
            min=2,
            max=20,
            step=1,
            description='Divisiones:'
        )
        
        # Conectar widgets
        self.variable_dropdown.observe(
            lambda change: self.update_sliders(change.new), names='value')
        
        # Crear interfaz interactiva
        interact(
            self.plot_variable,
            variable=self.variable_dropdown,
            target_date=self.date_dropdown,
            vmin=self.vmin_slider,
            vmax=self.vmax_slider,
            colormap=self.cmap_dropdown,
            n_divisions=self.divisions_slider
        )

# Ejemplo de uso
if __name__ == '__main__':
    file_path = r"C:\Users\imano\Desktop\4o CARRERA\TFG\cuadernos\refactor\miercoles\npp_rbf_interpolated.nc"  # Cambiar por la ruta correcta
    visualizer = VariableVisualizer(file_path, variable='npp')
    visualizer.create_widgets()