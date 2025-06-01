from data_pipeline import ingest
from utils import netcdf_utils
from utils.downloaders import NASADataDownloader
from utils.downloaders import CopernicusMarineDownloader

def main():
    print("Iniciando el pipeline de datos...")
    # ds = ingest.load_netcdf(r"C:\Users\imano\Desktop\prueba\prueba.nc")
    
    # Configuración
    downloader = CopernicusMarineDownloader.CopernicusMarineDownloader(
        download_dir = r"C:\Users\imano\Desktop\4o CARRERA\TFG\project\data\CHLAndPhyto"
    )

if __name__ == "__main__":
    main()