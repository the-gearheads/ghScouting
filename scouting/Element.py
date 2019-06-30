from flask import url_for
import jinja2


class ElementBase:
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args
        self.display = self.args.get("display") or False
        self.position = self.args.get("position") or None

    def get_line(self):
        return '<input class="uk-input" name="{}" type="{}">'.format(
            self.name, self.args["type"]
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
    def get_line(self):
        return '<textarea class="uk-textarea" name="{}"></textarea>'.format(self.name)


class ElementNumber(ElementBase):
    def get_line(self):
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

    def get_line(self):
        return '<button class="uk-button-default" name="{}" type="{}">{}</button>'.format(
            self.name, self.args["type"], self.args["text"]
        )


class ElementSubmit(ElementButton):
    def get_line(self):
        return '<button class="uk-button-primary" name="{}" type="submit" formmethod="{}">{}</button>'.format(
            self.name, self.args["method"], self.args["text"]
        )


class ElementImage(ElementBase):
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args
        self.display = self.args.get("display") or True
        self.position = self.args.get("position") or None

    def get_line(self):
        return (
            '<img src="'
            + url_for("static", filename=self.args["filename"])
            + '" alt="{}">'.format(self.name)
        )


class ElementText(ElementBase):
    def get_line(self):
        return f'<p>{self.args["text"]}</p>'
