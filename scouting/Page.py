from asyncio.windows_events import NULL
from pathlib import Path

import yaml

import scouting


class Page:
    def __init__(self, name):
        self.PAGE_TYPES = {"form": scouting.Form.Form, "menu": scouting.Form.Menu}
        self.config = Config(name)
        print(self.config.config)
        self.type = self.config.config["page_type"]
        self.content = self.__create_content__()

    def __create_content__(self):
        if self.type in self.PAGE_TYPES:
            return self.PAGE_TYPES[self.type](self.config)
        return None

    def get_page(self, app):
        if self.content:
            return self.content.get_page(app)
        raise AttributeError("Page has no content")

    def process_post(self):
        if self.content:
            return self.content.process_post()
        raise AttributeError("Page has no content")


class Config:
    def __init__(self, name):
        self.name = name
        self.config = self.__create_config__(name)

    def __create_config__(self, name):
        try:
            form = Path("config")
            with open(form / f"{name}.yml") as stream:
                return yaml.full_load(stream)
        except (FileNotFoundError, yaml.scanner.ScannerError) as e:
            return e
