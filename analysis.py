import yaml
import csv


def stats():
    with open("config/weights.yml", 'r') as config:
        configuration = yaml.safe_load(config)

    team_number = None
    team_attributes = dict()
    best_teams = dict()  # team number: # ranking score
    with open("eggs.csv", 'r') as fp:
        csv_file = csv.DictReader(fp)

        if not team_number:
            for team in csv_file:
                team_score = 0
                for key, value in team.items():
                    # print(f"\t{key, value}")
                    if value:
                        if key in configuration['weights'].keys():
                            team_score += (int(value) * configuration['weights'][key])
                        if key in configuration['values']:
                            team_score += configuration['values'][key][value]
                        team_attributes[key] = value

                if not best_teams.get(team['team']):
                    best_teams[team['team']] = [team_score]
                else:  # the team has already been entered before, just average the two scores
                    best_teams[team['team']].append(team_score)  # average all the scores when done

            # average scores and sort teams from best > worst
            for key, value in best_teams.items():
                best_teams[key] = sum(value) / len(value)
            best_teams = dict(sorted(best_teams.items(), key=lambda item: item[1], reverse=True))

        else:
            for team in csv_file:
                for key, value in team.items():
                    if value:
                        if key == 'matchnum':
                            continue
                        if key in configuration['weights'].keys():
                            if team_attributes.get(key):
                                team_attributes[key] = value
                            else:
                                team_attributes[key] = value
                        if key in configuration['values']:
                            team_attributes[key] = value  # TODO: add averaging for values and weights in attributes

        return best_teams


if __name__ == '__main__':
    print(stats())
