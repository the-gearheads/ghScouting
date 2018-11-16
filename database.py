import sqlite3


class Database:

    def __init__(self, filename: str):
        self.attributes = ["string", "number", "boolean"]
        self.match = 0
        self.team = 0
        self.string = "default"
        self.number = 0
        self.boolean = 0

        self.filename = filename
        self.connection = sqlite3.connect(self.get_filename())
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS matches (matchnum, team, number, boolean, string)')
        self.connection.commit()

    def __set_def_values__(self):
        if not self.__check_values_exist__():
            self.cursor.execute('INSERT INTO matches VALUES (?,?,?,?,?)', (self.match, self.team, 0, False, 'Default'))

    def __check_values_exist__(self):
        self.cursor.execute("SELECT team FROM matches WHERE team = ? AND matchnum = ?", (self.team, self.match))
        if self.cursor.fetchone() is None:
            return False
        return True

    def set_match(self, match: int):
        self.match = match

    def set_team(self, team: int):
        self.team = team

    def set_number(self, number: int):
        self.number = number

    def set_boolean(self, boolean: bool):
        self.boolean = boolean

    def set_string(self, string: str):
        self.string = string

    def get_number(self):
        if not self.__check_values_exist__():
            self.cursor.execute('SELECT number FROM matches WHERE team = ? AND matchnum = ?', (self.team, self.match))
            return self.cursor.fetchone()[0]

    def get_filename(self):
        return self.filename+".db"

    def commit(self):
        self.__set_def_values__()
        self.cursor.execute("UPDATE matches SET number = ?, boolean = ?, string = ? WHERE team = ? AND matchnum = ?", (self.number, self.boolean, self.string, self.team, self.match))
        self.connection.commit()

    def close(self):
        self.connection.close()
