import os
import unittest
from ...Read import InowasModflowReadAdapter


class InowasModflowReadAdapterTestCase(unittest.TestCase):
    def test_it_can_be_instantiated_test(self):
        instance = InowasModflowReadAdapter()
        self.assertIsInstance(instance, InowasModflowReadAdapter)

    def test_it_throws_exception_if_path_is_wrong_test(self):
        with self.assertRaises(FileNotFoundError) as context:
            InowasModflowReadAdapter.load('abc')
        self.assertEqual('Path not found: abc', str(context.exception))

    def test_it_throws_exception_if_path_does_not_contain_name_file_test(self):
        with self.assertRaises(FileNotFoundError) as context:
            dirname = os.path.dirname(__file__)
            InowasModflowReadAdapter.load(os.path.join(dirname, 'data/emptyFolder'))
        self.assertEqual('Modflow name file with ending .nam or .mfn not found', str(context.exception))

    def test_it_loads_the_model_correctly_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load(os.path.join(dirname, 'data/test_example_1'))
        self.assertIsInstance(instance, InowasModflowReadAdapter)

    def test_it_loads_the_model_correctly_with_crs_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load_with_crs(
            os.path.join(dirname, 'data/test_example_1'),
            279972.0566, 9099724.9436, 31985, -15.5
        )

        self.assertIsInstance(instance, InowasModflowReadAdapter)

        from flopy.discretization import StructuredGrid
        mg = instance.modelgrid
        self.assertIsInstance(mg, StructuredGrid)
        self.assertEqual(mg.epsg, '32725')
        self.assertEqual(round(mg.xoffset), 279972)
        self.assertEqual(round(mg.yoffset), 9099725)
        self.assertEqual(mg.angrot, -15.5)

    def test_it_converts_wgs84_to_utm_correctly_test(self):
        lat = 50.966319
        long = 13.923273
        easting, northing, zone_number, zone_letter = InowasModflowReadAdapter.wgs82ToUtm(long, lat)
        self.assertEqual(round(easting), 424393)
        self.assertEqual(round(northing), 5646631)
        self.assertEqual(zone_number, 33)
        self.assertEqual(zone_letter, 'U')

    def test_it_converts_utm_to_wgs84_correctly_test(self):
        easting, northing, zone_number, zone_letter = 424393, 5646631, 33, 'U'
        long, lat = InowasModflowReadAdapter.utmToWgs82XY(easting, northing, zone_number, zone_letter)
        self.assertEqual(round(long, 5), 13.92328)
        self.assertEqual(round(lat, 5), 50.96632)

    def test_it_returns_a_model_geometry_correctly_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load_with_crs(
            os.path.join(dirname, 'data/test_example_1'),
            279972.0566, 9099724.9436, 31985, -15.5
        )

        geometry = instance.model_geometry(4326, 0)
        self.assertEqual(geometry["type"], 'Polygon')
        # self.assertEqual(len(geometry["coordinates"][0]), 520)
        # self.assertEqual(geometry["coordinates"][0][0], [-34.874831, -8.073991])

    def test_it_returns_model_gid_size_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load(os.path.join(dirname, 'data/test_example_1'))
        self.assertIsInstance(instance, InowasModflowReadAdapter)
        grid_size = instance.model_grid_size()
        self.assertEqual(grid_size, {
            'n_x': 227,
            'n_y': 221,
        })

    def test_it_returns_model_stressperiods_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load(os.path.join(dirname, 'data/test_example_1'))
        self.assertIsInstance(instance, InowasModflowReadAdapter)
        stress_periods = instance.model_stress_periods()
        expected = {
            'start_date_time': '1970-01-01',
            'end_date_time': '1970-02-06',
            'time_unit': 4,
            'stressperiods': [
                {
                    'start_date_time': '1970-01-01',
                    'nstp': 1,
                    'tsmult': 1.0,
                    'steady': True,
                },
                {
                    'start_date_time': '1970-01-02',
                    'nstp': 5,
                    'tsmult': 1.0,
                    'steady': False,
                },
                {
                    'start_date_time': '1970-01-12',
                    'nstp': 10,
                    'tsmult': 1.5,
                    'steady': False,
                }
            ]
        }
        self.assertEqual(stress_periods, expected)

    def test_it_returns_model_length_unit_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load(os.path.join(dirname, 'data/test_example_1'))
        self.assertIsInstance(instance, InowasModflowReadAdapter)
        length_unit = instance.model_length_unit()
        self.assertEqual(length_unit, 2)

    def test_it_returns_model_time_unit_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load(os.path.join(dirname, 'data/test_example_1'))
        self.assertIsInstance(instance, InowasModflowReadAdapter)
        time_unit = instance.model_time_unit()
        self.assertEqual(time_unit, 4)

    def test_it_returns_wel_boundaries_of_example_1_test(self):
        dirname = os.path.dirname(__file__)

        instance = InowasModflowReadAdapter.load_with_crs(
            os.path.join(dirname, 'data/test_example_1'),
            279972.0566, 9099724.9436, 31985, -15.5
        )
        self.assertIsInstance(instance, InowasModflowReadAdapter)
        wel_boundaries = instance.wel_boundaries(target_epsg=4326)
        self.assertEqual(len(wel_boundaries), 93)
        print(wel_boundaries[0])
        self.assertEqual(wel_boundaries[0],
                         {
                             'type': 'wel',
                             'name': 'Well 1',
                             'geometry': {"coordinates": [-34.879083, -8.084035], "type": "Point"},
                             'layers': [0],
                             'sp_values': [-2039.0, -2039.0, -2039.0], 'cells': [[217, 31]]
                         }
                         )

    def test_it_returns_wel_boundaries_of_example_2_test(self):
        dirname = os.path.dirname(__file__)
        instance = InowasModflowReadAdapter.load_with_crs(os.path.join(dirname, 'data/test_example_2'), 0, 0, 4326, 0)
        self.assertIsInstance(instance, InowasModflowReadAdapter)
        wel_boundaries = instance.wel_boundaries(target_epsg=4326)
        self.assertEqual(len(wel_boundaries), 6)
        self.assertEqual(wel_boundaries, [
            {
                'type': 'wel',
                'name': 'Well 1',
                'geometry': {"coordinates": [0.013461, 0.040657], "type": "Point"},
                'layers': [0],
                'sp_values': [0, -5000.0, -5000.0],
                'cells': [[1, 1]]
            }, {
                'type': 'wel',
                'name': 'Well 2',
                'geometry': {"coordinates": [0.022435, 0.040658], "type": "Point"},
                'layers': [0],
                'sp_values': [0, -5000.0, -5000.0],
                'cells': [[2, 1]]
            },
            {
                'type': 'wel',
                'name': 'Well 3',
                'geometry': {"coordinates": [0.058334, 0.040659], "type": "Point"},
                'layers': [0],
                'sp_values': [0, -10000.0, -10000.0],
                'cells': [[6, 1]]
            },
            {
                'type': 'wel',
                'name': 'Well 4',
                'geometry': {"coordinates": [0.085259, 0.04066], "type": "Point"},
                'layers': [0],
                'sp_values': [0, -5000.0, -5000.0],
                'cells': [[9, 1]]
            },
            {
                'type': 'wel',
                'name': 'Well 5',
                'geometry': {"coordinates": [0.013461, 0.022587], "type": "Point"},
                'layers': [0],
                'sp_values': [0, -5000.0, -5000.0],
                'cells': [[1, 3]]
            },
            {
                'type': 'wel',
                'name': 'Well 6',
                'geometry': {"coordinates": [0.040385, 0.013553], "type": "Point"},
                'layers': [0],
                'sp_values': [0, -5000.0, -5000.0],
                'cells': [[4, 4]]
            }])


if __name__ == "__main__":
    unittest.main()
