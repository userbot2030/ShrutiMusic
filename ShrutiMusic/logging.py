# ShrutiMusic/logging.py
import logging

# Basic configuration (sesuaikan level/format sesuai kebutuhan Anda)
logging.basicConfig(
    level=logging.INFO,
    format="%(asctime)s - %(name)s - %(levelname)s - %(message)s",
)

# Export a real Logger instance (not a factory function)
LOGGER = logging.getLogger("ShrutiMusic")
