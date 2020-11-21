import os
from botme import logger

os.chdir("botme/core")


def _modules():
    _all = (
        i.replace(".py", "")
        for i in os.listdir()
        if "__init__.py" not in i and i.endswith(".py")
    )

    return _all


modules = list(tuple(_modules()))
logger.info(f"Berhasil menghidupkan {len(modules)} modul : {modules}")
