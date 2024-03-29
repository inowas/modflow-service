from datetime import datetime
import numpy as np
import matplotlib.pyplot as plt

from utils.FlopyAdapter.Read import ReadBudget, ReadHead, ReadConcentration, ReadDrawdown
from flask import abort, Flask, request, redirect, render_template, Response, send_file, make_response, jsonify
from flask_cors import CORS, cross_origin
import pandas as pd
import os
from pathlib import Path

import prometheus_client
from prometheus_flask_exporter import PrometheusMetrics
import sqlite3 as sql
import urllib.request
import json
import jsonschema
import shutil
import uuid
import zipfile
import io
import glob

DB_LOCATION = '/db/modflow.db'
MODFLOW_FOLDER = '/modflow'
UPLOAD_FOLDER = './uploads'
SCHEMA_SERVER_URL = 'https://schema.inowas.com'

app = Flask(__name__)
CORS(app)
metrics = PrometheusMetrics(app)

g_0 = prometheus_client.Gauge('number_of_calculated_models_0', 'Calculations in queue')
g_100 = prometheus_client.Gauge('number_of_calculated_models_100', 'Calculations in progress')
g_200 = prometheus_client.Gauge('number_of_calculated_models_200', 'Calculations finished with success')
g_400 = prometheus_client.Gauge('number_of_calculated_models_400', 'Calculations finished with error')


def db_init():
    conn = db_connect()

    sql_command = """
        CREATE TABLE IF NOT EXISTS calculations (
            id INTEGER PRIMARY KEY AUTOINCREMENT, 
            calculation_id STRING, 
            state INTEGER, 
            message TEXT, 
            created_at DATE, 
            updated_at DATE
        )
    """
    conn.execute(sql_command)


def fs_init():
    if not os.path.exists(UPLOAD_FOLDER):
        os.makedirs(UPLOAD_FOLDER)


def db_connect():
    return sql.connect(DB_LOCATION)


# noinspection SqlResolve
def get_calculation_by_id(calculation_id):
    conn = db_connect()
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    cursor.execute(
        'SELECT calculation_id, state, message FROM calculations WHERE calculation_id = ? ORDER BY id DESC LIMIT 1',
        (calculation_id,)
    )
    return cursor.fetchone()


def get_number_of_calculations(state=200):
    conn = db_connect()
    cursor = conn.cursor()

    cursor.execute(
        'SELECT Count() FROM calculations WHERE state = ?', (state,)
    )

    return cursor.fetchone()[0]


