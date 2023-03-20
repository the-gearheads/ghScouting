from flask import Flask, Response, request, redirect, render_template, send_from_directory, flash, url_for
import werkzeug.wrappers
import analysis
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


@app.route("/stats", methods=["POST", "GET"])  # we probably don't need POST anymore, too scared to test
def stats():
    team_number = request.args.to_dict().get('team_number')
    best_teams, team_attributes, configuration = analysis.stats()
    filter_attrs = set()
    for team_num, attrs in team_attributes.items():
        for attr in attrs:
            if attr in configuration['weights']:
                filter_attrs.add(attr)
    return render_template("stats.html", team_number=team_number, best_teams=best_teams, team_attributes=team_attributes, configuration=configuration, filter_attrs=filter_attrs)


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
