import sqlite3
import os
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
        self.cursor.execute("CREATE TABLE IF NOT EXISTS rank (team, rank)")
        self.connection.commit()

    def __check_values_exist__(self, team):
        self.cursor.execute(
            "SELECT team FROM rank WHERE team = ?",
            (team, ),
        )
        if self.cursor.fetchone() is None:
            return False
        return True
    
    def get_filename(self):
        return self.filename + ".db"

    def commit(self):
        for team, rank in self.queue.items():  # Iterate through queue
            print(team, rank)
            if not self.__check_values_exist__(team):
                print(
                    "Creating row with team: {}".format(
                        team
                    )
                )
                self.cursor.execute(
                    "INSERT INTO ranks (?) VALUES (?)",
                    (team, rank),
                )
                
            self.cursor.execute(
                "UPDATE ranks SET rank = ? WHERE team = ?".format(key),
                (value, team),
            )
        self.connection.commit()
        print("Values set!")
    def add(self, team, rank):
        self.queue[team]= rank 
        
    def close(self):
        self.connection.close()
