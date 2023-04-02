import os
from datetime import datetime
import json
import logging
import sqlite3 as sql
import traceback
from time import sleep

from utils.FlopyAdapter.Calculation import InowasFlopyCalculationAdapter

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


def write_state(target_directory, state):
    file = os.path.join(target_directory, 'state.log')
    f = open(file, "w")
    f.write(str(state))
    f.close()


def model_check(target_directory, flopy):
    file = os.path.join(target_directory, 'check.log')
    f = open(file, "w")
    flopy.check_model(f)
    f.close()


def calculate(idx, calculation_id, logger):
    print('Calculating: ' + calculation_id)
    logger.debug('Calculating: ' + calculation_id)

    target_directory = os.path.join(MODFLOW_FOLDER, calculation_id)
    logger.debug('Target Directory: {0}'.format(target_directory))

    filename = os.path.join(target_directory, 'configuration.json')
    logger.debug('Filename: {0}'.format(filename))

    content = read_json(filename)
    author = content.get("author")
    project = content.get("project")
    calculation_id = content.get("calculation_id")
    model_id = content.get("model_id")
    m_type = content.get("type")
    version = content.get("version")
    data = content.get("data")

    logger.debug('Summary:')
    logger.debug('Author: %s' % author)
    logger.debug('Project: %s' % project)
    logger.debug('Model Id: %s' % model_id)
    logger.debug('Calculation Id: %s' % calculation_id)
    logger.debug('Type: %s' % m_type)
    logger.debug('Version: %s' % version)
    logger.debug(
        "Running flopy calculation for model-id '{0}' with calculation-id '{1}'".format(model_id, calculation_id))

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
    conn.set_trace_callback(logger.debug)
    cur = conn.cursor()
    write_state(target_directory, 100)
    cur.execute('UPDATE calculations SET state = ?, updated_at = ? WHERE id = ?', (100, datetime.now(), idx))
    conn.commit()

    try:
        flopy = InowasFlopyCalculationAdapter(version, data, calculation_id)
        state = 200 if flopy.success else 400
        logger.debug('Flopy-state: ' + str(state))
        logger.info(str(flopy.response_message()))

        cur.execute('UPDATE calculations SET state = ?, message = ?, updated_at = ? WHERE id = ?',
                    (state, flopy.short_response_message(), datetime.now(), idx))
        conn.commit()
        write_state(target_directory, state)
    except:
        write_state(target_directory, 500)
        logger.error(traceback.format_exc())
        pass
    finally:
        try:
            flopy = InowasFlopyCalculationAdapter(version, data, calculation_id)
            model_check(target_directory, flopy)
        except:
            pass


def set_logger(target_directory, calculation_id):
    logger = logging.getLogger('Calculation_log_' + calculation_id)
    logger.setLevel(logging.DEBUG)

    debug_log_file = os.path.join(target_directory, 'debug.log')
    fhd = logging.FileHandler(debug_log_file, 'a+')
    fhd.setLevel(logging.DEBUG)
    logger.addHandler(fhd)

    error_log_file = os.path.join(target_directory, 'error.log')
    fhe = logging.FileHandler(error_log_file, 'a+')
    fhe.setLevel(logging.ERROR)
    logger.addHandler(fhe)

    modflow_log_file = os.path.join(target_directory, 'modflow.log')
    fhi = logging.FileHandler(modflow_log_file, 'a+')
    fhi.setLevel(logging.INFO)
    logger.addHandler(fhi)
    return logger


def run():
    while True:
        row = get_next_new_calculation_job()

        if not row:
            sleep(1)
            continue

        idx = row['id']
        calculation_id = row['calculation_id']
        target_directory = os.path.join(MODFLOW_FOLDER, calculation_id)
        logger = set_logger(target_directory, calculation_id)

        try:
            calculate(idx, calculation_id, logger)
        except:
            conn = db_connect()
            conn.set_trace_callback(logger.debug)
            cur = conn.cursor()
            cur.execute('UPDATE calculations SET state = ?, message = ?, updated_at = ? WHERE id = ?',
                        (500, traceback.format_exc(), datetime.now(), idx))
            conn.commit()
            logger.debug('Flopy-state: ' + str(500))
            logger.debug(traceback.format_exc())
            logger.error(traceback.format_exc())
            write_state(target_directory, 500)
        finally:
            root = logging.getLogger()
            list(map(root.removeHandler, root.handlers))
            list(map(root.removeFilter, root.filters))


if __name__ == '__main__':
    db_init()
    run()