def get_calculation_details_json(calculation_id, data, path):
    target_directory = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    calculation = get_calculation_by_id(calculation_id)
    try:
        message = calculation["message"]
    except TypeError:
        message = ""

    try:
        state = calculation['state']
    except TypeError:
        state = 404

    stateLogfile = os.path.join(path, 'state.log')
    if os.path.isfile(stateLogfile):
        if app.config['DEBUG']:
            print('Read state from file')
        state = int(Path(stateLogfile).read_text())

    if 200 != state:
        modflowLog = None
        if os.path.isfile(os.path.join(path, 'modflow.log')):
            modflowLog = Path(os.path.join(path, 'modflow.log')).read_text()
        details = {
            'calculation_id': calculation_id,
            'state': state,
            'message': modflowLog if modflowLog else message,
            'files': os.listdir(target_directory),
            'total_times': [],
            'head': {
                'idx': [],
                'total_times': [],
                'kstpkper': [],
                'layers': 0
            },
            'budget': {
                'idx': [],
                'total_times': [],
                'kstpkper': []
            },
            'concentration': {
                'idx': [],
                'total_times': [],
                'kstpkper': [],
                'layers': 0
            },
            'drawdown': {
                'idx': [],
                'total_times': [],
                'kstpkper': [],
                'layers': 0
            },
            'layer_values': []
        }
        response = make_response(json.dumps(details))
        response.headers['Content-Type'] = 'application/json'
        return response

    calculation_details_file = os.path.join(target_directory, 'calculation_details.json')
    if os.path.exists(calculation_details_file):
        return send_file(calculation_details_file, mimetype='application/json', etag=False)

    heads = ReadHead(path)
    budget = ReadBudget(path)
    concentration = ReadConcentration(path)
    drawdown = ReadDrawdown(path)

    total_times = [float(totim) for totim in heads.read_times()]
    times = {
        'start_date_time': data['dis']['start_datetime'],
        'time_unit': data['dis']['itmuni'],
        'total_times': total_times,
        'head': {
            'idx': [int(idx) for idx in heads.read_idx()],
            'total_times': [float(round(totim, 0)) for totim in heads.read_times()],
            'kstpkper': [[int(kstpker[0]), int(kstpker[1])] for kstpker in heads.read_kstpkper()],
            'layers': int(heads.read_number_of_layers())
        },
        'budget': {
            'idx': [int(idx) for idx in budget.read_idx()],
            'total_times': [float(round(totim, 0)) for totim in budget.read_times()],
            'kstpkper': [[int(kstpker[0]), int(kstpker[1])] for kstpker in budget.read_kstpkper()],
        },
        'concentration': {
            'idx': [int(idx) for idx in concentration.read_idx()],
            'total_times': [float(round(totim, 0)) for totim in concentration.read_times()],
            'kstpkper': [[int(kstpker[0]), int(kstpker[1])] for kstpker in concentration.read_kstpkper()],
            'layers': int(concentration.read_number_of_layers())
        },
        'drawdown': {
            'idx': [int(idx) for idx in drawdown.read_idx()],
            'total_times': [float(round(totim, 0)) for totim in drawdown.read_times()],
            'kstpkper': [[int(kstpker[0]), int(kstpker[1])] for kstpker in drawdown.read_kstpkper()],
            'layers': int(drawdown.read_number_of_layers())
        },
    }

    layer_values = []
    number_of_layers = data['dis']['nlay']

    lv = ['head']
    if len(budget.read_times()) > 0:
        lv.append('budget')

    if len(concentration.read_times()) > 0:
        lv.append('concentration')

    if len(drawdown.read_times()) > 0:
        lv.append('drawdown')

    for i in range(0, number_of_layers):
        layer_values.append(lv)

    details = {
        'calculation_id': calculation_id,
        'state': state,
        'message': message,
        'files': os.listdir(target_directory),
        'times': times,
        'layer_values': layer_values
    }

    if state == 200:
        json.dump(details, open(calculation_details_file, 'x'))

    return json.dumps(details)


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


def assert_is_valid(content):
    try:
        data = content.get('data')
        mf = data.get('mf')
        mt = data.get('mt')
    except AttributeError as e:
        raise e

    try:
        mf_schema_data = urllib.request.urlopen('{}/modflow/packages/mfPackages.json'.format(SCHEMA_SERVER_URL))
        mf_schema = json.loads(mf_schema_data.read())
        jsonschema.validate(instance=mf, schema=mf_schema)
    except jsonschema.exceptions.ValidationError as e:
        raise e

    if mt:
        try:
            mt_schema_data = urllib.request.urlopen('{}/modflow/packages/mtPackages.json'.format(SCHEMA_SERVER_URL))
            mt_schema = json.loads(mt_schema_data.read())
            jsonschema.validate(instance=mt, schema=mt_schema)
        except jsonschema.exceptions.ValidationError as e:
            raise e

    return True


# noinspection SqlResolve
def insert_new_calculation(calculation_id):
    with db_connect() as con:
        cur = con.cursor()
        cur.execute('SELECT * FROM calculations WHERE calculation_id = ? AND state < ?', (calculation_id, 200))

        result = cur.fetchall()
        if len(result) > 0:
            return

        cur.execute(
            'INSERT INTO calculations (calculation_id, state, created_at, updated_at) VALUES ( ?, ?, ?, ?)',
            (calculation_id, 0, datetime.now(), datetime.now())
        )


def is_binary(filename):
    """
    Return true if the given filename appears to be binary.
    File is considered to be binary if it contains a NULL byte.
    FIXME: This approach incorrectly reports UTF-16 as binary.
    """
    with open(filename, 'rb') as f:
        for block in f:
            if b'\0' in block:
                return True
    return False


