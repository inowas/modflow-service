import os
from datetime import datetime
import json
import logging
import sqlite3 as sql
import traceback
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


def log(text, logger):
    print(text)
    logger.debug(text)


def calculate(idx, calculation_id, logger):
    log(str(datetime.now()) + ': Calculating....' + calculation_id + "\r", logger)

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

    log('Summary:', logger)
    log('Author: %s' % author, logger)
    log('Project: %s' % project, logger)
    log('Model Id: %s' % model_id, logger)
    log('Calculation Id: %s' % calculation_id, logger)
    log('Type: %s' % m_type, logger)
    log('Version: %s' % version, logger)
    log("Running flopy calculation for model-id '{0}' with calculation-id '{1}'".format(model_id, calculation_id),
        logger)

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

    try:

        flopy = InowasFlopyCalculationAdapter(version, data, calculation_id)
        state = 200 if flopy.success else 400
        log('Flopy-state: ' + str(state))
        log('Flopy-Response: ' + str(flopy.response_message()))

        cur.execute('UPDATE calculations SET state = ?, message = ?, updated_at = ? WHERE id = ?',
                    (state, flopy.response_message(), datetime.now(), idx))
        conn.commit()

        if state == 400:
            pass
    except:
        log(traceback.format_exc(), logger)


def run():
    while True:
        row = get_next_new_calculation_job()

        if not row:
            sleep(1)
            continue

        idx = row['id']
        calculation_id = row['calculation_id']
        target_directory = os.path.join(MODFLOW_FOLDER, calculation_id)
        logger = logging.getLogger('Calculation_log_' + calculation_id)
        logger.setLevel(logging.DEBUG)
        fh = logging.FileHandler(os.path.join(target_directory, 'debug.log'))
        fh.setLevel(logging.DEBUG)
        logger.addHandler(fh)

        try:
            calculate(idx, calculation_id, logger)
        except:
            conn = db_connect()
            cur = conn.cursor()
            cur.execute('UPDATE calculations SET state = ?, message = ?, updated_at = ? WHERE id = ?',
                        (500, traceback.format_exc(), datetime.now(), idx))
            conn.commit()
            log('Flopy-state: ' + str(500), logger)
            log(traceback.print_exc(), logger)


if __name__ == '__main__':
    db_init()
    run()
