from flask import Flask, request, redirect, render_template, send_from_directory, flash
import functools
import werkzeug.wrappers
import traceback
import yaml
import yaml.scanner
import collections
import pyudev
import psutil
import shutil
import os

import scouting.Database
import scouting.Element

ELEMENT_TYPES = {
    "number": scouting.Element.ElementNumber,
    "radio": scouting.Element.ElementSelect,
    "checkbox": scouting.Element.ElementCheckbox,
    "textarea": scouting.Element.ElementTextarea,
    "button": scouting.Element.ElementButton,
    "submit": scouting.Element.ElementSubmit,
    "image": scouting.Element.ElementImage,
    "text": scouting.Element.ElementText,
    "dropdown": scouting.Element.ElementDropdown,
    "removeables_dropdown": scouting.Element.ElementRemoveablesDropdown,
    "databases_dropdown": scouting.Element.ElementDatabasesDropdown,
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
        if type(values) is dict:
            element_type = (
                ELEMENT_TYPES.get(values["type"]) or scouting.Element.ElementBase
            )
            element = element_type(item, values)
            scouting_form.append(element)
    return scouting_form


def get_page(form_data, config):
    types = {"form": parse_form, "menu": parse_menu}
    if form_data["page_type"] in types:
        return types[form_data["page_type"]](form_data, config)
    else:
        return return_error("form", f"Form type {form_data['page_type']} not found")


def parse_form(form_config, config):
    app.config["page"] = create_form(form_config)
    return render_template("main.html")


def parse_menu(form_config, config):
    if form_config.get("username") and form_config.get("password"):
        auth_response = check_auth(
            request, form_config["username"], form_config["password"]
        )
        if auth_response:
            return auth_response
    app.config["page"] = create_form(form_config)
    return render_template("main.html")


def get_page_post(form_data, config):
    types = {"form": form_post, "menu": menu_post}
    if form_data["page_type"] in types:
        return types[form_data["page_type"]](form_data, config)
    else:
        return return_error("form", f"Form type {form_data['page_type']} not found")


def form_post(form_data, config):
    form = create_form(form_data)

    db = scouting.Database.Database(config)
    db.create_columns(form)

    db.set_match(request.form["matchnum"])
    db.set_team(request.form["team"])

    for element in form:
        if not element.display:
            column, value = element.process(request.form)
            if value:
                db.add_queue(column, value)

    db.commit()
    db.close()

    flash(
        f'✓ Successfully submitted entry for team {request.form["team"]}, match {request.form["matchnum"]}'
    )
    return redirect(request.path)


def menu_post(form_data, config):
    form = create_form(form_data)
    # get all form elements which are buttons
    buttons = list(
        filter(lambda x: issubclass(type(x), scouting.Element.ElementButton), form)
    )
    # make a map of button names to button objects
    button_dict = dict(map(lambda x: (x.name, x), buttons))
    for element in request.form.items():
        if element[0] in button_dict.keys():
            # only used button is in form, so if it is in the button dict keys set pressed to the corresponding button obj
            pressed = button_dict[element[0]]

    if not pressed.args.get("action"):
        flash("No pressed action found!")
        return redirect(request.path)
    try:
        exitcode = pressed.process(request.form)
        flash(
            "Button action completed successfully."
            if exitcode == 0
            else "Button action failed with exit code " + exitcode
        )
    except Exception as e:
        flash("Button action failed with error " + type(e).__name__)
    return redirect(request.path)


def dict_constructor(loader, node):
    return collections.OrderedDict(loader.construct_pairs(node))


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
        "<title>Gearheads Scouting</title>\n"
        '<h2>The following error was encountered while processing "{}":</h2>\n'
        "<span style='white-space: pre-line'>{}</span>".format(name, page_data),
        200,
        mimetype="text/html",
    )


_mapping_tag = yaml.resolver.BaseResolver.DEFAULT_MAPPING_TAG
yaml.add_constructor(_mapping_tag, dict_constructor)


app = Flask(__name__)

main_config = load_config("config")
for key in main_config.keys():
    app.config[f"gh_{key}"] = main_config[key]

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
def page(config):
    page_data = load_config(config)

    if isinstance(page_data, Exception):  # Check if load_config threw an exception
        return return_error(config, page_data)

    try:
        return get_page(page_data, config)
    except Exception as e:
        return return_error(config, traceback.format_exc())


@app.route("/<config>", methods=["POST"])
def page_post(config):
    page_data = load_config(config)

    if isinstance(page_data, Exception):  # Check if load_config threw an exception
        return return_error(config, page_data)

    try:
        return get_page_post(page_data, config)
    except Exception as e:
        return return_error(config, traceback.format_exc())


# @app.route("/<config>", methods=["POST"])
# def page_post(config):
#     page_data = load_config(config)
#     if isinstance(page_data, Exception):  # Check if load_config threw an exception
#         return return_error(config, page_data)

#     try:
#         return get_page_post(config)
#     except Exception as e:
#         return return_error(config, traceback.format_exc())


@app.route("/<config>/csv")
def gen_csv(config):
    page_data = load_config(config)
    if page_data["page_type"] == "form":
        db = scouting.Database.Database(config)
        return db.gen_csv().getvalue()
    return return_error(config, "Cannot generate a csv for a non-form page")


# @app.route("/advanced")
def advanced(config):
    return render_template("main.html")


# @app.route("/advanced", methods=["POST"])
# def advanced_post():
#     if "export_config" in request.form:
#         shutil.copyfile("config.yml", request.form["device"] + "/config.yml")
#         return "Config successfully exported"
#     elif "import_config" in request.form:
#         shutil.copyfile(request.form["device"] + "/config.yml", "config.yml")
#         return "Config successfully imported"
#     elif "export_database_db" in request.form:
#         shutil.copyfile(
#             request.form["database"],
#             request.form["device"] + "/" + request.form["database"],
#         )
#         return "Database successfully exported"
#     elif "export_database_csv" in request.form:
#         dbname = request.form["database"]
#         csvname = dbname[:-3] + ".csv"
#         db = scouting.Database.Database(os.path.splitext(dbname)[0])
#         with open(csvname, "w+") as f:
#             f.write(db.gen_csv())
#         db.close()
#         return "Database successfully exported"
#     elif "delete" in request.form:
#         os.remove(request.form["database"])
#         return "Database deleted"
#     elif "restart" in request.form:
#         os.system("/usr/bin/sudo systemctl restart ghscouting")
#         return "Restart failed!"
#     elif "shutdown" in request.form:
#         os.system("/usr/bin/sudo shutdown now")
#         return "Shutdown failed!"
#     return "Unknown error. Debug info: {request.form}"
