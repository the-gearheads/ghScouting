from flask import Flask, Response, request, redirect, render_template, send_from_directory, flash, url_for, send_file
import werkzeug.wrappers
import analysis
import traceback
import yaml
import yaml.scanner
import psutil
import csv
import os
import statbotics_api

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

main_config = scouting.Page.Config("config", "eggs.csv")
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


@app.route("/stats", methods=["POST", "GET"])  # we probably don't need POST anymore, too scared to test
def stats():
    best_teams, team_attributes, configuration = analysis.stats("weights.yml", "2023-comp.csv", sort_by_epa=True)
    filter_attrs = set()
    epas_dict = statbotics_api.get_epa_list(list(team_attributes.keys()))
    for team_num, attrs in team_attributes.items():
        for attr in attrs:
            if attr in configuration['weights']:
                filter_attrs.add(attr)
    return render_template("stats.html", best_teams=best_teams, team_attributes=team_attributes, configuration=configuration, filter_attrs=filter_attrs, epas_dict=epas_dict)


@app.route("/pitstats", methods=["POST", "GET"])
def pitstats():
    best_teams, team_attributes, configuration = analysis.stats("weights2.yml", "pit.csv")
    filter_attrs = set()

    for team_num, attrs in team_attributes.items():
        for attr in attrs:
            if attr in configuration['weights']:
                filter_attrs.add(attr)
    return render_template("stats.html", best_teams=best_teams, team_attributes=team_attributes, configuration=configuration, filter_attrs=filter_attrs)


@app.route("/drivestats", methods=["POST", "GET"])
def drivestats():
    best_teams, team_attributes, configuration = analysis.stats("driveweights.yml", "driveteam.csv")
    filter_attrs = set()
    for team_num, attrs in team_attributes.items():
        for attr in attrs:
            if attr in configuration['weights']:
                filter_attrs.add(attr)
    return render_template("stats.html", best_teams=best_teams, team_attributes=team_attributes, configuration=configuration, filter_attrs=filter_attrs)


@app.route("/<config>")
def display_page(config):
    page = scouting.Page.Page(config, f"{config}.csv")

    if isinstance(page.config, Exception):  # Check config threw an exception
        return return_error(page)

    try:
        return page.get_page(app)
    except Exception as e:
        return return_error(config, traceback.format_exc())


@app.route("/<config>", methods=["POST"])
def page_post(config):
    page = scouting.Page.Page(config, f"{config}.csv")

    if isinstance(page.config, Exception):  # Check config threw an exception
        return return_error(page)

    try:
        return page.process_post()
    except Exception as e:
        return return_error(config, traceback.format_exc())


@app.route("/<config>/csv")
def gen_csv(config):
    page = scouting.Page.Page(config, f"{config}.csv")
    if page.type == "form":
        db = scouting.Database.Database(config)
#        return send_file(f"{config}.csv", mimetype='"text/csv"', as_attachment=True, attachment_filename="data.csv")
#        return db.gen_csv().getvalue()
        return send_from_directory(".", "pit.csv", attachment_filename="data.csv")
    return return_error(config, "Cannot generate a csv for a non-form page")
