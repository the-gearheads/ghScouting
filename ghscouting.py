from flask import Flask, request, url_for
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
import collections
import sys

import database

app = Flask(__name__)

if __name__ == "__name__":
    app.run(host='0.0.0.0')

def load_config(config):
    stream = open(config)
    return yaml.load(stream)


def validate_config(config):
    try:  # Use try instead of if so that it can output error message
        config['matchnum']
        config['team']
    except KeyError:
        print("ERROR: matchnum and team fields must be present in config")
        sys.exit(1)


yamlCfg = collections.OrderedDict(load_config("config.yml"))
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
    favicon = url_for('static', filename='favicon.ico')
    return input_template.render(config=yamlCfg,stylesheet=stylesheet,photo=photo,favicon=favicon)


@app.route('/', methods=['POST'])
def input_form_post():
    db = database.Database("database_test")
    db.verify_columns(yamlCfg)
    db.create_columns(yamlCfg)

    if not request.form['matchnum'] or not request.form['team']:
        return "You must supply a match number and team number!"

    db.set_match(request.form['matchnum'])
    db.set_team(request.form['team'])

    for key in yamlCfg.keys():
        if key != "matchnum" and key != "team":
            if request.form[key]:
                db.add_queue(key, request.form[key])

    db.commit()
    db.close()
    return "Submitted!"  # TODO: refresh page with fancy message
