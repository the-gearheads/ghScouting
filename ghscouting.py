from flask import Flask, Response, request, redirect, render_template, send_from_directory, flash, url_for
import werkzeug.wrappers
import traceback
import yaml
import yaml.scanner
import psutil
import csv
import os

import scouting.Database
import scouting.Element
import scouting.Form
import scouting.Page


# blatantly stolen from Flask snippets
def authenticate():
    """Sends a 401 response that enables basic auth"""

    return werkzeug.wrappers.Response(
        "Login to page failed",
        401,
        {"WWW-Authenticate": 'Basic realm="Login Required"'},
    )


def check_auth(request, username, password):
    auth = request.authorization
    if auth and (auth.username == username and auth.password == password):
        return
    return authenticate()


def return_error(name, page_data):
    return werkzeug.wrappers.Response(
        f"<title>Gearheads Scouting</title>\n"
        f"<h2>The following error was encountered while processing {name}:</h2>\n"
        f"<span style='white-space: pre-line'>{page_data}</span>",
        200,
        mimetype="text/html",
    )


app = Flask(__name__)

main_config = scouting.Page.Config("config")
gh_config = {f"gh_{k}": v for k, v in main_config.config.items()}
app.config.update(gh_config)

app.secret_key = app.config["gh_secret_key"]
app.jinja_env.trim_blocks = True
app.jinja_env.lstrip_blocks = True


@app.route("/favicon.ico")
def favicon():
    return send_from_directory(
        os.path.join(app.root_path, "static"),
        "favicon.ico",
        mimetype="image/vnd.microsoft.icon",
    )


@app.route("/")
def root():
    # Get default form from config
    return redirect("/" + app.config["gh_default"])


@app.route("/getCSV")
def getCSV():
    with open("eggs.csv") as fp:
        csv = fp.read()
    # csv = '1,2,3\n4,5,6\n'
    return Response(
        csv,
        mimetype="text/csv",
        headers={"Content-disposition":
                 "attachment; filename=data.csv"})


@app.route("/stats", methods=["POST", "GET"])
def stats():
    if request.method == "POST":
        return url_for('stats', team_number=request.form['team_number'])

    else:
        with open("config/weights.yml", 'r') as config:
            configuration = yaml.safe_load(config)

        team_number = request.args.to_dict().get('team_number')
        team_attributes = dict()
        best_teams = dict()  # team number: ranking score

        with open("eggs.csv", 'r') as fp:
            csv_file = csv.DictReader(fp)

            if not team_number:
                for team in csv_file:
                    print(team)
                    team_score = 0
                    for key, value in team.items():
                        print(f"\t{key, value}")
                        if value:
                            if key in configuration['weights'].keys():
                                team_score += (int(value) * configuration['weights'][key])
                            if key in configuration['values']:
                                team_score += int(configuration['values'][key][value])

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

    return render_template("stats.html", team_number=team_number, best_teams=best_teams, team_attributes=team_attributes)


@app.route("/<config>")
def display_page(config):
    page = scouting.Page.Page(config)

    if isinstance(page.config, Exception):  # Check config threw an exception
        return return_error(page)

    try:
        return page.get_page(app)
    except Exception as e:
        return return_error(config, traceback.format_exc())


@app.route("/<config>", methods=["POST"])
def page_post(config):
    page = scouting.Page.Page(config)

    if isinstance(page.config, Exception):  # Check config threw an exception
        return return_error(page)

    try:
        return page.process_post()
    except Exception as e:
        return return_error(config, traceback.format_exc())


@app.route("/<config>/csv")
def gen_csv(config):
    page = scouting.Page.Page(config)
    if page.type == "form":
        db = scouting.Database.Database(config)
        return db.gen_csv().getvalue()
    return return_error(config, "Cannot generate a csv for a non-form page")
