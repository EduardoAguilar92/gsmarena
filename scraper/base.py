import requests
import logging
import re
import time
from bs4 import BeautifulSoup
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.service import Service
from selenium.webdriver.chrome.options import Options
from typing import Optional, Dict, List
from .logger import get_logger

class GSMArenaScraper:
    """
    Clase para realizar web scraping de la página de GSMArena.

    Atributos:
        base_url (str): URL de la página base.
        
    """

    def __init__(self, base_url: str, pause_every = 20):
        """Constructor de la clase GSMArenaScraper."""
        self.base_url = base_url
        self.pause_every = pause_every
        self.brands: List[Dict] = []  # Lista para almacenar diccionarios de marcas.
        self.devices: List[Dict] = [] # Lista para almacenar diccionarios de dispositivos.
        self.session = requests.Session() # Usa una sesión para persistir cookies y cabeceras.
        self.logger = get_logger(self.__class__.__name__) # Inicializa el logger para la clase.
        self.logger.setLevel(logging.INFO)

    def say_hello(self):
        """Imprime un mensaje de saludo para confirmar que el scraper se ha inicializado."""
        self.logger.info("👋 Hola desde GSMArenaScraper")

    def initial_scraper(self):
        """
        Realiza el primer paso del scraping: obtener la lista de todas las marcas de teléfonos.
        Utiliza `requests` y `BeautifulSoup` para un scraping estático.
        """
        self.logger.info(f"Iniciando scraping de {self.base_url}")
        try:
            # Realiza una petición GET a la URL base para obtener el HTML de la página de marcas.
            response = self.session.get(self.base_url)
            response.raise_for_status()  # Lanza una excepción para respuestas con error (4xx o 5xx).
        except requests.exceptions.RequestException as e:
            self.logger.error(f'Error al realizar la petición a {self.base_url}: {e}')
            return # Detiene la ejecución si la petición inicial falla.

        try:
            # Parsea el contenido HTML de la respuesta.
            soup = BeautifulSoup(response.text, 'html.parser')
            # Encuentra el contenedor principal que aloja la lista de marcas.
            makers_container = soup.find('div', class_='st-text')
            # Encuentra todos los enlaces 'a' dentro del contenedor, cada uno representa una marca.
            brand_links = makers_container.find_all('a')

            # Itera sobre cada enlace para extraer la información de la marca.
            for link in brand_links:
                brand_name = link.contents[0].strip()
                brand_url = 'https://www.gsmarena.com/' + link.get('href')
                # Extrae el texto del número de dispositivos y lo limpia.
                devices_text = link.find('span').get_text(strip=True)
                # Usa una expresión regular para obtener solo el número del texto.
                devices_number = int(re.search(r'\d+', devices_text).group())
                # Añade la información de la marca a la lista 'brands'.
                self.brands.append({
                    'name': brand_name,
                    'url': brand_url,
                    'devices': devices_number
                })
        except (AttributeError, TypeError, ValueError) as e:
            self.logger.error(f'Error al analizar el HTML de la página de marcas: {e}')

        self.logger.info(f"Scraping inicial terminado. Se encontraron {len(self.brands)} marcas.")

    def brand_scraper(self):
        """
        Para cada marca, navega a su página y extrae la lista de todos sus dispositivos.
        Utiliza `Selenium` para manejar contenido que podría cargarse dinámicamente.
        """
        self.logger.info(f"Iniciando scraping de las {len(self.brands)} marcas")
        driver = None
        try:
            # Inicializa el driver de Selenium para Chrome.
            driver = webdriver.Chrome()
            time.sleep(3) # Pausa para asegurar que el navegador se inicie correctamente.
            
            # Itera sobre la lista de marcas obtenidas previamente.
            # NOTA: El bucle se interrumpe después de 3 marcas para fines de demostración.
            for i in range(len(self.brands)):
                if i == 3:
                    break
                brand_name = self.brands[i]['name']
                self.logger.info(f"Visitando la marca {brand_name}")
                # Navega a la URL de la página de la marca.
                driver.get(self.brands[i]["url"])
                # Pausa larga para permitir que el contenido dinámico (JavaScript) cargue completamente.
                time.sleep(10)
                # Obtiene el código fuente de la página después de la ejecución de JS.
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")

                # Encuentra el div que contiene la lista de dispositivos.
                makers_div = soup.find("div", class_="makers")
                if not makers_div:
                    self.logger.warning(f"No se encontró la sección de teléfonos para {brand_name}")
                    continue

                # Itera sobre cada enlace 'a' que representa un dispositivo.
                for a_tag in makers_div.find_all("a"):
                    href = a_tag.get("href")
                    strong_tag = a_tag.find("strong")
                    if href and strong_tag:
                        phone_name = strong_tag.text.strip()
                        device_url = "https://www.gsmarena.com/" + href
                        # self.logger.info(f"{phone_name} -> {device_url}")

                    # Añade la información del dispositivo a la lista 'devices'.
                    self.devices.append({
                    'brand': brand_name,
                    'name': phone_name,
                    'device_url': device_url,
                    'specs': []
                    })

        except Exception as e:
            # Captura cualquier error durante el scraping de una marca específica.
            current_brand_name = self.brands[i]['name'] if 'i' in locals() and i < len(self.brands) else "desconocida"
            self.logger.error(f"Error realizando la extracción de links de la marca {current_brand_name}: {e}")

        finally:
            # Asegura que el driver de Selenium se cierre correctamente, incluso si ocurren errores.
            if driver:
                driver.quit()

    def device_scraper(self):
        """
        Para cada dispositivo, navega a su página y extrae la tabla de especificaciones.
        Utiliza `Selenium` para asegurar que toda la página se cargue correctamente.
        """
        self.logger.info("Iniciando scraping de los equipos")

        driver = None
        try:
            # Inicializa el driver de Selenium para Chrome.
            driver = webdriver.Chrome()
            time.sleep(3) # Pausa para asegurar que el navegador se inicie correctamente.
            
            # Itera sobre la lista de dispositivos obtenidos.
            # NOTA: El bucle se interrumpe después de 3 dispositivos para fines de demostración.
            for i in range(len(self.devices)):
                if i == 3:
                    break
                device_name = self.devices[i]['name']
                self.logger.info(f"Visitando el equipo {device_name}")
                # Navega a la URL de la página del dispositivo.
                driver.get(self.devices[i]["device_url"])
                # Pausa para permitir que la página cargue completamente.
                time.sleep(10)
                # Obtiene el código fuente de la página.
                html = driver.page_source
                soup = BeautifulSoup(html, "html.parser")
                
                specs = {}
                # Encuentra la tabla de especificaciones por su ID.
                specs_table = soup.find("div", id="specs-list")
                if specs_table:
                    # Itera sobre cada fila 'tr' de la tabla de especificaciones.
                    rows = specs_table.find_all("tr")
                    for row in rows:
                        cols = row.find_all("td")
                        # Asegura que la fila contenga un par de celdas (nombre y valor de la especificación).
                        if len(cols) == 2:
                            spec_name = cols[0].text.strip()
                            spec_value = cols[1].text.strip()
                            specs[spec_name] = spec_value

                # Actualiza el diccionario del dispositivo con sus especificaciones.
                self.devices[i]['specs'] = specs


        except Exception as e:
            # Captura cualquier error durante el scraping de un dispositivo específico.
            current_device_name = self.devices[i]['name'] if 'i' in locals() and i < len(self.devices) else "desconocido"
            self.logger.error(f"Error realizando la extracción de especificaciones del equipo {current_device_name}: {e}")

        finally:
            # Asegura que el driver de Selenium se cierre correctamente.
            if driver:
                driver.quit()