@app.route('/', methods=['GET', 'POST'])
@cross_origin()
def upload_file():
    if request.method == 'POST':
        if 'multipart/form-data' in request.content_type:
            # check if the post request has the file part
            if 'file' not in request.files:
                abort(415, 'No file uploaded')

            uploaded_file = request.files['file']
            if uploaded_file.filename == '':
                abort(415, 'No selected file')

            temp_filename = str(uuid.uuid4()) + '.json'
            temp_file = os.path.join(app.config['UPLOAD_FOLDER'], temp_filename)
            uploaded_file.save(temp_file)

            content = read_json(temp_file)

            try:
                assert_is_valid(content)
            except (jsonschema.exceptions.ValidationError, AttributeError) as e:
                abort(make_response(
                    render_template('schema_validation_error.html', e=e),
                    422
                ))

            calculation_id = content.get("calculation_id")
            target_directory = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
            modflow_file = os.path.join(target_directory, 'configuration.json')

            if os.path.exists(target_directory):
                # abort(422, 'Model with calculationId: {} already exits.'.format(calculation_id))
                shutil.rmtree(target_directory)

            os.makedirs(target_directory)
            with open(modflow_file, 'w') as outfile:
                json.dump(content, outfile)

            insert_new_calculation(calculation_id)

            return redirect('/' + calculation_id)

        if 'application/json' in request.content_type:
            content = request.get_json(force=True)

            try:
                assert_is_valid(content)
            except (jsonschema.exceptions.ValidationError, AttributeError) as e:
                abort(make_response(jsonify(message=str(e)), 422))

            if app.config['DEBUG']:
                print('Content is valid')

            calculation_id = content.get('calculation_id')
            target_directory = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
            modflow_file = os.path.join(target_directory, 'configuration.json')

            if os.path.exists(modflow_file):
                if app.config['DEBUG']:
                    print('Path exists.')
                    shutil.rmtree(target_directory, ignore_errors=True)

            # if not os.path.exists(os.path.join(target_directory, 'state.log')):
            #     if app.config['DEBUG']:
            #         print('State-log not existing, remove folder.')
            #     shutil.rmtree(target_directory, ignore_errors=True)
            #     pass
            #
            #     if os.path.exists(os.path.join(target_directory, 'state.log')):
            #         if Path(os.path.join(target_directory, 'state.log')).read_text() != '200':
            #             if app.config['DEBUG']:
            #                 print('State-log existing, but not 200. Remove folder.')
            #             shutil.rmtree(target_directory, ignore_errors=True)

            if not os.path.exists(modflow_file):
                if app.config['DEBUG']:
                    print('Create folder.')
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


@app.route('/<calculation_id>', methods=['GET'])
@cross_origin()
def calculation_details(calculation_id):
    path = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(path, 'configuration.json')
    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    if not glob.glob(path + '/*.list'):
        insert_new_calculation(calculation_id)

    data = read_json(modflow_file).get('data').get('mf')
    path = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)

    if request.headers.get('Accept') == 'application/json':
        response = make_response(get_calculation_details_json(calculation_id, data, path))
        response.headers['Content-Type'] = 'application/json'
        return response

    if request.content_type and 'application/json' in request.content_type:
        response = make_response(get_calculation_details_json(calculation_id, data, path))
        response.headers['Content-Type'] = 'application/json'
        return response

    return render_template('details.html', id=str(calculation_id), data=data, path=path)


@app.route('/<calculation_id>/files/<file_name>', methods=['GET'])
@cross_origin()
def get_file(calculation_id, file_name):
    target_file = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id, file_name)

    if not os.path.exists(target_file):
        abort(404, {'message': 'File with name {} not found.'.format(file_name)})

    if is_binary(target_file):
        return json.dumps({
            'name': file_name,
            'content': 'This file is a binary file and cannot be shown as text'
        })

    with open(target_file) as f:
        file_content = f.read()
        return json.dumps({
            'name': file_name,
            'content': file_content
        })


