import statbotics
import pathlib
from datetime import datetime, timedelta, timezone
import shelve
# from threading import Lock


def get_epa(team_num: int, year: int = 2023) -> int:
    refresh_epa_listings([team_num], year)
    team_num = str(team_num)
    # mutex = Lock()
    # mutex.acquire()
    with shelve.open("internal_data/team_epas") as epas_list:
        if team_num in epas_list.keys():
            epa_mean = str(epas_list[team_num])
        else:
            try:
                sb = statbotics.Statbotics()
                team_attrs = sb.get_team_year(int(team_num), year)
                epa_mean = team_attrs['epa_mean']
                epas_list[str(team_num)] = str(epa_mean)
            except UserWarning:
                epa_mean = None
    # mutex.release()
    return epa_mean


def get_epa_list(teams_list: list, year: int = 2023) -> dict:
    refresh_epa_listings(teams_list, year)
    sb = statbotics.Statbotics()
    team_epas = dict()
    # mutex = Lock()
    # mutex.acquire()
    with shelve.open("internal_data/team_epas") as epas_list:
        for team_num in teams_list:
            if team_num in epas_list.keys():
                epa_mean = epas_list[team_num]
                team_epas[team_num] = epa_mean
            else:
                try:
                    team_attrs = sb.get_team_year(int(team_num), year)
                    epa_mean = team_attrs['epa_mean']
                    epas_list[team_num] = epa_mean
                    team_epas[team_num] = epa_mean
                except UserWarning:
                    continue
    # mutex.release()
    return team_epas


# update the epas list if it hasnt been in at least 10 minutes
def refresh_epa_listings(teams_list: int, year: int):
    epas_file = pathlib.Path('internal_data/team_epas')
    if epas_file.exists():
        mod_stamp = epas_file.stat().st_mtime
        mod_time = datetime.fromtimestamp(mod_stamp)  # tz=datetime.timezone.utc
        offset = datetime.now() - timedelta(minutes=10)

    if offset > mod_time or not epas_file.exists():  # if last modified more than 10 minutes ago
        print("refreshing epa file data...")
        sb = statbotics.Statbotics()
        with shelve.open("internal_data/team_epas") as epas_list:
            for team_num in teams_list:
                try:
                    team_attrs = sb.get_team_year(int(team_num), year)
                    epa_mean = team_attrs['epa_mean']
                    epas_list[str(team_num)] = epa_mean
                except UserWarning:
                    continue


if __name__ == "__main__":
    refresh_epa_listings([1189, 2075], 2023)