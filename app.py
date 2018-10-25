from flask import Flask, request, render_template
import database

test = database.Database("database_test")
print(test.get_name())

app = Flask(__name__)


@app.route('/')
def input_form():
    return render_template('input_form.html')


@app.route('/', methods=['POST'])
def input_form_post():
    text = request.form['text']
    return "You submitted: " + text
