import logging

def configure_logging(log_level: str = "INFO"):
    # Define the mapping between log level strings and logging constants
    log_level_mapping = {
        "DEBUG": logging.DEBUG,
        "INFO": logging.INFO,
        "WARNING": logging.WARNING,
        "ERROR": logging.ERROR,
        "CRITICAL": logging.CRITICAL,
    }

    # Get the log level from the mapping, defaulting to logging.INFO
    log_level_const = log_level_mapping.get(log_level.upper(), logging.INFO)


    # Create a custom formatter with colors
    class ColoredFormatter(logging.Formatter):
        COLOR_CODES = {
            logging.DEBUG: "\033[94m",  # Bright blue
            logging.INFO: "\033[92m",   # Bright green
            logging.WARNING: "\033[93m",  # Bright yellow
            logging.ERROR: "\033[91m",  # Bright red
            logging.CRITICAL: "\033[91m",  # Bright red
        }

        def format(self, record):
            color_code = self.COLOR_CODES.get(record.levelno, "")
            reset_code = "\033[0m"
            level_name = record.levelname
            level_name_length = len(level_name)
            padding = max(0, 8 - level_name_length)
            padding_spaces = " " * padding
            log_format = f"{level_name}{reset_code}:{padding_spaces} %(asctime)s.%(msecs)03d - %(message)s"
            formatter = logging.Formatter(log_format, datefmt="%d.%m.%Y %H:%M:%S")
            formatted_message = formatter.format(record)
            return f"{color_code}{formatted_message}"

    # Create a handler for console output
    console_handler = logging.StreamHandler()
    console_handler.setLevel(log_level_const)

    # Create a formatter and set it for the handler
    formatter = ColoredFormatter()
    console_handler.setFormatter(formatter)

    # Get the root logger
    root_logger = logging.getLogger()
    root_logger.setLevel(log_level_const)

    # Remove existing handlers (if any)
    for handler in root_logger.handlers:
        root_logger.removeHandler(handler)

    # Add the console handler to the root logger
    root_logger.addHandler(console_handler)