import json
import logging


class Logger:
    def __init__(self, name: str):
        self.logger = logging.getLogger(name)
        self.logger.setLevel(logging.INFO)

        handler = logging.StreamHandler()
        self.logger.addHandler(handler)

    def info(self, message: str, **kwargs):
        log = {"message": message, **kwargs}
        self.logger.info(json.dumps(log))
