import os
import time
from selenium import webdriver
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from webdriver_manager.chrome import ChromeDriverManager
from typing import List, Optional

class NASADataDownloader:
    def __init__(self, username: str, password: str, download_dir: str):
        """
        Inicializa el descargador de datos de NASA Earthdata
        
        Args:
            username (str): Nombre de usuario de Earthdata
            password (str): Contraseña de Earthdata
            download_dir (str): Directorio para guardar archivos descargados
        """
        self.username = username
        self.password = password
        self.download_dir = download_dir
        self.driver = None
        
        # Crear directorio de descarga si no existe
        os.makedirs(self.download_dir, exist_ok=True)
        
    def initialize_driver(self):
        """Configura e inicializa el controlador de Chrome"""
        chrome_options = webdriver.ChromeOptions()
        
        # Configuración de preferencias para descargas
        prefs = {
            "download.default_directory": self.download_dir,
            "download.prompt_for_download": False,
            "download.directory_upgrade": True,
            "safebrowsing.enabled": True
        }
        chrome_options.add_experimental_option("prefs", prefs)
        
        # Inicializar el driver
        self.driver = webdriver.Chrome(
            service=Service(ChromeDriverManager().install()),
            options=chrome_options
        )
        
    def login_to_earthdata(self):
        """Inicia sesión en el portal Earthdata de NASA"""
        if not self.driver:
            raise RuntimeError("Driver no inicializado. Llame a initialize_driver() primero.")
            
        self.driver.get("https://urs.earthdata.nasa.gov")
        
        # Esperar y completar el formulario de login
        WebDriverWait(self.driver, 15).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(self.username)
        
        self.driver.find_element(By.ID, "password").send_keys(self.password)
        self.driver.find_element(By.NAME, "commit").click()
        
        # Pequeña pausa para asegurar el login
        time.sleep(3)
        
    def download_files(self, urls: List[str], delay: int = 10):
        """
        Descarga archivos desde una lista de URLs
        
        Args:
            urls (List[str]): Lista de URLs para descargar
            delay (int): Tiempo de espera entre descargas (segundos)
        """
        if not self.driver:
            raise RuntimeError("Driver no inicializado. Llame a initialize_driver() primero.")
            
        for url in urls:
            try:
                filename = url.split("/")[-1]
                filepath = os.path.join(self.download_dir, filename)
                
                # Verificar si el archivo ya existe
                if os.path.exists(filepath):
                    print(f"✓ {filename} ya existe")
                    continue
                
                print(f"Descargando {filename}...")
                self.driver.get(url)
                
                # Esperar a que la descarga se complete
                time.sleep(delay)
                
                # Verificar la descarga
                if os.path.exists(filepath) and os.path.getsize(filepath) > 10240:
                    size_mb = os.path.getsize(filepath) / 1e6
                    print(f"✓ {filename} descargado ({size_mb:.2f} MB)")
                else:
                    print(f"✗ Error: {filename} es demasiado pequeño o no se descargó")
                    
            except Exception as e:
                print(f"Error con {url}: {str(e)}")
                
    def close(self):
        """Cierra el navegador y libera recursos"""
        if self.driver:
            self.driver.quit()
            self.driver = None
            
    @staticmethod
    def read_urls_from_file(filepath: str) -> List[str]:
        """
        Lee URLs desde un archivo de texto
        
        Args:
            filepath (str): Ruta al archivo con URLs
            
        Returns:
            List[str]: Lista de URLs limpias
        """
        with open(filepath, "r") as f:
            return [line.strip() for line in f.readlines() if line.strip()]

def main():
    import argparse
    
    parser = argparse.ArgumentParser(description='Descargador de datos de NASA Earthdata')
    parser.add_argument('username', help='Nombre de usuario Earthdata')
    parser.add_argument('password', help='Contraseña Earthdata')
    parser.add_argument('download_dir', help='Directorio para descargas')
    parser.add_argument('urls_file', help='Archivo con URLs a descargar')
    parser.add_argument('--delay', type=int, default=10,
                       help='Tiempo de espera entre descargas (segundos)')
    
    args = parser.parse_args()
    
    # Crear instancia del descargador
    downloader = NASADataDownloader(
        username=args.username,
        password=args.password,
        download_dir=args.download_dir
    )
    
    try:
        # Inicializar y configurar
        downloader.initialize_driver()
        downloader.login_to_earthdata()
        
        # Leer URLs y descargar
        urls = NASADataDownloader.read_urls_from_file(args.urls_file)
        downloader.download_files(urls, delay=args.delay)
        
    finally:
        # Asegurar que el driver se cierre
        downloader.close()

if __name__ == '__main__':
    main()