import os
import unittest
import json
import random
import traceback
import tracemalloc
from ...Calculation import InowasFlopyCalculationAdapter


class InowasModflowCalculationAdapterTest(unittest.TestCase):

    def test_1_can_be_executed(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'data/test_1.json')
        with open(filename) as fileHandle:
            content = json.loads(fileHandle.read())

        author = content.get("author")
        project = content.get("project")
        calculation_id = content.get("calculation_id")
        model_id = content.get("model_id")
        m_type = content.get("type")
        version = content.get("version")

        self.assertEqual(author, "test author")
        self.assertEqual(project, "test project")
        self.assertEqual(version, "3.2.10")
        self.assertEqual(calculation_id, "6ba018c844d9fe62cc6c3cf448a0d34f")
        self.assertEqual(model_id, "16e98871-50cb-47e8-82d3-12c23e2857c8")
        self.assertEqual(m_type, None)

        data = content.get("data")

        target_directory = \
            './FlopyAdapter/test/Calculation/calculation/' \
            + str(random.randint(1000, 9999)) \
            + '-' + str(random.randint(1000, 9999)) \
            + '-' + str(random.randint(1000, 9999))

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

        try:
            flopy = InowasFlopyCalculationAdapter(version, data, calculation_id)
        except Exception as e:  # work on python 3.x
            traceback.print_exc()
            raise e

    def test_2_can_be_executed(self):
        dirname = os.path.dirname(__file__)
        filename = os.path.join(dirname, 'data/test_2.json')
        with open(filename) as fileHandle:
            content = json.loads(fileHandle.read())

        author = content.get("author")
        project = content.get("project")
        calculation_id = content.get("calculation_id")
        model_id = content.get("model_id")
        m_type = content.get("type")
        version = content.get("version")

        self.assertEqual(author, "test author")
        self.assertEqual(project, "test project")
        self.assertEqual(version, "3.2.10")
        self.assertEqual(calculation_id, "11b10e037d9821afad7ccad9e7c9c633")
        self.assertEqual(model_id, "117f02db-b934-4878-87a4-36b9dd1c02cf")
        self.assertEqual(m_type, None)

        data = content.get("data")

        target_directory = \
            './FlopyAdapter/test/Calculation/calculation/' \
            + str(random.randint(1000, 9999)) \
            + '-' + str(random.randint(1000, 9999)) \
            + '-' + str(random.randint(1000, 9999))

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

        try:
            flopy = InowasFlopyCalculationAdapter(version, data, calculation_id)
        except Exception as e:  # work on python 3.x
            traceback.print_exc()
            raise e

