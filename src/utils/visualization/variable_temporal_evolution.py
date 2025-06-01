import xarray as xr
import pandas as pd
import matplotlib.pyplot as plt
import numpy as np
from pathlib import Path
import argparse

def plot_temporal_evolution(input_file, variable_name, 
                           time_dim='time', groupby_dim=None,
                           output_file=None, figsize=(10, 6),
                           title=None, ylabel=None, xlabel='Fecha',
                           show_trend=True, grid=True, show_plot=True):
    """
    Analiza y visualiza la evolución temporal de una variable en un dataset NetCDF.
    
    Args:
        input_file (str): Ruta del archivo NetCDF de entrada
        variable_name (str): Nombre de la variable a analizar
        time_dim (str): Nombre de la dimensión temporal (default: 'time')
        groupby_dim (str): Dimensión adicional para agrupamiento (opcional)
        output_file (str): Ruta para guardar el gráfico (opcional)
        figsize (tuple): Tamaño de la figura (ancho, alto)
        title (str): Título del gráfico (opcional)
        ylabel (str): Etiqueta del eje Y (opcional)
        xlabel (str): Etiqueta del eje X (default: 'Fecha')
        show_trend (bool): Mostrar línea de tendencia (default: True)
        grid (bool): Mostrar grid (default: True)
        show_plot (bool): Mostrar gráfico interactivo (default: True)
    """
    # Cargar dataset
    try:
        ds = xr.open_dataset(input_file)
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return
    
    # Convertir a DataFrame
    df = ds.to_dataframe().reset_index()
    
    # Verificar que existe la variable
    if variable_name not in df.columns:
        print(f"Error: La variable '{variable_name}' no existe en el dataset")
        return
    
    # Convertir tiempo a datetime
    df[time_dim] = pd.to_datetime(df[time_dim])
    
    # Agrupar datos
    if groupby_dim:
        if groupby_dim not in df.columns:
            print(f"Error: La dimensión de agrupamiento '{groupby_dim}' no existe")
            return
        series = df.groupby([time_dim, groupby_dim])[variable_name].mean().unstack()
    else:
        series = df.groupby(time_dim)[variable_name].mean()
    
    # Crear figura
    fig, ax = plt.subplots(figsize=figsize)
    
    # Configurar título por defecto si no se especifica
    if title is None:
        title = f"Evolución temporal de {variable_name}"
        if groupby_dim:
            title += f" (agrupado por {groupby_dim})"
        else:
            title += " (media global)"
    
    # Configurar etiqueta Y por defecto
    if ylabel is None:
        ylabel = variable_name
    
    # Plot de la serie temporal
    if groupby_dim:
        for column in series.columns:
            ax.plot(series.index, series[column], label=str(column))
    else:
        ax.plot(series.index, series.values, label=f"{variable_name} (media)")
    
    # Añadir tendencia lineal si se solicita
    if show_trend and not groupby_dim:
        x = np.arange(len(series))
        y = series.values
        coef = np.polyfit(x, y, 1)
        trend = np.poly1d(coef)
        ax.plot(series.index, trend(x), color="red", linestyle="--", label="Tendencia lineal")
    
    # Configurar el gráfico
    ax.set_title(title)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(grid)
    
    # Mostrar leyenda si hay múltiples series o tendencia
    if groupby_dim or show_trend:
        ax.legend()
    
    plt.tight_layout()
    
    # Guardar gráfico si se especifica
    if output_file:
        plt.savefig(output_file, dpi=300, bbox_inches='tight')
        print(f"Gráfico guardado en: {output_file}")
    
    # Mostrar gráfico
    if show_plot:
        plt.show()
    
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Análisis de evolución temporal')
    parser.add_argument('input', help='Archivo NetCDF de entrada')
    parser.add_argument('variable', help='Variable a analizar')
    parser.add_argument('--output', help='Ruta para guardar el gráfico')
    parser.add_argument('--time_dim', default='time', 
                       help='Nombre de la dimensión temporal')
    parser.add_argument('--groupby', dest='groupby_dim',
                       help='Dimensión adicional para agrupamiento')
    parser.add_argument('--figsize', nargs=2, type=float, default=[10, 6],
                       help='Tamaño de la figura (ancho alto)')
    parser.add_argument('--title', help='Título del gráfico')
    parser.add_argument('--ylabel', help='Etiqueta del eje Y')
    parser.add_argument('--xlabel', default='Fecha', help='Etiqueta del eje X')
    parser.add_argument('--no_trend', action='store_false', dest='show_trend',
                       help='Ocultar línea de tendencia')
    parser.add_argument('--no_grid', action='store_false', dest='grid',
                       help='Ocultar grid')
    parser.add_argument('--no_show', action='store_false', dest='show_plot',
                       help='No mostrar gráfico interactivo')
    
    args = parser.parse_args()
    
    plot_temporal_evolution(
        input_file=args.input,
        variable_name=args.variable,
        time_dim=args.time_dim,
        groupby_dim=args.groupby_dim,
        output_file=args.output,
        figsize=args.figsize,
        title=args.title,
        ylabel=args.ylabel,
        xlabel=args.xlabel,
        show_trend=args.show_trend,
        grid=args.grid,
        show_plot=args.show_plot
    )

if __name__ == '__main__':
    main()