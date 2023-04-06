import statbotics


def get_epa(team_num: int) -> int:
    sb = statbotics.Statbotics()
    team_attrs = sb.get_team_year(team_num, 2023)
    epa_mean = team_attrs['epa_mean']
    return epa_mean


def get_epa_list(teams_list: list) -> dict:
    sb = statbotics.Statbotics()
    team_epas = dict()
    for team_num in teams_list:
        try:
            team_attrs = sb.get_team_year(int(team_num), 2023)
            epa_mean = team_attrs['epa_mean']
            team_epas[team_num] = epa_mean
        except UserWarning:
            continue

    return team_epas