@app.route('/<calculation_id>/results/types/<type>/layers/<layer>/totims/<totim>', methods=['GET'])
@cross_origin()
def get_results_head_drawdown_by_totim(calculation_id, type, layer, totim):
    permitted_types = ['head', 'drawdown']
    if type not in permitted_types:
        abort(404, 'Type: {} not available. Available types are: {}'.format(type, ", ".join(permitted_types)))

    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(target_folder, 'configuration.json')

    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    permitted_outputs = ['image', 'json']
    output = request.args.get('output', 'json')

    if output not in permitted_outputs:
        abort(404, 'Output: {} not available. Available outputs are: {}'.format(output, ", ".join(permitted_outputs)))

    totim = float(totim)
    layer = int(layer)

    if type == 'head':
        heads = ReadHead(target_folder)
        times = heads.read_times()

        if totim not in times:
            abort(404, 'Totim: {} not available. Available totims are: {}'.format(totim, ", ".join(map(str, times))))

        nlay = heads.read_number_of_layers()
        if layer >= nlay:
            abort(404, 'Layer must be less then the overall number of layers ({}).'.format(nlay))

        return json.dumps(heads.read_layer_by_totim(totim, layer))

    if type == 'drawdown':
        drawdown = ReadDrawdown(target_folder)
        times = drawdown.read_times()
        if totim not in times:
            abort(404, 'Totim: {} not available. Available totims are: {}'.format(totim, ", ".join(map(str, times))))

        nlay = drawdown.read_number_of_layers()
        if layer >= nlay:
            abort(404, 'Layer must be less then the overall number of layers ({}).'.format(nlay))

        return json.dumps(drawdown.read_layer_by_totim(totim, layer))


def create_png_image(data: [], vmin=None, vmax=None, cmap='jet_r'):
    bytes_image = io.BytesIO()

    data = np.array(data, dtype=np.float32)

    if vmin is None:
        vmin = np.nanmin(data) - np.nanstd(data)

    if vmax is None:
        vmax = np.nanmax(data) + np.nanstd(data)

    plt.imsave(bytes_image, data, format='png', cmap=cmap, vmin=vmin, vmax=vmax)
    bytes_image.seek(0)
    return bytes_image


def create_png_colorbar(data: [], vmin=None, vmax=None, cmap='jet_r'):
    bytes_image = io.BytesIO()

    data = np.array(data, dtype=np.float32)
    if vmin is None:
        vmin = np.nanmin(data) - np.nanstd(data)

    if vmax is None:
        vmax = np.nanmax(data) + np.nanstd(data)

    fig, (ax) = plt.subplots(nrows=1, ncols=1)
    fig.patch.set_facecolor('None')
    fig.patch.set_alpha(0.0)
    im = ax.imshow(data, cmap=cmap, vmin=vmin, vmax=vmax)
    plt.colorbar(im, ax=ax)
    ax.remove()
    plt.savefig(bytes_image, format='png', bbox_inches='tight')
    bytes_image.seek(0)
    return bytes_image


@app.route('/<calculation_id>/results/types/<type>/idx/<idx>', methods=['GET'])
@app.route('/<calculation_id>/results/types/<type>/layers/<layer>/idx/<idx>', methods=['GET'])
@cross_origin()
def get_results_head_drawdown_by_idx(calculation_id, type='head', layer=0, idx=0):
    permitted_types = ['head', 'drawdown']

    if type not in permitted_types:
        abort(404, 'Type: {} not available. Available types are: {}'.format(type, ", ".join(permitted_types)))

    permitted_outputs = ['image', 'json', 'colorbar']
    output = request.args.get('output', 'json')

    if output not in permitted_outputs:
        abort(404, 'Output: {} not available. Available outputs are: {}'.format(output, ", ".join(permitted_outputs)))

    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(target_folder, 'configuration.json')

    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    idx = int(idx)
    layer = int(layer)

    if type == 'head':
        heads = ReadHead(target_folder)
        times = heads.read_times()

        if idx >= len(times):
            abort(404,
                  'TotimKey: {} not available. Available keys are in between: {} and {}'.format(idx, 0, len(times) - 1))

        nlay = heads.read_number_of_layers()
        if layer >= nlay:
            abort(404, 'Layer must be less then the overall number of layers ({}).'.format(nlay))

        data = heads.read_layer_by_idx(idx, layer)
        [min, max] = heads.read_min_max_by_idx(idx)
        cmap = 'jet_r'

        if output == 'image':
            return send_file(create_png_image(data, cmap=cmap, vmin=min, vmax=max), mimetype='image/png',
                             etag=True,
                             max_age=3600)

        if output == 'colorbar':
            return send_file(create_png_colorbar(data, cmap=cmap, vmin=min, vmax=max), mimetype='image/png',
                             etag=True,
                             max_age=3600)

        return json.dumps(data)

    if type == 'drawdown':
        drawdown = ReadDrawdown(target_folder)
        times = drawdown.read_times()
        if idx >= len(times):
            abort(404,
                  'TotimKey: {} not available. Available keys are in between: {} and {}'.format(idx, 0, len(times) - 1))
        nlay = drawdown.read_number_of_layers()
        if layer >= nlay:
            abort(404, 'Layer must be less then the overall number of layers ({}).'.format(nlay))

        data = drawdown.read_layer_by_idx(idx, layer)
        [min, max] = drawdown.read_min_max_by_idx(idx)
        cmap = 'jet_r'

        if output == 'image':
            return send_file(create_png_image(data, cmap=cmap, vmin=min, vmax=max), mimetype='image/png',
                             etag=True,
                             max_age=3600)

        if output == 'colorbar':
            return send_file(create_png_colorbar(data, cmap=cmap, vmin=min, vmax=max), mimetype='image/png',
                             etag=True,
                             max_age=3600)

        return json.dumps(data)


