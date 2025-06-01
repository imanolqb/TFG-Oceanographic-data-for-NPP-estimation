import os
import copernicusmarine

class CopernicusMarineDownloader:
    def __init__(self, download_dir: str):
        """
        Inicializa el descargador de datos de Copernicus Marine
        
        Args:
            download_dir (str): Directorio para guardar archivos descargados
        """
        self.download_dir = download_dir
        
        # Crear directorio de descarga si no existe
        os.makedirs(self.download_dir, exist_ok=True)

    def login(self, username: str, password: str):
        """
        Inicia sesión en el portal de Copernicus Marine
        
        Args:
            username (str): Nombre de usuario para el portal
            password (str): Contraseña para el portal
        """
        try:
            copernicusmarine.login(username, password)
        except Exception as e:
            print(f"Error al iniciar sesión: {str(e)}")
    
    def download_data(self, product: str, variables: list, start_date: str, end_date: str, 
                      min_lat: float = None, max_lat: float = None, min_lon: float = None, max_lon: float = None):
        """
        Descarga datos de Copernicus Marine
        
        Args:
            product (str): Nombre del producto a descargar
            variables (str): Variable específica del producto
            start_date (str): Fecha de inicio en formato 'YYYY-MM-DD'
            end_date (str): Fecha de fin en formato 'YYYY-MM-DD'
            min_lat (float, optional): Latitud mínima para filtrar datos
            max_lat (float, optional): Latitud máxima para filtrar datos
            min_lon (float, optional): Longitud mínima para filtrar datos
            max_lon (float, optional): Longitud máxima para filtrar datos
        """
        try:
            # Descargar los datos
            copernicusmarine.subset(
                dataset_id=product,
                variables=variables,
                minimum_latitude=min_lat,
                maximum_latitude=max_lat,
                minimum_longitude=min_lon,
                maximum_longitude=max_lon,
                start_datetime=start_date,
                end_datetime=end_date,
                output_directory=self.download_dir
            )
            
        except Exception as e:
            print(f"Error al descargar datos: {str(e)}")

def main():
    import argparse

    parser = argparse.ArgumentParser(description="Descargador de datos de Copernicus Marine")
    parser.add_argument('username', help='Nombre de usuario para el portal de Copernicus Marine')
    parser.add_argument('password', help='Contraseña para el portal de Copernicus Marine')
    parser.add_argument('download_dir', help='Directorio para guardar archivos descargados')
    parser.add_argument('product', help='Nombre del producto a descargar')
    parser.add_argument('variables', nargs='+', help='Variables específicas del producto')
    parser.add_argument('start_date', help='Fecha de inicio en formato YYYY-MM-DD')
    parser.add_argument('end_date', help='Fecha de fin en formato YYYY-MM-DD')
    parser.add_argument('--min_lat', type=float, help='Latitud mínima para filtrar datos')
    parser.add_argument('--max_lat', type=float, help='Latitud máxima para filtrar datos')
    parser.add_argument('--min_lon', type=float, help='Longitud mínima para filtrar datos')
    parser.add_argument('--max_lon', type=float, help='Longitud máxima para filtrar datos')
    args = parser.parse_args()
    # Crear instancia del descargador
    downloader = CopernicusMarineDownloader(download_dir=args.download_dir)
    # Iniciar sesión en el portal
    downloader.login(username=args.username, password=args.password)
    # Descargar los datos
    downloader.download_data(
        product=args.product,
        variables=args.variables,
        start_date=args.start_date,
        end_date=args.end_date,
        min_lat=args.min_lat,
        max_lat=args.max_lat,
        min_lon=args.min_lon,
        max_lon=args.max_lon
    )

if __name__ == '__main__':
    main()