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
from markupsafe import Markup


import scouting
import scouting.Database
import scouting.Module_Database
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

def transfer(config):
    page = scouting.Page.Page(config)
    foo = page.content.form
    
    db = scouting.Database.Database(config)
    con = scouting.Page.Config(config).config
    #print(foo) 
    keys = []
    d = {}
    hork = db.get_all("matches")
    keys = db.get_columns()[1:]
    
   
    #print(hork)
    for i in hork:
        team = i[1]
        try:
            d[team] 
        except KeyError:
            d[team] = {}
        for x in range(1, len(keys)):
            try:
                d[team][keys[x]]
            except (KeyError):
                d[team][keys[x]] = []
            d[team][keys[x]].append(i[x+1])
    #print(d)
    b = {}
    
    for team, values in d.items():
        b[team] = {}
        columns = []
        for i in foo:
            #print(values[i.name])
            if issubclass(type(i), scouting.Element.ElementCheckbox):
                w = con[i.name]["options"]
                o = {}
                for y in w:
                    
                    #print(y)
                    #print(values[f"{i.name}_{y}"])
                    o[y] = values[f"{i.name}_{y}"]
                    #print(o[y])
                    try:
                        columns.append(i.args["display"])
                    except KeyError:
                        columns.append(i.name)
                    b[team][i.name] = i.processor(o)
                    
                continue
            if issubclass(type(i), scouting.Element.ElementButton):
                continue
            if issubclass(type(i), scouting.Element.ElementSubmit):
                continue
            if issubclass(type(i), scouting.Element.ElementImage):
                continue
            if i.name == "matchnum" or i.name == "team":
                continue
            try:
                columns.append(i.args["display"])
            except KeyError:
                columns.append(i.name)
            b[team][i.name] = i.processor(values[i.name])
    return b, columns
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
@app.route("/<config>/display")
def display(config):
    con = scouting.Page.Config(config)
    db = scouting.Database.Database(config)
    keys = []
    for value in db.get_columns():
        try:
            keys.append(con.config[value]["display"])
        except KeyError:
            keys.append(value)
            
    return str(keys)
    
@app.route("/<config>/analysis/rank")
def rank_server(config):
    db = scouting.Module_Database.Database(config)
    #transfer(config)
    x, y = transfer(config) 
    data = json.dumps(x)
    col = json.dumps(y)
    ranks = json.dumps((db.get_all("analysis_rank")))
    #print(data, ranks)
    return render_template('analysis/rank.html', ranks=Markup(ranks), data=Markup(data), col=Markup(col))
    
@app.route("/<config>/analysis/post", methods=['POST'])
def post_server(config):
    message = "Post"
    db = scouting.Module_Database.Database(config)
    result = json.loads(request.form['data'])
    for rank, teams in result.items():
        for team in teams:
            db.add(team, rank)
    #print(result)
    #print(db.get_all("analysis_rank"))
    db.commit()
    db.close()
    return render_template('analysis/post.html', message=message)
#@app.route("/<config>/analysis/test")
#def rank_test(config):

    
    