@app.route('/<calculation_id>/timeseries/types/<type>/layers/<layer>/rows/<row>/columns/<column>', methods=['GET'])
@cross_origin()
def get_results_time_series(calculation_id, type, layer, row, column):
    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(target_folder, 'configuration.json')

    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    permitted_types = ['head', 'drawdown']

    layer = int(layer)
    row = int(row)
    col = int(column)

    if type not in permitted_types:
        abort(404,
              'Type: {} not in the list of permitted types. \
              Permitted types are: {}.'.format(type, ", ".join(permitted_types))
              )

    if type == 'head':
        heads = ReadHead(target_folder)
        return json.dumps(heads.read_ts(layer, row, col))

    if type == 'drawdown':
        drawdown = ReadDrawdown(target_folder)
        return json.dumps(drawdown.read_ts(layer, row, col))


@app.route('/<calculation_id>/results/types/budget/totims/<totim>', methods=['GET'])
@cross_origin()
def get_results_budget_by_totim(calculation_id, totim):
    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(target_folder, 'configuration.json')

    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    totim = float(totim)

    budget = ReadBudget(target_folder)
    times = budget.read_times()
    if totim not in times:
        abort(404, 'Totim: {} not available. Available totims are: {}'.format(totim, ", ".join(map(str, times))))

    return json.dumps({
        'cumulative': budget.read_budget_by_totim(totim, incremental=False),
        'incremental': budget.read_budget_by_totim(totim, incremental=True)
    })


@app.route('/<calculation_id>/results/types/budget/idx/<idx>', methods=['GET'])
@cross_origin()
def get_results_budget_by_idx(calculation_id, idx):
    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(target_folder, 'configuration.json')

    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    idx = int(idx)

    budget = ReadBudget(target_folder)
    times = budget.read_times()
    if idx >= len(times):
        abort(404,
              'TotimKey: {} not available. Available keys are in between: {} and {}'.format(idx, 0, len(times) - 1))

    return json.dumps({
        'cumulative': budget.read_budget_by_idx(idx=idx, incremental=False),
        'incremental': budget.read_budget_by_idx(idx=idx, incremental=True)
    })


@app.route(
    '/<calculation_id>/results/types/concentration/substance/<substance>/layers/<layer>/totims/<totim>',
    methods=['GET'])
@cross_origin()
def get_layer_results_concentration_by_totim(calculation_id, substance, layer, totim):
    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(target_folder, 'configuration.json')

    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    layer = int(layer)
    substance = int(substance)
    totim = float(totim)

    concentrations = ReadConcentration(target_folder)

    nsub = concentrations.read_number_of_substances()
    if substance >= nsub:
        abort(404, 'Substance: {} not available. Number of substances: {}.'.format(substance, nsub))

    times = concentrations.read_times()
    if totim not in times:
        abort(404, 'Totim: {} not available. Available totims are: {}'.format(totim, ", ".join(map(str, times))))

    nlay = concentrations.read_number_of_layers()
    if layer >= nlay:
        abort(404, 'Layer must be less then the overall number of layers ({}).'.format(nlay))

    return json.dumps(concentrations.read_layer(substance=substance, totim=totim, layer=layer))


