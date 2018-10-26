import sqlite3


class Database:
    def __init__(self, filename: str):
        self.team = 0
        self.filename = filename
        self.connection = sqlite3.connect(filename + '.db')
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS teams (team, number, boolean, string)')
        # self.cursor.execute('INSERT INTO teams VALUES (?,?,?,?)', (self.team, 0, False, 'Default'))
        self.connection.commit()

    def __set_def_values__(self):
        self.cursor.execute('INSERT INTO teams VALUES (?,?,?,?)', (self.team, 0, False, 'Default'))
        self.commit()

    def set_team(self, team: int):
        self.team = team
        if not self.check_team():
            self.__set_def_values__()

    def check_team(self):
        self.cursor.execute("SELECT team FROM teams WHERE team = ?", (self.team,))
        return self.cursor.fetchone()

    def set_number(self, number: int):
        self.cursor.execute('UPDATE teams SET number=? WHERE team=?', (number, self.team))
        self.commit()

    def set_boolean(self, boolean: bool):
        self.cursor.execute('UPDATE teams SET boolean=? WHERE team=?', (boolean, self.team))
        self.commit()

    def set_string(self, string: str):
        self.cursor.execute('UPDATE teams SET string=? WHERE team=?', (string, self.team))
        self.commit()

    def get_number(self):
        self.cursor.execute('SELECT number FROM teams')
        return self.cursor.fetchone()[0]

    def get_filename(self):
        return self.filename+".db"

    def commit(self):
        self.connection.commit()

    def close(self):
        self.connection.close()
