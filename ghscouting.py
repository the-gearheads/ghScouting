from flask import Flask, request, redirect, render_template, send_from_directory, flash
import functools
import werkzeug.wrappers
import traceback
import yaml
import yaml.scanner
import collections
import psutil
import shutil
import os
import json

import scouting
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


### RANK STUFF (MOVE)

@app.route("/<config>/analysis/rank")
def rank_server(config):
    message = "Rank"
    return render_template('analysis/rank.html', message=message)
    
@app.route("/<config>/analysis/post", methods=['POST'])
def post_server(config):
    message = "Post"
    print(request.form['data'])
    result = json.loads(request.form['data'])
    print(result['S'])
    return render_template('analysis/post.html', message=message)
#@app.route("/<config>/analysis/test")
#def rank_test(config):
    