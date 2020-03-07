from flask import Flask, request, redirect, render_template, send_from_directory, flash
import werkzeug.wrappers
import traceback
import yaml
import yaml.scanner
import psutil
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
    keys = []
    d = {}
    data = db.get_all("matches")
    keys = db.get_columns()[1:]
    for i in data:
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
    raw_data = {}
    col_data = {}
    col_wth_value = set()
    special_col = {}
    for team, values in d.items():
        raw_data[team] = {}
        col_data[team] = {}
        columns = []
        newColumns = []
        for i in foo:
            if issubclass(type(i), scouting.Element.ElementCheckbox):
                w = con[i.name]["options"]
                try: 
                    special_col[i.args["display"]] = w
                except KeyError:
                    special_col[i.name] = w
                o = {}
                for y in w:
                    value = str(y)
                    o[y] = values[f"{i.name}_{y}"]
                    try:
                        newColumns.append(i.args["display"])
                        col_wth_value.add(i.args["display"]+"_"+value)
                    except KeyError:
                        newColumns.append(i.name)
                        col_wth_value.add(i.name+"_"+value)
                    raw_data[team][i.name] = i.processor(o)
                    try:
                        if value == i.processor(o):
                            col_data[team][i.args["display"]+"_"+value] = i.processor(o)
                        else:
                            col_data[team][i.args["display"]+"_"+value] = None
                    except KeyError:
                        if value == i.processor(o):
                            col_data[team][i.name+"_"+value] = i.processor(o)
                        else:
                            col_data[team][i.name+"_"+value] = None
                        
                        
                    
                    
                    
                continue
            if issubclass(type(i), scouting.Element.ElementSelect):
                w = con[i.name]["options"]
                try: 
                    special_col[i.args["display"]] = w
                except KeyError:
                    special_col[i.name] = w
                for y in w:
                    value = str(y)
                    try:
                        newColumns.append(i.args["display"])
                        col_wth_value.add(i.args["display"]+"_"+value)
                    except KeyError:
                        newColumns.append(i.name)
                        col_wth_value.add(i.name+"_"+value)
                    raw_data[team][i.name] = i.processor(values[i.name])
                    try:
                        if value == i.processor(values[i.name]):
                            col_data[team][i.args["display"]+"_"+value] = i.processor(values[i.name])
                        else:
                            col_data[team][i.args["display"]+"_"+value] = None
                    except KeyError:
                        if value == i.processor(values[i.name]):
                            col_data[team][i.name+"_"+value] = i.processor(values[i.name])
                        else:
                            col_data[team][i.name+"_"+value] = None
                        
                        
                    
                    
                continue
            if issubclass(type(i), scouting.Element.ElementTextarea):
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
                if con[i.name]["options"] == None:
                    
                    columns.append(i.args["display"])
                else:
                    pass
                newColumns.append(i.args["display"])
            except KeyError:
                newColumns.append(i.args["display"])
                columns.append(i.args["display"])
            raw_data[team][i.name] = i.processor(values[i.name])
            try:
                col_data[team][i.args["display"]] = i.processor(values[i.name])
            except KeyError:
                col_data[team][i.name] = i.processor(values[i.name])
    print(columns)
    return raw_data, columns, col_data, col_wth_value, special_col, newColumns
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
    x, y, col_data, col_wth_value, special_col, new = transfer(config) 
    data = json.dumps(x)
    col = json.dumps(new)
    ranks = json.dumps((db.get_all("analysis_rank")))
    return render_template('analysis/rank.html', ranks=Markup(ranks), data=Markup(data), col=Markup(col))
    
@app.route("/<config>/analysis/filter")
def filter_server(config):
    db = scouting.Module_Database.Database(config)
    x, y, col_data, col_wth_value, special_col, new = transfer(config)
    w = set(y + list(col_wth_value))
    data = json.dumps(x)
    col = json.dumps(list(w))
    newCol = json.dumps(new)
    return render_template('analysis/filter.html', data=Markup(data), col=Markup(col), newCol=Markup(newCol))
    
@app.route("/<config>/analysis/post", methods=['POST'])
def post_server(config):
    message = "Post"
    db = scouting.Module_Database.Database(config)
    result = json.loads(request.form['data'])
    for rank, teams in result.items():
        for team in teams:
            db.add(team, rank)
    db.commit()
    db.close()
    return render_template('analysis/post.html', message=message)
    
@app.route("/<config>/analysis/post_filter", methods=['POST'])
def post_filter_server(config):
    message = "Post"
    db = scouting.Module_Database.Database(config)
    result = json.loads(request.form['data'])
    data, columns_old, columns_data, col_wth_value, special_col, new  = transfer(config)
    d = {}
    raw_data = {}
    team_values = {}
    keyNames = []
    keyValues= []
    nameArr = []
    inputArr = []
    print(result)
    for name, value in result.items():
        nameArr.append(name)
        inputArr.append(value)
    print(nameArr, inputArr)
    for item in nameArr:
        try:
            newName, newValue = item.split("_")
            keyNames.append(newName)
            keyValues.append(newValue)
            for i in range(0, len(keyNames)):
                raw_data[keyNames[i]] = keyValues[i]
        except ValueError:
            continue
    teams_scores= {}
    for team, values in columns_data.items():
        unique_weight = 0
        scores = []
        properties = []
        score = 0
        weight = 0 
        for val_key in values.keys():
            for datapoint in nameArr:
                if val_key == datapoint:
                    weight = len(result) - nameArr.index(datapoint)
                    unique_weight = inputArr[nameArr.index(datapoint)]
                    leng = len(val_key)
                    if "_" in val_key and val_key[leng - 1].isdigit() == True and values[val_key] != None:
                        value = int(unique_weight)
                    else:
                        value = values[val_key]
                    properties.insert(0, value)
                    try :
                        #print(unique_weight * int(value) * weight)
                        score = int(unique_weight) * float(value) * weight 
                        #print(score)
                    except (TypeError, ValueError):
                        if value == None:
                            score = 0
                            pass
                        else:
                            score = int(unique_weight) * weight
                    scores.insert(0, score)
                    teams_scores[team] = sum(scores)
                else:
                    pass   
        d[team] = properties
        team_values[team] = properties
    print(teams_scores)
    print(team_values)
    ts = json.dumps(teams_scores)
    return ts
    db.commit()
    db.close()
    return render_template('analysis/post_filter.html', message=message)
  
