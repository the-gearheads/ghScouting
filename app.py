from flask import Flask, request, render_template
import database

app = Flask(__name__)


@app.route('/')
def input_form():
    return render_template('input_form.html')


@app.route('/', methods=['POST'])
def input_form_post():
    db = database.Database("database_test")
    db.set_team(request.form['team'])
    db.set_number(request.form['number'])
    db.set_boolean(request.form['boolean'])
    db.set_string(request.form['string'])
    db.close()
    return "probably added to the db but error codes are hard"