@app.route(
    '/<calculation_id>/results/types/concentration/substance/<substance>/layers/<layer>/idx/<idx>',
    methods=['GET'])
@cross_origin()
def get_layer_results_concentration_by_idx(calculation_id, substance, layer, idx):
    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    modflow_file = os.path.join(target_folder, 'configuration.json')

    if not os.path.exists(modflow_file):
        abort(404, 'Calculation with id: {} not found.'.format(calculation_id))

    concentrations = ReadConcentration(target_folder)
    layer = int(layer)
    substance = int(substance)
    idx = int(idx)

    nsub = concentrations.read_number_of_substances()
    if substance >= nsub:
        abort(404, 'Substance: {} not available. Number of substances: {}.'.format(substance, nsub))

    times = concentrations.read_times()

    if idx >= len(times):
        abort(404, 'idxKey: {} not available. Available keys are in between: {} and {}'.format(idx, 0, len(times) - 1))

    nlay = concentrations.read_number_of_layers()
    if layer >= nlay:
        abort(404, 'Layer must be less then the overall number of layers ({}).'.format(nlay))

    return json.dumps(concentrations.read_layer_by_idx(substance=substance, idx=idx, layer=layer))


@app.route('/<calculation_id>/results/types/observations', methods=['GET'])
@cross_origin()
def get_results_observations(calculation_id):
    target_folder = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    hob_out_file = os.path.join(target_folder, 'mf.hob.out')

    if not os.path.exists(hob_out_file):
        abort(404, 'Head observations from calculation with id: {} not found.'.format(calculation_id))

    try:
        df = pd.read_csv(hob_out_file, delim_whitespace=True, header=0, names=['simulated', 'observed', 'name'])
        json_data = df.to_json(orient='records')
        return json_data
    except:
        abort(500, 'Error converting head observation output file.')


@app.route('/<calculation_id>/download', methods=['GET'])
@cross_origin()
def get_download_model(calculation_id):
    os.chdir(os.path.join(app.config['MODFLOW_FOLDER'], calculation_id))
    data = io.BytesIO()
    with zipfile.ZipFile(data, mode='w') as z:
        for root, dirs, files in os.walk("."):
            for filename in files:
                z.write(filename)

    data.seek(0)
    return send_file(
        data,
        mimetype='application/zip',
        as_attachment=True,
        download_name='model-calculation-{}.zip'.format(calculation_id)
    )


@app.route('/cleanup/<calculation_id>', methods=['GET'])
@cross_origin()
def cleanup_calculation(calculation_id):
    path = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    os.chdir(path)

    deleted_list = []
    for file in glob.glob("mf.*"):
        deleted_list.append(file)
        os.remove(file)

    for file in glob.glob("mt.*"):
        deleted_list.append(file)
        os.remove(file)

    for file in glob.glob("mt*.*"):
        deleted_list.append(file)
        os.remove(file)

    for file in glob.glob("MT*.*"):
        deleted_list.append(file)
        os.remove(file)

    for file in glob.glob("state.log"):
        deleted_list.append(file)
        os.remove(file)

    return json.dumps(deleted_list)


def get_package_data(calculation_id: str, package: str, prop: str = None, idx: int = None):
    target_directory = os.path.join(app.config['MODFLOW_FOLDER'], calculation_id)
    filename = os.path.join(target_directory, 'configuration.json')

    if not os.path.exists(filename):
        raise FileNotFoundError(f'Calculation with id: {calculation_id} not found.')

    content = read_json(filename)
    data: dict = content.get('data').get('mf') or content.get('data').get('mt') or content.get('data').get('swt')

    if not data:
        raise FileNotFoundError(f'Calculation data with id: {calculation_id} not found.')

    if not prop:
        return data.get(package)

    if data.get(package) and data.get(package).get(prop):
        prop_data = data.get(package).get(prop)
        if isinstance(prop_data, __builtins__.list):
            if idx is None:
                return prop_data
            if prop_data[int(idx)]:
                return prop_data[int(idx)]
        return prop_data

    raise FileNotFoundError(f'Data with package: {package} and prop: {prop} not found.')


