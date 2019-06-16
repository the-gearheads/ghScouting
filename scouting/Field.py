import jinja2


class FieldBase:
    def __init__(self, name: str, args: dict):
        self.name = name
        self.args = args

    def get_line(self):
        return '<input name="{}" type="{}"><br>'.format(self.name, self.args["type"])

    def render(self):
        render_body = ""
        if self.args.get("display"):
            render_body = render_body + '<label for="{}">{}</label><br>'.format(
                self.name, self.args.get("display")
            )
        render_body = render_body + self.get_line()
        return jinja2.Markup(render_body)

    def process(self, form):
        return self.name, form.get(self.name)


class FieldTextarea(FieldBase):
    def get_line(self):
        return '<textarea name="{}"></textarea><br>'.format(self.name)


class FieldNumber(FieldBase):
    def get_line(self):
        return '<input name="{}" type="number" min="{}" max="{}"><br>'.format(
            self.name, self.args.get("min"), self.args.get("max")
        )


class FieldSelect(FieldBase):
    def render(self):
        render_body = ""
        if self.args.get("display"):
            render_body = render_body + '<label for="{}">{}</label><br>'.format(
                self.name, self.args.get("display")
            )
        for option in self.args["options"]:
            render_body = (
                render_body
                + '<input name="{0}" value="{1}" type="{2}"> {1} '.format(
                    self.name, option, self.args["type"]
                )
            )
        render_body = render_body + "<br>"
        return jinja2.Markup(render_body)

    def process(self, form):
        return self.name, form.get(self.name)


class FieldCheckbox(FieldSelect):
    def process(self, form):
        return f"{self.name}_{form.get(self.name)}", True
