# GSMArena Scraper

Este proyecto es una potente herramienta de web scraping desarrollada en Python, diseñada específicamente para extraer de forma sistemática y automatizada una gran cantidad de datos sobre teléfonos móviles desde el popular sitio web GSMArena.com.

Utilizando una combinación de librerías robustas como `requests` para peticiones HTTP, `BeautifulSoup4` para el parseo de HTML y `Selenium` para la interacción con contenido dinámico, este scraper es capaz de navegar por la estructura del sitio, recopilar información detallada y organizarla para su posterior análisis.

## Características

-   **Extracción de Marcas**: Obtiene una lista completa de todas las marcas de teléfonos disponibles en GSMArena.
-   **Extracción de Dispositivos**: Para cada marca, extrae la lista de todos los modelos de teléfonos.
-   **Extracción de Especificaciones**: Para cada dispositivo, recopila una tabla detallada de especificaciones.
-   **Manejo de Páginas Dinámicas**: Utiliza Selenium para interactuar con contenido cargado dinámicamente (JavaScript).
-   **Logging**: Integra un sistema de logging para registrar el progreso del scraping, advertencias y errores en un archivo `scraper.log` y en la consola.
-   **Resilencia**: Incluye pausas (`time.sleep`) para evitar sobrecargar el servidor y ser bloqueado.

## Requisitos

-   Python 3.7+
-   Google Chrome instalado.
-   ChromeDriver compatible con tu versión de Google Chrome.

## Instalación

1.  **Clona el repositorio:**
    ```bash
    git clone <URL-DEL-REPOSITORIO>
    cd gsmarena-scraper
    ```

2.  **Crea y activa un entorno virtual (recomendado):**
    ```bash
    python -m venv venv
    # En Windows
    venv\Scripts\activate
    # En macOS/Linux
    source venv/bin/activate
    ```

3.  **Instala las dependencias:**
    Crea un archivo `requirements.txt` con el siguiente contenido:
    ```txt
    requests
    beautifulsoup4
    selenium
    ```
    Luego, instálalas:
    ```bash
    pip install -r requirements.txt
    ```

## Uso

El scraper está diseñado para ser ejecutado desde un notebook de Jupyter (o un entorno similar). A continuación se muestra un ejemplo de cómo utilizar la clase `GSMArenaScraper` celda por celda.

1.  **Importar las librerías necesarias e inicializar el scraper:**
    ```python
    from scraper.base import GSMArenaScraper
    import json

    # Inicializar el scraper
    base_url = "https://www.gsmarena.com/makers.php3"
    scraper = GSMArenaScraper(base_url=base_url)
    scraper.say_hello()
    ```

2.  **Obtener la lista de marcas:**
    Esta celda ejecuta el primer paso del scraping para obtener todas las marcas.
    ```python
    scraper.initial_scraper()
    print(f"Marcas encontradas: {len(scraper.brands)}")
    # Descomenta la siguiente línea para ver las marcas
    # print(scraper.brands[:5]) # Muestra las primeras 5
    ```

3.  **Obtener la lista de dispositivos por marca:**
    Esta celda itera sobre las marcas para extraer todos sus modelos.
    *Nota: El método original en `scraper/base.py` tiene un `break` para limitar el scraping a las primeras 3 marcas. Puedes eliminarlo para obtener todos los dispositivos de todas las marcas.*
    ```python
    scraper.brand_scraper()
    print(f"Dispositivos encontrados: {len(scraper.devices)}")
    # Descomenta la siguiente línea para ver los dispositivos
    # print(scraper.devices[:5]) # Muestra los primeros 5
    ```

4.  **Obtener las especificaciones de cada dispositivo:**
    Finalmente, esta celda recorre cada dispositivo para extraer su tabla de especificaciones.
    *Nota: El método original en `scraper/base.py` tiene un `break` para limitar el scraping a los primeros 3 dispositivos. Puedes eliminarlo para obtener las especificaciones de todos.*
    ```python
    scraper.device_scraper()
    print("Scraping de especificaciones completado.")
    ```

5.  **Guardar los resultados:**
    Una vez que el scraping ha finalizado, puedes guardar la lista completa de dispositivos y sus especificaciones en un archivo JSON.
    ```python
    with open('gsmarena_devices.json', 'w', encoding='utf-8') as f:
        json.dump(scraper.devices, f, ensure_ascii=False, indent=4)

    print("Datos guardados en gsmarena_devices.json")
    ```

