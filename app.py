from flask import Flask, request, url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml

import database

app = Flask(__name__)


def load_config(config):
    stream = open(config)
    return yaml.load(stream)


def validate_config(config):
    try:
        config["matchnum"]
        config["team"]
    except KeyError:
        print("Config must contain fields for matchnum and team")
        exit(1)


yamlCfg = load_config("config.yml")
validate_config(yamlCfg)


env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml']),
)

input_template = env.get_template('input_form.html')


@app.route('/')
def input_form():
    stylesheet = url_for('static', filename='style.css')
    photo = url_for('static', filename='gearheads.png')
    return input_template.render(config=yamlCfg,stylesheet=stylesheet,photo=photo)


@app.route('/', methods=['POST'])
def input_form_post():
    db = database.Database("database_test")  # TODO: automatically generate db calls based on config file
    db.create_columns(yamlCfg)
    db.set_match(request.form['matchnum'])
    db.set_team(request.form['team'])
    for key in yamlCfg.keys():
        if key != "matchnum" and key != "team":
            db.add_queue(key, request.form[key])
    db.commit()
    db.close()
    return "probably added to the db but error codes are hard" # TODO: actually error handle please
