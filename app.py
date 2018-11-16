from flask import Flask, request
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml

import database

app = Flask(__name__)


def load_config(config):
    stream = open(config)
    return yaml.load(stream)


yamlCfg = load_config("config.yml")  # TODO: Make file selection less dumb

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
    db.set_match(request.form['matchnum'])
    db.set_team(request.form['team'])
    db.set_number(request.form['number'])
    db.set_boolean(request.form['boolean'])
    db.set_string(request.form['string'])
    db.commit()
    db.close()
    return "probably added to the db but error codes are hard" # TODO: actually error handle please
