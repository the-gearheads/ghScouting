import yaml
import statbotics_api
import csv
import os


def stats(weightsFile, dbfile, sort_by_epa=False):
    with open("config/{}".format(weightsFile), 'r') as config:
        configuration = yaml.safe_load(config)

    team_attributes = dict()

    best_teams = None  # team number: # ranking score
    if not os.path.exists(dbfile):
        open(dbfile, 'a').close()

    with open(dbfile, 'r+') as fp:
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
                        # print(f"adding {[configuration['values'][key][value]]} to key {key} value {value}")

            if not best_teams.get(team['team']):
                best_teams[team['team']] = [team_score]
            else:  # the team has already been entered before, just average the two scores
                best_teams[team['team']].append(team_score)  # average all the scores when done
            
            #this is not supposed to be here
            team_number = team['team']
            # print(team_number)
            # print(team)
            team_attributes[team_number]=dict()
            for key, value in team.items():
                if value:
                    if key == 'matchnum':
                        continue
                    if key == 'comments':
                        if not team_attributes[team_number].get(key):
                            team_attributes[team_number][key] = [value]
                        else:
                            team_attributes[team_number][key].append(value)
                    if key in configuration['weights'].keys() or True:
                        if not team_attributes[team_number].get(key):
                            team_attributes[team_number][key] = [value]
                        else:
                            team_attributes[team_number][key].append(value)
                    if key in configuration['values'] or True:
                        if not team_attributes[team_number].get(key):
                            # print(key)
                            team_attributes[team_number][key] = [value]
                        else:
                            team_attributes[team_number][key].append(value)

        # average scores and sort teams from best > worst
        for key, value in best_teams.items():
            best_teams[key] = sum(value) / len(value)

        best_teams = dict(sorted(best_teams.items(), key=lambda item: (item[1]), reverse=True))

        if sort_by_epa is True:
            best_teams = {team_id: epa for team_id, epa in (best_teams.keys(), statbotics_api.get_epa_list(list(best_teams.keys())))}
            best_teams = dict(sorted(best_teams.items(), key=lambda item: (item[1]), reverse=True))


        return best_teams, team_attributes, configuration


if __name__ == '__main__':
    print(stats("weights.yml", "/home/ghscouting/ghScouting/2023-comp.csv"))
