import sqlite3


class Database:
    def __init__(self, name):
        self.name = name

    def get_name(self):
        return self.name

