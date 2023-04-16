import yaml
import statbotics_api
import csv
import os


def stats(weightsFile, dbfile, sort_by_epa=False, team_num_attr=None):
    with open("config/{}".format(weightsFile), 'r') as config:
        configuration = yaml.safe_load(config)

    team_attributes = dict()

    best_teams = None  # team number: # ranking score
    if not os.path.exists(dbfile):
        open(dbfile, 'a').close()

    with open(dbfile, 'r+', encoding='utf8') as fp:
        csv_file = csv.DictReader(fp)
        best_teams = dict()  # team number: # ranking score
        for team in csv_file:
            # print(team)
            team_score = 0
            for key, value in team.items():
                if value:
                    # print(key, value)
                    if key in configuration['weights'].keys():
                        team_score += (int(value) * configuration['weights'][key])
                    if key in configuration['values']:
                        team_score += configuration['values'][key][value]

            if not best_teams.get(team['team']):
                best_teams[team['team']] = [team_score]
            else:  # the team has already been entered before
                best_teams[team['team']].append(team_score)  # average all the scores when done
            
            team_number = team['team']
            team_attributes[team_number] = dict()
            for key, value in team.items():
                if value:
                    print(key, value)
                    if key == 'matchnum':
                        continue
                    if key in configuration['weights'].keys() or True:
                        if not team_attributes[team_number].get(key):
                            team_attributes[team_number][key] = [value]
                        else:
                            team_attributes[team_number][key].append(value)
                    if key in configuration['values'] or True:
                        if not team_attributes[team_number].get(key):
                            team_attributes[team_number][key] = [value]
                        else:
                            team_attributes[team_number][key].append(value)

        # average scores and sort teams from best > worst
        for key, value in best_teams.items():
            best_teams[key] = sum(value) / len(value)

        best_teams = dict(sorted(best_teams.items(), key=lambda item: (item[1]), reverse=True))

        if sort_by_epa and best_teams.keys():
            epas_list = statbotics_api.get_epa_list(list(best_teams.keys()))
            best_teams = dict(sorted(best_teams.items(), key=lambda item: (epas_list[int(item[0])]), reverse=True))

        # add team name to attrs
        team_names = statbotics_api.get_teams_names(list(best_teams.keys()))
        for team_number, attrs in team_attributes.items():
            attrs['name'] = [team_names[int(team_number)]]
        return best_teams, team_attributes, configuration


if __name__ == '__main__':
    print(stats("weights.yml", "2023-comp.csv", sort_by_epa=True))