import importlib

from botme import updater, logger, j
from botme.core import modules, function
from botme.core.database import db

for module in modules:
    importlib.import_module(f"botme.core.{module}")


if __name__ == "__main__":
    if db.getid() or db.start(method="GET"):
        for i in db.start(method="GET"):
            if not j.get_job(str(i[0])):
                j.add_job(
                    function.ask,
                    "interval",
                    hours=db.interval(i[0], "GET")[1],
                    args=(int(i[0]),),
                    id=str(i[0]),
                )
    updater.start_polling()
    logger.info("Listening using polling")
    

    updater.idle()
