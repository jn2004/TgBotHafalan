import re
import glob

from botme import logger


def modules():
    for i in glob.glob("*/*/*.py"):
        if not i.endswith("__init__.py"):
            yield re.sub(r".+/|.py", "", i)

modules = list(tuple(modules()))
logger.info(f"Berhasil menghidupkan {len(modules)} modul : {modules}")
