from flask import Flask, request
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml, sys

import database

app = Flask(__name__)


def load_config(config):
    stream = open(config)
    return yaml.load(stream)


def validate_config(config):
    if list(config.keys())[0] != "matchnum" or list(config.keys())[1] != "team":
            print("In config.yml, the first field must be matchnum and the second field must be team.")
            sys.exit(1)


yamlCfg = load_config("config.yml")
validate_config(yamlCfg)


# TODO: Make file selection less dumb

validate_config(yamlCfg)

env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml'])
)

input_template = env.get_template('input_form.html')

@app.route('/')
def input_form():
    return input_template.render(config=yamlCfg)


@app.route('/', methods=['POST'])
def input_form_post():
    db = database.Database("database_test")  # TODO: automatically generate db calls based on config file
    db.create_columns(yamlCfg)
    db.set_match(request.form['matchnum'])
    db.set_team(request.form['team'])
    db.add_queue("number", request.form['number'])
    db.add_queue("boolean", request.form['boolean'])
    db.add_queue("string", request.form['string'])
    db.commit()
    db.close()
    return "probably added to the db but error codes are hard" # TODO: actually error handle please
