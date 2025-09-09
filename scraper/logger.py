import logging

def get_logger(name: str, log_file: str = "scraper.log") -> logging.Logger:
    """
    Configura un logger con salida a archivo y a consola.
    """
    # Obtiene una instancia del logger con el nombre especificado.
    logger = logging.getLogger(name)
    logger.setLevel(logging.DEBUG)  # Cambia a INFO en producción
    # Establece el nivel mínimo de severidad para los mensajes que el logger procesará.
    logger.setLevel(logging.DEBUG)

    # Evita agregar múltiples handlers si el logger ya fue configurado previamente.
    if not logger.handlers:
        # Handler para archivo
        # --- Handler para archivo ---
        # Crea un handler que escribe los logs en un archivo.
        fh = logging.FileHandler(log_file, encoding="utf-8")
        # Establece el nivel de severidad para este handler en particular.
        fh.setLevel(logging.DEBUG)

        # Handler para consola
        # --- Handler para consola ---
        # Crea un handler que envía los logs a la consola (stream).
        ch = logging.StreamHandler()
        # Establece un nivel más alto para la consola, para no llenarla de mensajes de debug.
        ch.setLevel(logging.INFO)

        # Formato común
        # --- Formato común ---
        # Define el formato de los mensajes de log.
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s: %(message)s",
            "%Y-%m-%d %H:%M:%S"
        )
        # Asigna el formato a ambos handlers.
        fh.setFormatter(formatter)
        ch.setFormatter(formatter)

        # Agregar handlers
        # --- Agregar handlers al logger ---
        logger.addHandler(fh)
        logger.addHandler(ch)

    # Devuelve el logger configurado.
    return logger
