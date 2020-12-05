import importlib

from botme import updater, logger
from botme.core import modules

for module in modules:
    importlib.import_module(f"botme.core.{module}")


if __name__ == "__main__":
    updater.start_polling()
    logger.info("Listening using polling")
    updater.idle()
