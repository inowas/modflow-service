import os
from datetime import datetime
import json
import sqlite3 as sql
import traceback
import shutil
from time import sleep

from FlopyAdapter.Calculation import InowasFlopyCalculationAdapter

DB_LOCATION = '/db/modflow.db'
MODFLOW_FOLDER = '/modflow'


def db_connect():
    return sql.connect(DB_LOCATION)


def db_init():
    conn = db_connect()
    conn.execute(
        'CREATE TABLE IF NOT EXISTS calculations (id INTEGER PRIMARY KEY AUTOINCREMENT, calculation_id TEXT, state INTEGER, message TEXT, created_at DATE, updated_at DATE)'
    )


def get_next_new_calculation_job():
    conn = db_connect()
    conn.row_factory = sql.Row
    cursor = conn.cursor()

    cursor.execute('SELECT id, calculation_id FROM calculations WHERE state = ? ORDER BY id LIMIT ?', (0, 1))
    return cursor.fetchone()


def read_json(file):
    with open(file) as filedata:
        data = json.loads(filedata.read())
    return data


def calculate(idx, calculation_id):
    print(str(datetime.now()) + ': Calculating....' + calculation_id + "\r")

    target_directory = os.path.join(MODFLOW_FOLDER, calculation_id)
    filename = os.path.join(target_directory, 'configuration.json')
    content = read_json(filename)

    author = content.get("author")
    project = content.get("project")
    calculation_id = content.get("calculation_id")
    model_id = content.get("model_id")
    m_type = content.get("type")
    version = content.get("version")
    data = content.get("data")

    print('Summary:')
    print('Author: %s' % author)
    print('Project: %s' % project)
    print('Model Id: %s' % model_id)
    print('Calculation Id: %s' % calculation_id)
    print('Type: %s' % m_type)
    print('Version: %s' % version)
    print("Running flopy calculation for model-id '{0}' with calculation-id '{1}'".format(model_id, calculation_id))

    if 'mf' in data:
        data['mf']['mf']['modelname'] = 'mf'
        data['mf']['mf']['model_ws'] = target_directory

    if 'mt' in data:
        data['mt']['mt']['modelname'] = 'mt'
        data['mt']['mt']['model_ws'] = target_directory

    if 'mp' in data:
        data['mp']['mp']['modelname'] = 'mp'
        data['mp']['mp']['model_ws'] = target_directory

    if 'swt' in data:
        data['swt']['swt']['modelname'] = 'swt'
        data['swt']['swt']['model_ws'] = target_directory

    conn = db_connect()
    cur = conn.cursor()
    cur.execute('UPDATE calculations SET state = ?, updated_at = ? WHERE id = ?', (100, datetime.now(), idx))
    conn.commit()

    flopy = InowasFlopyCalculationAdapter(version, data, calculation_id)
    state = 200 if flopy.success else 400

    cur.execute('UPDATE calculations SET state = ?, message = ?, updated_at = ? WHERE id = ?',
                (state, flopy.response_message(), datetime.now(), idx))
    conn.commit()

    if state == 400:
        shutil.rmtree(target_directory, ignore_errors=True)

def run():
    while True:
        row = get_next_new_calculation_job()

        if not row:
            sleep(1)
            continue

        idx = row['id']
        calculation_id = row['calculation_id']
        target_directory = os.path.join(MODFLOW_FOLDER, calculation_id)

        try:
            calculate(idx, calculation_id)
        except:
            conn = db_connect()
            cur = conn.cursor()
            cur.execute('UPDATE calculations SET state = ?, message = ?, updated_at = ? WHERE id = ?',
                        (500, traceback.format_exc(), datetime.now(), idx))
            conn.commit()
            shutil.rmtree(target_directory, ignore_errors=True)
            traceback.print_exc()

if __name__ == '__main__':
    db_init()
    run()
