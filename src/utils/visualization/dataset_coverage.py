import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns
from pathlib import Path
import argparse

def analyze_dataset_coverage(input_file, output_dir=None, 
                            delimiter='\t', exclude_cols=['ts', 'tile'],
                            plot_style='seaborn', figsize=(12, 6),
                            save_plots=False, show_plots=True):
    """
    Analiza la cobertura de datos en un archivo tabular (CSV/TSV).
    
    Args:
        input_file (str): Ruta del archivo de datos
        output_dir (str): Directorio para guardar resultados (None para no guardar)
        delimiter (str): Delimitador de columnas ('\t' para TSV, ',' para CSV)
        exclude_cols (list): Columnas a excluir del análisis
        plot_style (str): Estilo de matplotlib ('seaborn', 'ggplot', etc.)
        figsize (tuple): Tamaño de las figuras
        save_plots (bool): Guardar gráficos en archivos
        show_plots (bool): Mostrar gráficos interactivos
    """
    # Cargar datos
    try:
        df = pd.read_csv(input_file, delimiter=delimiter)
    except Exception as e:
        print(f"Error al cargar el archivo: {e}")
        return
    
    # Configurar estilo de gráficos
    plt.style.use(plot_style)
    
    # --- Análisis de completitud ---
    # Por columna (variable)
    col_coverage = df.notnull().mean() * 100
    
    # Por fila (registro)
    row_coverage = df.notnull().mean(axis=1) * 100
    
    # Filtrar columnas excluidas
    cols_to_show = [col for col in col_coverage.index if col not in exclude_cols]
    filtered_col_coverage = col_coverage[cols_to_show]
    
    # --- Resultados numéricos ---
    print("\n=== Cobertura por Columna ===\n")
    print(col_coverage.sort_values(ascending=False).to_string())
    
    print("\n=== Estadísticos de Cobertura por Fila ===\n")
    print(row_coverage.describe().to_string())
    
    # --- Visualización ---
    fig, (ax1, ax2) = plt.subplots(1, 2, figsize=figsize)
    
    # 1. Gráfico de barras para cobertura por columna
    filtered_col_coverage.sort_values().plot.barh(ax=ax1, color='skyblue')
    ax1.set_title("Cobertura por Variable (%)")
    ax1.set_xlabel("Porcentaje de completitud")
    ax1.grid(True, linestyle='--', alpha=0.7)
    
    # 2. Histograma para cobertura por fila
    # sns.histplot(row_coverage, bins=20, kde=True, color='salmon', ax=ax2)
    # .set_title("Distribución de Cobertura por Fila")
    # ax2.set_xlabel("Porcentaje de completitud")
    # ax2.set_ylabel("Número de filas")
    sns.kdeplot(row_coverage, color='salmon', fill=True, ax=ax2)
    ax2.set_title(f"Distribución de Densidad de Completitud\n(Total filas: {len(df):,})")
    ax2.set_xlabel("Porcentaje de completitud")
    ax2.set_ylabel("Densidad")
    ax2.grid(axis='y', linestyle='--', alpha=0.7)

    
    plt.tight_layout()
    
    # Guardar gráficos si se especifica
    if save_plots and output_dir:
        output_dir = Path(output_dir)
        output_dir.mkdir(exist_ok=True)
        
        # Guardar figura completa
        plt.savefig(output_dir / 'coverage_analysis.png', dpi=300, bbox_inches='tight')
        
        # Guardar datos como CSV
        coverage_data = pd.DataFrame({
            'column_coverage': col_coverage,
            'row_coverage': row_coverage
        })
        coverage_data.to_csv(output_dir / 'coverage_stats.csv', index=True)
        
        print(f"\nResultados guardados en: {output_dir}")
    
    # Mostrar gráficos
    if show_plots:
        plt.show()
    
    plt.close()

def main():
    parser = argparse.ArgumentParser(description='Análisis de cobertura de datos')
    parser.add_argument('input', help='Archivo de datos de entrada (CSV/TSV)')
    parser.add_argument('--output_dir', help='Directorio para guardar resultados')
    parser.add_argument('--delimiter', default='\t', 
                       help='Delimitador de columnas (default: \\t para TSV)')
    parser.add_argument('--exclude_cols', nargs='+', default=['ts', 'tile'],
                       help='Columnas a excluir del análisis')
    parser.add_argument('--plot_style', default='seaborn',
                       help='Estilo de matplotlib para gráficos')
    parser.add_argument('--no_plots', action='store_false', dest='show_plots',
                       help='No mostrar gráficos interactivos')
    parser.add_argument('--save', action='store_true', dest='save_plots',
                       help='Guardar gráficos y resultados')
    
    args = parser.parse_args()
    
    analyze_dataset_coverage(
        input_file=args.input,
        output_dir=args.output_dir,
        delimiter=args.delimiter,
        exclude_cols=args.exclude_cols,
        plot_style=args.plot_style,
        show_plots=args.show_plots,
        save_plots=args.save_plots
    )

if __name__ == '__main__':
    main()