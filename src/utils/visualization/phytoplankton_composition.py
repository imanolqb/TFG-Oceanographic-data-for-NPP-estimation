import pandas as pd
import matplotlib.pyplot as plt
from pathlib import Path
import argparse

def analyze_phytoplankton_composition(input_file, output_file=None, 
                                    delimiter='\t', time_column='ts',
                                    group_columns=None, nice_names=None,
                                    figsize=(11, 8), colormap='Spectral',
                                    title=None, ylabel='Proporción',
                                    xlabel='Fecha', grid_alpha=0.3,
                                    show_plot=True):
    """
    Analiza y visualiza la composición relativa de grupos fitoplanctónicos.
    
    Args:
        input_file (str): Ruta del archivo de datos (CSV/TSV)
        output_file (str): Ruta para guardar el gráfico (opcional)
        delimiter (str): Delimitador de columnas ('\t' para TSV, ',' para CSV)
        time_column (str): Nombre de la columna de tiempo
        group_columns (list): Lista de columnas con grupos fitoplanctónicos
        nice_names (dict): Diccionario para nombres descriptivos de grupos
        figsize (tuple): Tamaño de la figura (ancho, alto)
        colormap (str): Mapa de colores para el gráfico
        title (str): Título del gráfico (opcional)
        ylabel (str): Etiqueta del eje Y
        xlabel (str): Etiqueta del eje X
        grid_alpha (float): Transparencia de la grid (0 a 1)
        show_plot (bool): Mostrar gráfico interactivo (default: True)
    """
    # Cargar datos
    try:
        df = pd.read_csv(input_file, delimiter=delimiter)
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return
    
    # Configurar nombres por defecto si no se proporcionan
    if group_columns is None:
        group_columns = [
            'bio.phyto.diato', 'bio.phyto.dino', 'bio.phyto.green',
            'bio.phyto.hapto', 'bio.phyto.micro', 'bio.phyto.nano',
            'bio.phyto.pico'
        ]
    
    if nice_names is None:
        nice_names = {
            'bio.phyto.diato': 'Diatomeas',
            'bio.phyto.dino': 'Dinoflagelados',
            'bio.phyto.green': 'Clorofitas',
            'bio.phyto.hapto': 'Haptófitas',
            'bio.phyto.micro': 'Microfitoplancton',
            'bio.phyto.nano': 'Nanofitoplancton',
            'bio.phyto.pico': 'Picofitoplancton'
        }
    
    # Verificar columnas existentes
    available_groups = [col for col in group_columns if col in df.columns]
    missing_groups = set(group_columns) - set(available_groups)
    
    if missing_groups:
        print(f"Advertencia: No se encontraron las columnas: {missing_groups}")
    
    if not available_groups:
        raise ValueError("No se encontraron columnas de grupos fitoplanctónicos en el archivo")
    
    # Procesar columna de tiempo si existe
    if time_column in df.columns:
        df[time_column] = pd.to_datetime(df[time_column])
    else:
        print(f"Advertencia: No se encontró la columna de tiempo '{time_column}'")
        time_column = None
    
    # Calcular composición relativa
    if time_column:
        comp_df = df.groupby(time_column)[available_groups].mean()
    else:
        comp_df = df[available_groups].mean().to_frame().T
    
    # Normalizar a proporciones
    comp_df = comp_df.div(comp_df.sum(axis=1), axis=0)
    
    # Configurar título por defecto si no se especifica
    if title is None:
        title = 'Composición relativa de grupos fitoplanctónicos'
        if time_column:
            title += ' (evolución temporal)'
    
    # Crear gráfico
    plt.figure(figsize=figsize)
    
    # Gráfico de áreas apiladas
    ax = comp_df.plot.area(
        stacked=True,
        colormap=colormap,
        legend=False
    )
    
    # Configurar leyenda con nombres descriptivos
    handles, labels = ax.get_legend_handles_labels()
    new_labels = [nice_names.get(l, l) for l in labels]
    ax.legend(
        handles, 
        new_labels, 
        title='Grupo', 
        bbox_to_anchor=(1.05, 1),
        loc='upper left'
    )
    
    # Configurar el gráfico
    ax.set_title(title, pad=20)
    ax.set_ylabel(ylabel)
    ax.set_xlabel(xlabel)
    ax.grid(alpha=grid_alpha)
    
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
    parser = argparse.ArgumentParser(description='Análisis de composición de fitoplancton')
    parser.add_argument('input', help='Archivo de datos de entrada (CSV/TSV)')
    parser.add_argument('--output', help='Ruta para guardar el gráfico')
    parser.add_argument('--delimiter', default='\t', 
                       help='Delimitador de columnas (default: \\t para TSV)')
    parser.add_argument('--time_column', default='ts',
                       help='Nombre de la columna de tiempo')
    parser.add_argument('--groups', nargs='+',
                       help='Columnas con grupos fitoplanctónicos')
    parser.add_argument('--figsize', nargs=2, type=float, default=[11, 8],
                       help='Tamaño de la figura (ancho alto)')
    parser.add_argument('--colormap', default='Spectral',
                       help='Mapa de colores para el gráfico')
    parser.add_argument('--title', help='Título del gráfico')
    parser.add_argument('--ylabel', default='Proporción',
                       help='Etiqueta del eje Y')
    parser.add_argument('--xlabel', default='Fecha',
                       help='Etiqueta del eje X')
    parser.add_argument('--grid_alpha', type=float, default=0.3,
                       help='Transparencia de la grid (0 a 1)')
    parser.add_argument('--no_show', action='store_false', dest='show_plot',
                       help='No mostrar gráfico interactivo')
    
    args = parser.parse_args()
    
    analyze_phytoplankton_composition(
        input_file=args.input,
        output_file=args.output,
        delimiter=args.delimiter,
        time_column=args.time_column,
        group_columns=args.groups,
        figsize=args.figsize,
        colormap=args.colormap,
        title=args.title,
        ylabel=args.ylabel,
        xlabel=args.xlabel,
        grid_alpha=args.grid_alpha,
        show_plot=args.show_plot
    )

if __name__ == '__main__':
    main()