Al ejecutar estas celdas en orden, los datos extraídos se guardarán en el archivo `gsmarena_devices.json` en el directorio raíz de tu proyecto.

## Documentación del Código

### `scraper/base.py`

Este archivo contiene la clase principal `GSMArenaScraper` que orquesta todo el proceso de scraping.

#### **Clase `GSMArenaScraper`**

##### `__init__(self, base_url: str, pause_every=20)`
-   **Descripción**: Constructor de la clase.
-   **Parámetros**:
    -   `base_url` (str): La URL inicial para comenzar el scraping (la página de marcas).
    -   `pause_every` (int): Parámetro para futuras implementaciones de pausas periódicas (no usado actualmente).
-   **Atributos**:
    -   `self.base_url`: Almacena la URL base.
    -   `self.brands`: Lista para almacenar diccionarios de marcas.
    -   `self.devices`: Lista para almacenar diccionarios de dispositivos.
    -   `self.session`: Una sesión de `requests` para persistencia de cookies y cabeceras.
    -   `self.logger`: Instancia del logger para registrar eventos.

##### `initial_scraper(self)`
-   **Descripción**: Realiza la primera fase del scraping. Obtiene la lista de todas las marcas de teléfonos desde la `base_url`.
-   **Proceso**:
    1.  Realiza una petición GET a `self.base_url`.
    2.  Parsea el HTML con `BeautifulSoup`.
    3.  Encuentra el contenedor de marcas (`<div class="st-text">`).
    4.  Itera sobre cada enlace (`<a>`) para extraer el nombre de la marca, la URL y el número de dispositivos.
    5.  Puebla la lista `self.brands`.

##### `brand_scraper(self)`
-   **Descripción**: Itera sobre la lista de marcas (`self.brands`) y visita la página de cada una para obtener la lista de sus dispositivos.
-   **Proceso**:
    1.  Inicia un driver de `Selenium` (Chrome).
    2.  Para cada marca en `self.brands`:
        a. Navega a la URL de la marca.
        b. Espera a que la página cargue.
        c. Parsea el HTML de la página.
        d. Encuentra el contenedor de dispositivos (`<div class="makers">`).
        e. Itera sobre cada dispositivo para extraer su nombre y URL.
    3.  Puebla la lista `self.devices` con la información de cada dispositivo.
    4.  Cierra el driver de Selenium al finalizar.
-   **Nota**: Este método utiliza `Selenium` porque la lista de dispositivos puede cargarse dinámicamente.

##### `device_scraper(self)`
-   **Descripción**: Itera sobre la lista de dispositivos (`self.devices`) y visita la página de cada uno para extraer sus especificaciones técnicas.
-   **Proceso**:
    1.  Inicia un driver de `Selenium`.
    2.  Para cada dispositivo en `self.devices`:
        a. Navega a la URL del dispositivo.
        b. Espera a que la página cargue.
        c. Parsea el HTML.
        d. Encuentra la tabla de especificaciones (`<div id="specs-list">`).
        e. Itera sobre las filas (`<tr>`) de la tabla para extraer el nombre de la especificación y su valor.
    3.  Actualiza cada diccionario de dispositivo en `self.devices` con un nuevo campo `specs` que contiene las especificaciones.
    4.  Cierra el driver de Selenium al finalizar.

### `scraper/logger.py`

Este módulo proporciona una función de utilidad para configurar un logger estándar.

#### **Función `get_logger(name: str, log_file: str = "scraper.log")`**
-   **Descripción**: Configura y devuelve un objeto `Logger`.
-   **Parámetros**:
    -   `name` (str): El nombre del logger (usualmente `__name__` o el nombre de la clase).
    -   `log_file` (str): El nombre del archivo donde se guardarán los logs. Por defecto es `scraper.log`.
-   **Configuración**:
    -   **Nivel de Log**: `DEBUG` para el archivo y `INFO` para la consola.
    -   **Handlers**:
        -   `FileHandler`: Escribe los logs en `scraper.log`.
        -   `StreamHandler`: Muestra los logs en la consola.
    -   **Formato**: `%(asctime)s [%(levelname)s] %(name)s: %(message)s`.
