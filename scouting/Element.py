from flask import url_for
import jinja2
import subprocess
import pyudev
import psutil
import os


# uh i should probably put this somewhere else but whatever
def list_removeable():
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
    databases_ext = []
    # kinda hacky but whatever™
    for file in os.listdir(os.getcwd()):
        if file.endswith(".db"):
            databases_ext.append(file)
    databases = list(map(lambda x: os.path.splitext(x)[0], databases_ext))
    databases.sort()
    return databases


class ElementBase:
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args
        self.display = self.args.get("display") or False
        self.position = self.args.get("position") or None

    # allow to keep rest of class while only overloading one method minimum
    def line_base(self):
        return '<input class="uk-input" name="{}" type="{}">'.format(
            self.name, self.args["type"]
        )

    # allows easy global modifications
    def get_line(self):
        return (
            self.line_base()[:-1] + " required>"
            if self.args.get("required")
            else self.line_base()
        )

    def render(self):
        render_body = ""
        if self.args.get("display"):
            render_body = render_body + '<label for="{}">{}</label>'.format(
                self.name, self.args.get("display")
            )
        render_body = render_body + self.get_line()
        return jinja2.Markup(render_body)

    def process(self, form):
        return self.name, form.get(self.name)


class ElementTextarea(ElementBase):
    def line_base(self):
        return '<textarea class="uk-textarea" name="{}"></textarea>'.format(self.name)


class ElementNumber(ElementBase):
    def line_base(self):
        return '<input class="uk-input" name="{}" type="number" min="{}" max="{}">'.format(
            self.name, self.args.get("min"), self.args.get("max")
        )


class ElementSelect(ElementBase):
    def render(self):
        render_body = ""
        if self.args.get("display"):
            render_body = render_body + '<label for="{}">{}</label>'.format(
                self.name, self.args.get("display")
            )
        for option in self.args["options"]:
            render_body = (
                render_body
                + '<input class="uk-{2}" name="{0}" value="{1}" type="{2}"> {1} '.format(
                    self.name, option, self.args["type"]
                )
            )
        render_body = render_body + ""
        return jinja2.Markup(render_body)

    def process(self, form):
        return self.name, form.get(self.name)


class ElementCheckbox(ElementSelect):
    def process(self, form):
        value = form.get(self.name)
        if value:
            return f"{self.name}_{value}", True
        return self.name, None


class ElementButton(ElementBase):
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args
        self.display = self.args.get("display") or True
        self.position = self.args.get("position") or None

    def line_base(self):
        return '<button class="uk-button-default" name="{}" type="{}">{}</button>'.format(
            self.name, self.args["type"], self.args["text"]
        )

    def process(self, form):
        process = subprocess.run(self.args["action"].split(" "))
        return process.returncode


class ElementDropdown(ElementBase):
    def line_base(self):
        line = "<select name={}>".format(self.name)
        for option in self.args["options"]:
            line += "\n<option value='{0}'>{0}</option>".format(option)
        line += "\n</select>"
        return line

    def get_line(self):
        return (
            self.line_base()[:8] + "required "
            if self.args.get("required")
            else self.line_base()
        )


class ElementRemoveablesDropdown(ElementDropdown):
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args
        self.args["options"] = list_removeable()


class ElementDatabasesDropdown(ElementDropdown):
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args
        self.args["options"] = list_databases()


class ElementSubmit(ElementButton):
    def line_base(self):
        return '<button class="uk-button-primary" name="{}" type="submit" formmethod="{}">{}</button>'.format(
            self.name, self.args["method"], self.args["text"]
        )


class ElementImage(ElementBase):
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args
        self.display = self.args.get("display") or True
        self.position = self.args.get("position") or None

    def line_base(self):
        return (
            '<img src="'
            + url_for("static", filename=self.args["filename"])
            + '" alt="{}">'.format(self.name)
        )


class ElementText(ElementBase):
    def line_base(self):
        return f'<p>{self.args["text"]}</p>'
