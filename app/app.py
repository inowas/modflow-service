import os
from flask import Flask, request, redirect, render_template
from flask_cors import CORS, cross_origin
import urllib.request
import sqlite3 as sql
from datetime import datetime
import json
import jsonschema
import uuid

from InowasFlopyAdapter.ReadBudget import ReadBudget
from InowasFlopyAdapter.ReadConcentration import ReadConcentration
from InowasFlopyAdapter.ReadDrawdown import ReadDrawdown
from InowasFlopyAdapter.ReadHead import ReadHead

DB_LOCATION = '/db/modflow.db'
MODFLOW_FOLDER = '/modflow'
UPLOAD_FOLDER = './uploads'

app = Flask(__name__)
CORS(app)


def db_init():
    conn = db_connect()
    conn.execute(
        'CREATE TABLE IF NOT EXISTS calculations (id INTEGER PRIMARY KEY AUTOINCREMENT, calculation_id STRING, state INTEGER, message TEXT, created_at DATE, updated_at DATE)')


def db_connect():
    return sql.connect(DB_LOCATION)


def get_calculation_by_id(calculation_id):
    conn = db_connect()
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    cursor.execute('SELECT calculation_id, state, message FROM calculations WHERE calculation_id = ?',
                   (calculation_id,))
    return cursor.fetchone()


def get_calculation_details_json(calculation_id, data, path):
    calculation = get_calculation_by_id(calculation_id)
    heads = ReadHead(path)
    budget_times = ReadBudget(path).read_times()
    concentration_times = ReadConcentration(path).read_times()
    drawdown_times = ReadDrawdown(path).read_times()

    times = {
        'start_date_time': data['dis']['start_datetime'],
        'time_unit': data['dis']['itmuni'],
        'total_times': heads.read_times()
    }

    layer_values = []
    number_of_layers = data['dis']['nlay']

    lv = ['head']
    if len(budget_times) > 0:
        lv.append('budget')

    if len(concentration_times) > 0:
        lv.append('concentration')

    if len(drawdown_times) > 0:
        lv.append('drawdown')

    for i in range(0, number_of_layers):
        layer_values.append(lv)

    return json.dumps({
        'calculation_id': calculation_id,
        'state': calculation['state'],
        'message': calculation['message'],
        'times': str(times),
        'layer_values': layer_values
    })


def valid_json_file(file):
    with open(file) as filedata:
        try:
            json.loads(filedata.read())
        except ValueError:
            return False
        return True


def read_json(file):
    with open(file) as filedata:
        data = json.loads(filedata.read())
    return data


def is_valid(content):
    try:
        data = content.get('data')
        mf = data.get('mf')
        mt = data.get('mt')
    except AttributeError:
        return False

    try:
        mf_schema_data = urllib.request.urlopen("https://schema.inowas.com/modflow/packages/mfPackages.schema.json")
        mf_schema = json.loads(mf_schema_data.read())
        jsonschema.validate(instance=mf, schema=mf_schema)
    except jsonschema.exceptions.ValidationError:
        return False

    if mt:
        try:
            mt_schema_data = urllib.request.urlopen("https://schema.inowas.com/modflow/packages/mtPackages.schema.json")
            mt_schema = json.loads(mt_schema_data.read())
            jsonschema.validate(instance=mt, schema=mt_schema)
        except jsonschema.exceptions.ValidationError:
            return False

    return True


def insert_new_calculation(calculation_id):
    with db_connect() as con:
        cur = con.cursor()
        cur.execute("INSERT INTO calculations (calculation_id, state, created_at, updated_at) VALUES ( ?, ?, ?, ?)",
                    (calculation_id, 0, datetime.now(), datetime.now()))


@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':

        if 'multipart/form-data' in request.content_type:
            # check if the post request has the file part
            if 'file' not in request.files:
                return 'No file uploaded'
            uploaded_file = request.files['file']

            if uploaded_file.filename == '':
                return 'No selected file'

            temp_filename = str(uuid.uuid4()) + '.json'
            temp_file = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            uploaded_file.save(temp_file)

            content = read_json(temp_file)

            if not is_valid(content):
                os.remove(temp_file)
                return 'This JSON file does not match with the MODFLOW JSON Schema'

            calculation_id = content.get("calculation_id")
            target_directory = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
            modflow_file = os.path.join(target_directory, 'configuration.json')

            if os.path.exists(modflow_file):
                return 'Model with calculationId: ' + calculation_id + ' already exits.'

            os.makedirs(target_directory)
            with open(modflow_file, 'w') as outfile:
                json.dump(content, outfile)

            insert_new_calculation(calculation_id)

            return redirect('/' + calculation_id)

        if 'application/json' in request.content_type:
            content = request.json

            if not is_valid(content):
                return 'Content is not valid.'

            calculation_id = content.get('calculation_id')
            target_directory = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
            modflow_file = os.path.join(target_directory, 'configuration.json')

            if os.path.exists(modflow_file):
                return 'Model with calculationId: ' + calculation_id + ' already exits.'

            os.makedirs(target_directory)
            with open(modflow_file, 'w') as outfile:
                json.dump(content, outfile)

            insert_new_calculation(calculation_id)

            return json.dumps({
                'status': 200,
                'calculation_id': calculation_id,
                'link': '/' + calculation_id
            })

    if request.method == 'GET':
        return render_template('upload.html')


@app.route('/<calculation_id>')
@cross_origin()
def calculation_details(calculation_id):
    modflow_file = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id, 'configuration.json')
    if not os.path.exists(modflow_file):
        return 'The file does not exist'

    data = read_json(modflow_file).get("data").get("mf")
    path = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)

    if request.content_type == 'application/json':
        return get_calculation_details_json(calculation_id, data, path)

    return render_template('details.html', id=str(calculation_id), data=data, path=path)


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
