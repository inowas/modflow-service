import os
from flask import Flask, request, redirect, render_template
from flask_cors import CORS, cross_origin
import urllib.request
from shutil import copyfile
import sqlite3 as sql
from datetime import datetime
import json
import jsonschema
import uuid

UPLOAD_FOLDER = './uploads'
MODFLOW_FOLDER = '/modflow'

app = Flask(__name__)
CORS(app)


def db_init():
    conn = db_connect()
    conn.execute(
        'CREATE TABLE IF NOT EXISTS calculations (id INTEGER PRIMARY KEY AUTOINCREMENT, calculation_id STRING, state INTEGER, message TEXT, created_at DATE, updated_at DATE)')


def db_connect():
    return sql.connect('/db/modflow.db')


def valid_json_file(file):
    with open(file) as filedata:
        try:
            data = json.loads(filedata.read())
        except ValueError:
            return False
        return True


def read_json(file):
    with open(file) as filedata:
        data = json.loads(filedata.read())
    return data


def schema_validation(file):
    content = read_json(file)
    data = content.get("data").get("mf")
    link = "https://schema.inowas.com/modflow/packages/packages.schema.json"
    schemadata = urllib.request.urlopen(link)
    schema = json.loads(schemadata.read())
    try:
        jsonschema.validate(instance=data, schema=schema)
    except jsonschema.exceptions.ValidationError:
        return False
    return True


def file_extension(filename):
    if '.' in filename:
        return '_' + filename.rsplit('.', 1)[1]


@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        # check if the post request has the file part
        if 'file' not in request.files:
            return redirect(request.url)
        uploaded_file = request.files['file']

        if uploaded_file.filename == '':
            return 'No selected file'

        temp_filename = str(uuid.uuid4()) + '.' + file_extension(uploaded_file.filename)
        temp_file = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
        uploaded_file.save(temp_file)

        if not valid_json_file(temp_file):
            os.remove(temp_file)
            return 'File is not a valid JSON-File'

        if not schema_validation(temp_file):
            os.remove(temp_file)
            return 'This JSON file does not match with the MODFLOW JSON Schema'

        content = read_json(temp_file)
        calculation_id = content.get("calculation_id")

        target_directory = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
        modflow_file = os.path.join(target_directory, 'configuration.json')

        if os.path.exists(modflow_file):
            os.remove(temp_file)
            return 'calculation_id (' + calculation_id + ')is already existing. Address: http://127.0.0.1:5000/' + calculation_id

        os.makedirs(target_directory)
        copyfile(temp_file, modflow_file)

        with db_connect() as con:
            cur = con.cursor()
            cur.execute("INSERT INTO calculations (calculation_id, state, created_at, updated_at) VALUES ( ?, ?, ?, ?)",
                        (calculation_id, 0, datetime.now(), datetime.now()))

        return json.dumps({
            'status': 200,
            'get_metadata': '/' + calculation_id
        })

    return render_template('upload.html')


@app.route('/<calculation_id>')
@cross_origin()
def configuration(calculation_id):
    modflow_file = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id, 'configuration.json')
    if not os.path.exists(modflow_file):
        return 'The file does not exist'
    data = read_json(modflow_file).get("data").get("mf")
    return json.dumps(data)


@app.route('/list')
def list():
    con = db_connect()
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute("select * from calculations")

    rows = cur.fetchall()
    return render_template("list.html", rows=rows)


if __name__ == '__main__':
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)

    app.secret_key = '2349978342978342907889709154089438989043049835890'
    app.config['SESSION_TYPE'] = 'filesystem'
    app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
    app.config['MODFLOW_FOLDER'] = MODFLOW_FOLDER
    app.debug = True

    db_init()

    app.run(debug=True, host='0.0.0.0')
