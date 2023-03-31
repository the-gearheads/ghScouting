from flask import render_template, request, flash, redirect
import werkzeug
import traceback
import scouting.Page
import scouting.Element


ELEMENT_TYPES = {
    "number": scouting.Element.ElementNumber,
    "radio": scouting.Element.ElementSelect,
    "checkbox": scouting.Element.ElementCheckbox,
    "textarea": scouting.Element.ElementTextarea,
    "button": scouting.Element.ElementButton,
    "submit": scouting.Element.ElementSubmit,
    "image": scouting.Element.ElementImage,
    "display_text": scouting.Element.ElementDisplayText,
    "dropdown": scouting.Element.ElementDropdown,
    "removeables_dropdown": scouting.Element.ElementRemoveablesDropdown,
    "databases_dropdown": scouting.Element.ElementDatabasesDropdown,
}


class Form:
    def __init__(self, config, dbFile):
        self.name = config.name
        self.dbFile = dbFile
        self.config = config
        self.form = self.__create_form__(self.config)

    def __create_form__(self, config: scouting.Page.Config):
        form = []
        for item, values in config.config.items():
            if type(values) is dict:
                element_type = (
                    ELEMENT_TYPES.get(values["type"]) or scouting.Element.ElementBase
                )
                element = element_type(item, values)
                form.append(element)
        return form

    def get_page(self, app):
        app.config["page"] = self.form
        return render_template("form.html")

    def process_post(self):
        print("Was I reached at the correct time?")
        db = scouting.Database.Database(self.dbFile)
        db.create_columns(self.form)
        db.set_match(request.form["matchnum"])
        db.set_team(request.form["team"])
        for element in self.form:
            if not element.display_field:
                column, value = element.process(request.form)
                if value:
                    db.add_queue(column, value)
        db.commit()
        db.gen_csv()
        db.close()

        flash(
            f'✓ Successfully submitted entry for team {request.form["team"]}, match {request.form["matchnum"]}'
        )
        return redirect(request.path)


class Menu(Form):
    def get_page(self, app):
        if self.config.config.get("username") and self.config.config.get("password"):
            auth_response = self.__check_auth__(
                self.config.config["username"], self.config.config["password"]
            )
        if auth_response:
            return auth_response
        app.config["page"] = self.form
        return render_template("form.html")

    def process_post(self):
        buttons = list(
            filter(
                lambda x: issubclass(type(x), scouting.Element.ElementButton), self.form
            )
        )
        # make a map of button names to button objects
        button_dict = dict(map(lambda x: (x.name, x), buttons))
        for element in request.form.items():
            if element[0] in button_dict.keys():
                # only the pressed button is in form, so if it is in the button dict keys set pressed to the corresponding button obj
                pressed = button_dict[element[0]]

        if not pressed.args.get("action") and "commands" not in pressed.args.get(
            "action"
        ):
            flash("No pressed action found!")
            return redirect(request.path)
        try:
            returned = pressed.process(request.form)
            if returned == 0:
                flash(f"{pressed.args['text']} action completed successfully.")
            else:
                flash(f"{pressed.args['text']} action failed with the following error")
                flash(returned.decode("utf-8"))
        except Exception as e:
            print(traceback.format_exc())
            flash("Button action failed with error " + type(e).__name__)
        return redirect(request.path)

    def __check_auth__(self, username, password):
        auth = request.authorization
        if auth and (auth.username == username and auth.password == password):
            return
        return werkzeug.wrappers.Response(
            "Login to page failed",
            401,
            {"WWW-Authenticate": 'Basic realm="Login Required"'},
        )
