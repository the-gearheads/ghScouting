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
    z = {}
    p = set()
    s = {}
    
    for team, values in d.items():
        b[team] = {}
        z[team] = {}
        columns = []
        for i in foo:
            #print(values[i.name])
            if issubclass(type(i), scouting.Element.ElementCheckbox):
                w = con[i.name]["options"]
               # print(w)
                try: 
                    s[i.args["display"]] = w
                except KeyError:
                    s[i.name] = w
                o = {}
                for y in w:
                    value = str(y)
                    #print(y)
                    #print(values[f"{i.name}_{y}"])
                    o[y] = values[f"{i.name}_{y}"]
                    #print(o[y])
                    try:
                        columns.append(i.args["display"])
                        p.add(i.args["display"]+"_"+value)
                    except KeyError:
                        columns.append(i.name)
                        p.add(i.name+"_"+value)
                    b[team][i.name] = i.processor(o)
                    try:
                        z[team][i.args["display"]+"_"+value] = i.processor(o)
                    except KeyError:
                        z[team][i.name+"_"+value] = i.processor(o)
                        
                        
                    
                    
                    
                continue
            if issubclass(type(i), scouting.Element.ElementSelect):
                w = con[i.name]["options"]
                #print(w)
                try: 
                    s[i.args["display"]] = w
                except KeyError:
                    s[i.name] = w
                for y in w:
                    value = str(y)
                    try:
                        columns.append(i.args["display"])
                        p.add(i.args["display"]+"_"+value)
                    except KeyError:
                        columns.append(i.name)
                        p.add(i.name+"_"+value)
                    b[team][i.name] = i.processor(values[i.name])
                    try:
                        z[team][i.args["display"]+"_"+value] = i.processor(values[i.name])
                    except KeyError:
                        z[team][i.name+"_"+value] = i.processor(values[i.name])
                        
                        
                    
                    
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
                #print(con[i.name]["options"])
                columns.append(i.args["display"])
            except KeyError:
                columns.append(i.name)
                pass
            b[team][i.name] = i.processor(values[i.name])
            try:
                z[team][i.args["display"]] = i.processor(values[i.name])
            except KeyError:
                z[team][i.name] = i.processor(values[i.name])

    return b, columns, z, p, s
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
    
@app.route("/<config>/analysis/filter")
def filter_server(config):
    db = scouting.Module_Database.Database(config)
    #transfer(config)
    x, y, z, p, s = transfer(config)
    w = set(y + list(p))
    data = json.dumps(x)
    col = json.dumps(list(w))
    print(list(w))
    return render_template('analysis/filter.html', data=Markup(data), col=Markup(col))
    
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
    
@app.route("/<config>/analysis/post_filter", methods=['POST'])
def post_filter_server(config):
    message = "Post"
    db = scouting.Module_Database.Database(config)
    result = json.loads(request.form['data'])
    #print(result)
    x, y, z, p, s  = transfer(config)
    #print(d)
    #print(z)
    d = {}
    b = {}
    team_values = {}
    f = []
    g= []
    #print(p)
    for item in result:
        try:
            newName, newValue = item.split("_")
            f.append(newName)
            g.append(newValue)
            for i in range(0, len(f)):
                b[f[i]] = g[i]
        except ValueError:
            continue
            #b[newName[i]] = newValue[i]
    #print(p)
    teams_scores= {}
    for team, values in z.items():
        scores = []
        properties = []
        score = 0
        weight = 0 
        j = 0
        for key, value in s.items():
            for name in values.keys():
                for i in result:
                    if i == name:
                        weight = len(result) - result.index(i)
                       # print(weight)
                    else:
                        pass
                    continue
                for x, y in b.items():
                    if name.split("_")[0] == x:
                        for val in values.values():
                            if y == val:
                                j = 1      
                
                
                
                            
        for key in values.keys():
            for datapoint in result:
                
                if datapoint == key:
                    value = values[key]
                    properties.insert(0, value)
                    try :
                        print(value)
                        score = float(value) * weight
                    except (TypeError, ValueError):
                        print(j)
                        score = j * weight
                    #weight.pop(0)
                    scores.insert(0, score)
                    teams_scores[team] = scores
                else:
                    #print("no")
                    pass
        d[team] = properties
        team_values[team] = properties
            
    #print(d)
    print(teams_scores)
    print(team_values)
    db.commit()
    db.close()
    return render_template('analysis/post_filter.html', message=message)
#@app.route("/<config>/analysis/test")
#def rank_test(config):

    
    
