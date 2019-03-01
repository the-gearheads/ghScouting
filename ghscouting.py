from flask import Flask, request, url_for
from flask_basicauth import BasicAuth
from jinja2 import Environment, FileSystemLoader, select_autoescape
import yaml
import collections
import pyudev
import psutil
import shutil
import os

import database

app = Flask(__name__)

app.config['BASIC_AUTH_USERNAME'] = 'ghscouting'
app.config['BASIC_AUTH_PASSWORD'] = 'password'

basic_auth = BasicAuth(app)


def load_config(config):
    stream = open(config)
    return yaml.load(stream)


def validate_config(config):
    try:  # Use try instead of if so that it can output error message
        config['matchnum']
        config['team']
    except KeyError:
        print("ERROR: matchnum and team fields must be present in config")
        exit(1)


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG


def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))


def list_usb():
    usbs = []
    context = pyudev.Context()
    removable = [device for device in context.list_devices(subsystem='block', DEVTYPE='disk') if device.attributes.asstring('removable') == "1"]
    for device in removable:
        partitions = [device.device_node for device in context.list_devices(subsystem='block', DEVTYPE='partition', parent=device)]
        for p in psutil.disk_partitions():
            if p.device in partitions:
                usbs.append("{}".format(p.mountpoint))
    usbs.sort()
    return usbs


def list_databases():
    databases = []
    for file in os.listdir(os.getcwd()):
        if file.endswith(".db"):
            databases.append(file)
    databases.sort()
    return databases


yaml.add_constructor(_mapping_tag, dict_constructor)


env = Environment(
    loader=FileSystemLoader('templates'),
    autoescape=select_autoescape(['html', 'xml']),
)

input_template = env.get_template('input_form.html')
advanced_template = env.get_template('advanced.html')


@app.route('/')
def input_form():
    try:
        yamlCfg = load_config("config.yml")
        validate_config(yamlCfg)
    except yaml.scanner.ScannerError:
        return "Configuration syntax error"
    stylesheet = url_for('static', filename='style.css')
    photo = url_for('static', filename='gearheads.png')
    favicon = url_for('static', filename='favicon.ico')
    return input_template.render(config=yamlCfg, stylesheet=stylesheet, photo=photo, favicon=favicon)


@app.route('/', methods=['POST'])
def input_form_post():
    yamlCfg = load_config("config.yml")
    validate_config(yamlCfg)
    db = database.Database("database_test")

    if not db.verify_columns(yamlCfg):
        return "FATAL ERROR! No further data will be recorded until config fixed!"

    db.create_columns(yamlCfg)

    if not request.form['matchnum'] or not request.form['team']:
        return "You must supply a match number and team number!"

    db.set_match(request.form['matchnum'])
    db.set_team(request.form['team'])

    for key in yamlCfg.keys():
        if key != "matchnum" and key != "team" and yamlCfg[key].get("metatype") != "display":
            if yamlCfg[key]['type'] == 'counter':
                count = 0
                for selection in yamlCfg[key]['selections']:
                    counting = yamlCfg[key]["counting"]
                    if request.form.get(counting + "_" + selection[0] + "_" + selection[2]):  # TODO: make this better
                        count = count + 1
                db.add_queue(key, count)
            if key in request.form and request.form[key] != "":  # "" to not record empty strings
                db.add_queue(key, request.form[key])

    db.commit()
    db.close()
    return "Successfully submitted!<br><form method='get' action='/'><button type='submit'>Submit another entry</button></form>"  # TODO: refresh page with fancy message


@app.route('/advanced')
@basic_auth.required
def advanced():
    return advanced_template.render(list_usb=list_usb(), list_db=list_databases())


@app.route('/advanced', methods=['POST'])
def advanced_post():
    if "export_config" in request.form:
        shutil.copyfile("config.yml", request.form['device']+"/config.yml")
        return "Config successfully exported"
    elif "import_config" in request.form:
        shutil.copyfile(request.form['device'] + "/config.yml", "config.yml")
        return "Config successfully imported"
    elif "export_database_db" in request.form:
        shutil.copyfile(request.form['database'], request.form['device'] + "/" + request.form['database'])
        return "Database successfully exported"
    elif "export_database_csv" in request.form:
        dbname = request.form['database']
        csvname = dbname + ".csv"
        db = database.Database(os.path.splitext(dbname)[0])
        db.output_to_csv(db.get_filename())
        db.close()
        shutil.copyfile(csvname, request.form['device'] + "/" + csvname)
        os.remove(csvname)
        return "Database successfully exported"
    elif "delete" in request.form:
        os.remove(request.form['database'])
        return "Database deleted"
    elif "restart" in request.form:
        os.system('/usr/bin/sudo systemctl restart ghscouting')
        return "Restart failed!"
    elif "shutdown" in request.form:
        os.system('/usr/bin/sudo shutdown now')
        return "Shutdown failed!"
    return "this could be my fault but you probably inspect elemented the site and that's not very cool of you"
