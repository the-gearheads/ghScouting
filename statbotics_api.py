import statbotics
import pathlib
from datetime import datetime, timedelta
import pickle
import sqlite3
# from threading import Lock


def get_epa(team_num: str, year: int = 2023) -> int:
    refresh_epa_listings(year)
    conn = sqlite3.connect("internal_data/team_epas.db")
    curs = conn.cursor()
    curs.execute("SELECT epa FROM epas WHERE num = ?", (team_num,))
    epa_mean = curs.fetchone()
    return epa_mean


def get_epa_list(teams_list: list, year: int = 2023):
    refresh_epa_listings(year)

    conn = sqlite3.connect("internal_data/team_epas.db")
    curs = conn.cursor()
    curs.execute("SELECT num, epa FROM epas ORDER BY epa DESC")
    team_epas = dict(curs.fetchall())
    teams_list = list(map(int, teams_list))
    unadded_teams = list(set((team_epas.keys() | teams_list) - (team_epas.keys() & set(teams_list))))  # get unique items (not in cache file yet)
    if unadded_teams:
        add_epa_listings(unadded_teams)
        curs.execute("SELECT num, epa FROM epas ORDER BY epa DESC")
        team_epas | dict(curs.fetchall())

    return team_epas


# update the epas list if it hasn't been in at least 10 minutes
def refresh_epa_listings(year=2023):
    epas_path = pathlib.Path('internal_data/team_epas.db')
    if not epas_path.exists():
        conn = sqlite3.connect("internal_data/team_epas.db")
        curs = conn.cursor()
        curs.execute("CREATE TABLE IF NOT EXISTS epas (num INTEGER PRIMARY KEY, epa REAL NOT NULL, name)")
        conn.commit()
        conn.close()
    mod_stamp = epas_path.stat().st_mtime
    mod_time = datetime.fromtimestamp(mod_stamp)  # tz=datetime.timezone.utc
    offset = datetime.now() - timedelta(minutes=10)

    if offset > mod_time:  # if last modified more than 10 minutes ago
        conn = sqlite3.connect("internal_data/team_epas.db")
        curs = conn.cursor()
        curs.execute("CREATE TABLE IF NOT EXISTS epas (num INTEGER PRIMARY KEY, epa REAL NOT NULL, name)")
        sb = statbotics.Statbotics()
        curs.execute("SELECT num FROM epas")
        rows = curs.fetchall()
        for row in rows:
            team_num = row[0]
            try:
                team_attrs = sb.get_team_year(int(team_num), year)
                epa_end = team_attrs['epa_end']
            except UserWarning:
                epa_end = 0

            curs.execute("UPDATE epas SET epa = ? WHERE num == ?", (epa_end, team_num))
        conn.commit()
        conn.close()


def add_epa_listings(teams_list: list, year: int = 2023):
    conn = sqlite3.connect("internal_data/team_epas.db")
    curs = conn.cursor()
    curs.execute("CREATE TABLE IF NOT EXISTS epas (num INTEGER PRIMARY KEY, epa REAL NOT NULL, name)")
    sb = statbotics.Statbotics()

    for team_num in teams_list:
        try:
            team_attrs = sb.get_team_year(int(team_num), year)
            epa_end = team_attrs['epa_end']
            team_name = team_attrs['name']
        except UserWarning as e:
            epa_end = 0
            team_name = "Team Not Found"

        curs.execute("INSERT OR REPLACE INTO epas VALUES(?, ?, ?)", (team_num, epa_end, team_name))
    conn.commit()
    conn.close()


def get_teams_names(teams_list: list, year: int = 2023):
    refresh_epa_listings(year)

    conn = sqlite3.connect("internal_data/team_epas.db")
    curs = conn.cursor()
    curs.execute("SELECT num, name FROM epas ORDER BY epa DESC")
    team_epas = dict(curs.fetchall())
    teams_list = list(map(int, teams_list))
    unadded_teams = list(set((team_epas.keys() | teams_list) - (
                team_epas.keys() & set(teams_list))))  # get unique items (not in cache file yet)
    if unadded_teams:
        add_epa_listings(unadded_teams)
        curs.execute("SELECT num, name FROM epas ORDER BY epa DESC")
        team_epas | dict(curs.fetchall())

    return team_epas


# just for testing
if __name__ == "__main__":
    # refresh_epa_listings([1189, 2075, 118, 1], 2023)
    get_epa_list([1189, 2075, 118, 1, 4], 2023)
    print(get_epa('1189'))
