import sqlite3


class Database:
    def __init__(self, filename: str):
        self.match = 0
        self.team = 0
        self.string = "default"
        self.number = 0
        self.boolean = 0

        self.filename = filename
        self.connection = sqlite3.connect(filename + '.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS matches (matchnum, team, number, boolean, string)')
        # self.cursor.execute('INSERT INTO teams VALUES (?,?,?,?)', (self.team, 0, False, 'Default'))
        self.connection.commit()

    def __set_def_values__(self):
        if not self.check_stats_exist():
            self.cursor.execute('INSERT INTO matches VALUES (?,?,?,?)', (self.team, 0, False, 'Default'))
            self.commit()

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
        self.cursor.execute('SELECT number FROM teams WHERE team=? AND matchnum=?', (self.team, self.match))
        return self.cursor.fetchone()[0]

    def get_filename(self):
        return self.filename+".db"

    def check_stats_exist(self):
        self.cursor.execute("SELECT team FROM teams WHERE team = ? AND matchnum=? ", (self.team, self.match))
        return self.cursor.fetchone()

    def commit(self):
        self.__set_def_values__()
        # self.cursor.execute('UPDATE ') # TODO: finish this

    def close(self):
        self.connection.close()
