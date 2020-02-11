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
        self.cursor.execute("CREATE TABLE IF NOT EXISTS analysis_rank (team, rank)")
        self.connection.commit()

    def __check_values_exist__(self, team):
        self.cursor.execute(
            "SELECT team FROM analysis_rank WHERE team = ?",
            (team, ),
        )
        if self.cursor.fetchone() is None:
            return False
        return True
    
    def get_filename(self):
        return self.filename + ".db"
    
    def get_all(self, table):
        self.connection.row_factory = dict_factory
        self.cursor.execute(f"SELECT * FROM {table}") 
        data = self.cursor.fetchall()
        d = {}
        for item in data:
            d[item[0]] = item[1:]
        return d
    
        

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
                    "INSERT INTO analysis_rank(team, rank) VALUES (?, ?)",
                    (team, rank)
                )
                self.connection.commit()
                
            self.cursor.execute(
                "UPDATE analysis_rank SET rank = ? WHERE team = ?",
                (rank, team),
            )
        self.connection.commit()
        print("Values set!")
    def add(self, team, rank):
        self.queue[team]= rank 
        
    def close(self):
        self.connection.close()
        
def dict_factory(cursor, row):
    d = {}
    for idx, col in enumerate(cursor.description):
        d[col[0]] = row[idx]
    return d