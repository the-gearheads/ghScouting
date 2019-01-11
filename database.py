import sqlite3, sys


class Database:

    def __init__(self, filename: str):

        self.match = 0
        self.team = 0
        self.queue = {}

        self.filename = filename
        self.connection = sqlite3.connect(self.get_filename())
        self.cursor = self.connection.cursor()
        self.cursor.execute('CREATE TABLE IF NOT EXISTS matches (matchnum, team)')
        self.connection.commit()

    def __check_values_exist__(self):
        self.cursor.execute("SELECT team FROM matches WHERE team = ? AND matchnum = ?", (self.team, self.match))
        if self.cursor.fetchone() is None:
            return False
        return True

    def __check_column_exist__(self, column):
        self.cursor.execute("PRAGMA table_info(matches);")  # Prints columns in table
        for line in self.cursor.fetchall():  # Iterates over lines in pragma output
            if line[1] == column:  # Checks if second element (column name) is equal to the provided column name
                return True
        return False

    def __get_column_count__(self):  # TODO: Merge with check column exist
        self.cursor.execute("PRAGMA table_info(matches);")
        return len(self.cursor.fetchall())

    def add_queue(self, column, value):
        self.queue[column] = value

    def set_match(self, match: int):
        self.match = match

    def set_team(self, team: int):
        self.team = team

    def verify_columns(self, config):
        self.cursor.execute("PRAGMA table_info(matches);")  # Prints columns in table
        for line in self.cursor.fetchall():  # Iterates over lines in pragma output
            if line[1] in config:  # Checks if second element (column name) is equal to the provided column name
                    pass
            else:
                print('ERROR: Config must contain existing values in database! Either add config entry for value "' + line[1] + '" or delete the current database.')
                sys.exit(1) # TODO FIX EXIT

    def create_columns(self, config):
        for key, values in config.items():
            if not self.__check_column_exist__(key):
                print("Created column " + key)
                self.cursor.execute('ALTER TABLE matches ADD COLUMN %s' % key)

    def get_number(self):
        if not self.__check_values_exist__():
            self.cursor.execute('SELECT number FROM matches WHERE team = ? AND matchnum = ?', (self.team, self.match))
            return self.cursor.fetchone()[0]

    def get_filename(self):
        return self.filename+".db"

    def commit(self):
        for key, value in self.queue.items():  # Iterate through queue
            print("About to create row with matchnum and team: " + self.match + " " + self.team)
            if not self.__check_values_exist__():
                print("Creating row with matchnum and team: " + self.match + " " + self.team)
                self.cursor.execute(
                    'INSERT INTO matches (matchnum,team) VALUES (?,?)',
                    (self.match, self.team,)
                )
                self.cursor.execute('SELECT team FROM matches WHERE matchnum = %s' % self.match)
                print(self.cursor.fetchone())

            print("Setting " + key + " to " + value)
            self.cursor.execute(  # TODO: currently only works when row already exists
                'UPDATE matches SET %s = ? WHERE team = ? and matchnum = ?' % key,
                (value, self.team, self.match)
            )

        self.connection.commit()
        print("Values set!")

    def close(self):
        self.connection.close()