@app.route('/<calculation_id>/packages/<package>', methods=['GET'])
@app.route('/<calculation_id>/packages/<package>/props/<prop>', methods=['GET'])
@cross_origin()
def get_packages_json(calculation_id: str, package: str, prop: str = None):
    data = get_package_data(calculation_id, package, prop)
    return json.dumps(data)


@app.route('/<calculation_id>/elevations/<type>', methods=['GET'])
@app.route('/<calculation_id>/elevations/<type>/layers/<layer_idx>', methods=['GET'])
@cross_origin()
def get_elevation_image(calculation_id: str, type: str, layer_idx: str = 0):
    permitted_types = ['top', 'botm']
    permitted_outputs = ['json', 'image']
    output = request.args.get('output', 'json')

    if type not in permitted_types:
        abort(404, f'Type: {type} not available. Available types are: {", ".join(map(str, permitted_types))}')

    if output not in permitted_outputs:
        abort(404, f'Output: {output} not available. Available outputs are: {", ".join(map(str, permitted_outputs))}')

    cmap = request.args.get('cmap', 'gist_earth')
    layer_idx = int(layer_idx)
    vmin = request.args.get('vmin', None)
    vmax = request.args.get('vmax', None)

    try:
        data = get_package_data(calculation_id, 'dis', 'top')
        if type == 'botm':
            data = get_package_data(calculation_id, 'dis', 'botm')

            if not data or not data[layer_idx]:
                abort(404, f'Layer: {layer_idx} not available. Available layers are: {", ".join(map(str, data))}')
            data = data[layer_idx]

        height = get_package_data(calculation_id, 'dis', 'nrow')
        width = get_package_data(calculation_id, 'dis', 'ncol')

        vmin = float(vmin) if vmin else np.nanmin(data)
        vmax = float(vmax) if vmax else np.nanmax(data)

        if vmin == vmax:
            vmin = vmin - 1
            vmax = vmax + 1

        if isinstance(data, __builtins__.float) or isinstance(data, __builtins__.int):
            data = (np.ones((int(height), int(width))) * data).tolist()

        if output == 'image':
            return send_file(
                create_png_image(data, vmin=vmin, vmax=vmax, cmap=cmap),
                mimetype='image/png',
                etag=True,
                max_age=3600
            )

        return json.dumps(data)
    except Exception as e:
        abort(500, e)


# noinspection SqlResolve
@app.route('/list')
def list():
    con = db_connect()
    con.row_factory = sql.Row

    cur = con.cursor()
    cur.execute('select * from calculations')

    rows = cur.fetchall()
    return render_template("list.html", rows=rows)


@app.route('/metrics')
def metrics():
    g_0.set(get_number_of_calculations(0))
    g_100.set(get_number_of_calculations(100))
    g_200.set(get_number_of_calculations(200))
    g_400.set(get_number_of_calculations(400))
    CONTENT_TYPE_LATEST = str('text/plain; version=0.0.4; charset=utf-8')
    return Response(prometheus_client.generate_latest(), mimetype=CONTENT_TYPE_LATEST)


@app.after_request
def after_request(response):
    if response.headers['Content-Type'] == 'application/json':
        response.headers["Cache-Control"] = "no-cache, no-store, must-revalidate"
        response.headers["Pragma"] = "no-cache"
        response.headers["Expires"] = "0"

    return response


app.secret_key = '2349978342978342907889709154089438989043049835890'
app.config['SESSION_TYPE'] = 'filesystem'
app.config['UPLOAD_FOLDER'] = UPLOAD_FOLDER
app.config['MODFLOW_FOLDER'] = MODFLOW_FOLDER
app.config['SEND_FILE_MAX_AGE_DEFAULT'] = 0
app.config['DEBUG'] = False

db_init()
fs_init()

if __name__ == '__main__':
    app.config['DEBUG'] = True
    app.run(debug=app.config['DEBUG'], host='0.0.0.0')
