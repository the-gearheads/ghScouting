import sqlite3
import csv
import io

import scouting.Element


class Database:
    def __init__(self, filename: str):

        self.match = 0
        self.team = 0
        self.queue = {}

        self.filename = filename
        self.connection = sqlite3.connect(self.get_filename())
        self.cursor = self.connection.cursor()
        self.cursor.execute("CREATE TABLE IF NOT EXISTS matches (matchnum, team)")
        self.connection.commit()

    def __check_values_exist__(self):
        self.cursor.execute(
            "SELECT team FROM matches WHERE team = ? AND matchnum = ?",
            (self.team, self.match),
        )
        if self.cursor.fetchone() is None:
            return False
        return True

    def __check_column_exist__(self, column):
        self.cursor.execute("PRAGMA table_info(matches);")  # Prints columns in table
        for line in self.cursor.fetchall():  # Iterates over lines in pragma output
            if (
                line[1] == column
            ):  # Checks if second element (column name) is equal to the provided column name
                return True
        return False

    def __get_column_count__(self):  # TODO: Merge with check column exist
        self.cursor.execute("PRAGMA table_info(matches);")
        return len(self.cursor.fetchall())

    def __get_columns__(self):
        self.cursor.execute("PRAGMA table_info(matches);")
        return self.cursor.fetchall()

    def add_queue(self, column, value):
        self.queue[column] = value

    def set_match(self, match: int):
        self.match = match

    def set_team(self, team: int):
        self.team = team

    def list_columns(self):
        self.cursor.execute("PRAGMA table_info(matches);")
        return self.cursor.fetchall()

    def create_columns(self, config):
        names = []
        for item in config:
            if not item.display_field:
                if issubclass(type(item), scouting.Element.ElementCheckbox):
                    for option in item.args["options"]:
                        print(f"{item.name}_{option}")
                        names.append(f"{item.name}_{option}")
                else:
                    names.append(item.name)
        for name in names:
            if not self.__check_column_exist__(name):
                print("Creating column " + name)
                self.cursor.execute(f"ALTER TABLE matches ADD COLUMN '{name}'")

        # for key, values in config.items():
        #     if (
        #         not self.__check_column_exist__(key)
        #         and config[key].get("metatype") != "display"
        #     ):
        #         print("Creating column " + key)
        #         self.cursor.execute("ALTER TABLE matches ADD COLUMN {}".format(key))
        #     if values["type"] == "checkbox":
        #         for option in config[key]["options"]:
        #             column_name = f"{key}_{option}"
        #             if not self.__check_column_exist__(column_name):
        #                 print("Creating column " + column_name)
        #                 self.cursor.execute(
        #                     "ALTER TABLE matches ADD COLUMN {}".format(column_name)
        #                 )

    def get_number(self):
        if not self.__check_values_exist__():
            self.cursor.execute(
                "SELECT number FROM matches WHERE team = ? AND matchnum = ?",
                (self.team, self.match),
            )
            return self.cursor.fetchone()[0]

    def get_filename(self):
        return self.filename + ".db"

    def gen_csv(self):
        columns = list(map(lambda x: x[1], self.__get_columns__()))
        self.cursor.execute("SELECT * FROM matches")
        data = self.cursor.fetchall()
        csv_data = io.StringIO(newline="")
        writer = csv.writer(csv_data)
        writer.writerow(columns)
        writer.writerows(data)
        with open('eggs.csv', 'w', newline='') as csvfile:
            spamwriter = csv.writer(csvfile)
            spamwriter.writerow(columns)
            spamwriter.writerows(data)
        return csv_data

    def commit(self):
        for key, value in self.queue.items():  # Iterate through queue
            if not self.__check_values_exist__():
                print(
                    "Creating row with matchnum and team: {} {}".format(
                        self.match, self.team
                    )
                )
                self.cursor.execute(
                    "INSERT INTO matches (matchnum,team) VALUES (?,?)",
                    (self.match, self.team),
                )
                self.cursor.execute(
                    "SELECT team FROM matches WHERE matchnum = {}".format(self.match)
                )

            print("Setting " + key + " to " + str(value))

            if value is True:
                value = "true"

            self.cursor.execute(
                "UPDATE matches SET '{}' = ? WHERE team = ? and matchnum = ?".format(key),
                (value, self.team, self.match),
            )

        self.connection.commit()
        print("Values set!")

    def close(self):
        self.connection.close()
