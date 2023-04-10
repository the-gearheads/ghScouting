import statbotics
import shelve
# from threading import Lock


def get_epa(team_num: int, year: int = 2023) -> int:
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
