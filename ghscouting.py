from flask import Flask, request, redirect, render_template, send_from_directory
from flask_basicauth import BasicAuth
import werkzeug.wrappers
import yaml
import yaml.scanner
import collections
import pyudev
import psutil
import shutil
import os

import scouting.Database
import scouting.Field

# Constant variables
FIELD_TYPES = {
    "number": scouting.Field.FieldNumber,
    "radio": scouting.Field.FieldSelect,
    "checkbox": scouting.Field.FieldCheckbox,
    "textarea": scouting.Field.FieldTextarea,
}


def load_config(config):
    try:
        stream = open(config + ".yml")
    except FileNotFoundError as e:
        return e
    try:
        return yaml.load(stream)
    except yaml.scanner.ScannerError as e:
        return e


def create_form(form_config):
    scouting_form = []
    for item, values in form_config.items():
        field_type = FIELD_TYPES.get(values["type"]) or scouting.Field.FieldBase
        field = field_type(item, values)
        scouting_form.append(field)
    return scouting_form


def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))


def list_usbs():
    usbs = []
    context = pyudev.Context()
    removable = [
        device
        for device in context.list_devices(subsystem="block", DEVTYPE="disk")
        if device.attributes.asstring("removable") == "1"
    ]
    for device in removable:
        partitions = [
            device.device_node
            for device in context.list_devices(
                subsystem="block", DEVTYPE="partition", parent=device
            )
        ]
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


_mapping_tag = (
    yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
)  # TODO: Seems kinda hacky but idk
yaml.add_constructor(_mapping_tag, dict_constructor)


app = Flask(__name__)

main_config = load_config("config")
for key in main_config.keys():
    app.config[f"gh_{key}"] = main_config[key]

app.config["BASIC_AUTH_USERNAME"] = app.config["gh_admin_username"]
app.config["BASIC_AUTH_PASSWORD"] = app.config["gh_admin_password"]

basic_auth = BasicAuth(app)


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
def form(config):
    form_data = load_config(config)
    if isinstance(form_data, Exception):  # Check if load_config threw an exception
        response = werkzeug.wrappers.Response(
            "<title>Gearheads Scouting</title>\n"
            '<h2>The following error was encountered while processing form "{}":</h2>\n'
            "<p>{}</p>".format(config, form_data),
            200,
            mimetype="text/html",
        )
        return response
    app.config["form"] = create_form(
        form_data
    )  # Add requested form data to request-global flask config
    return render_template("main.html")


@app.route("/<config>", methods=["POST"])
def form_post(config):
    form_data = load_config(config)
    if isinstance(form_data, Exception):  # Check if load_config threw an exception
        response = werkzeug.wrappers.Response(
            "<title>Gearheads Scouting</title>\n"
            '<h2>The following error was encountered while processing form "{}":</h2>\n'
            "<p>{}</p>".format(config, form_data),
            200,
            mimetype="text/html",
        )
        return response

    form = create_form(form_data)

    db = scouting.Database.Database(config)
    db.create_columns(form_data)

    if not request.form["matchnum"] or not request.form["team"]:
        return "You must supply a match number and team number!"

    db.set_match(request.form["matchnum"])
    db.set_team(request.form["team"])

    for field in form:
        column, value = field.process(request.form)
        if value:
            db.add_queue(column, value)

    #    for key in app.config["form"].keys():
    #        if (
    #            key != "matchnum"
    #            and key != "team"
    #            and app.config["form"][key].get("metatype") != "display"
    #        ):
    #            if app.config["form"][key]["type"] == "counter":
    #                count = 0
    #                for selection in app.config["form"][key]["selections"]:
    #                    counting = app.config["form"][key]["counting"]
    #                    if request.form.get(
    #                        counting + "_" + selection[0] + "_" + selection[2]
    #                    ):  # TODO: make this better
    #                        count = count + 1
    #                db.add_queue(key, count)
    #            if (
    #                app.config["form"][key]["type"] == "grid"
    #                and app.config["form"][key].get("gridtype") == "checkbox"
    #            ):
    #                for selection in request.form.getlist(key):
    #                    column_name = "{}_{}".format(key, selection)
    #                    db.add_queue(column_name, True)
    #            elif request.form.get(key):
    #                db.add_queue(key, request.form[key])

    db.commit()
    db.close()

    response = werkzeug.wrappers.Response(
        "Successfully submitted!\n"
        '<form method="get" action="/">'
        '<button type="submit">Submit another entry</button>'
        "</form>",
        200,
        mimetype="text/html",
    )
    return response


@app.route("/advanced")
@basic_auth.required
def advanced():
    return render_template(
        "advanced.html", list_usbs=list_usbs, list_databases=list_databases
    )


@app.route("/advanced", methods=["POST"])
def advanced_post():
    if "export_config" in request.form:
        shutil.copyfile("config.yml", request.form["device"] + "/config.yml")
        return "Config successfully exported"
    elif "import_config" in request.form:
        shutil.copyfile(request.form["device"] + "/config.yml", "config.yml")
        return "Config successfully imported"
    elif "export_database_db" in request.form:
        shutil.copyfile(
            request.form["database"],
            request.form["device"] + "/" + request.form["database"],
        )
        return "Database successfully exported"
    elif "export_database_csv" in request.form:
        dbname = request.form["database"]
        csvname = dbname[:-3] + ".csv"
        db = scouting.Database.Database(os.path.splitext(dbname)[0])
        db.output_to_csv(csvname)
        db.close()
        return "Database successfully exported"
    elif "delete" in request.form:
        os.remove(request.form["database"])
        return "Database deleted"
    elif "restart" in request.form:
        os.system("/usr/bin/sudo systemctl restart ghscouting")
        return "Restart failed!"
    elif "shutdown" in request.form:
        os.system("/usr/bin/sudo shutdown now")
        return "Shutdown failed!"
    return "Unknown error. Debug info: {request.form}"
