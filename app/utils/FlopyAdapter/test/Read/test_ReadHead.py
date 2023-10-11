import os
import unittest
from ...Read import ReadHead


class ReadHeadTest(unittest.TestCase):
    def test_it_reads_the_totims_test(self):
        dirname = os.path.dirname(__file__)
        rh = ReadHead(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rh, ReadHead)
        self.assertEqual(rh.read_times(),
                         [1.0, 4.0, 7.0, 10.0, 13.0,
                          16.0, 19.0, 22.0, 25.0, 28.0,
                          31.0, 59.0, 90.0, 93.0, 96.0,
                          99.0, 102.0, 105.0, 108.0,
                          111.0, 114.0, 117.0, 120.0, 151.0]
                         )

    def test_it_reads_the_idx_test(self):
        dirname = os.path.dirname(__file__)
        rh = ReadHead(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rh, ReadHead)
        self.assertEqual(rh.read_idx(),
                         [0, 1, 2, 3, 4,
                          5, 6, 7, 8, 9,
                          10, 11, 12, 13, 14,
                          15, 16, 17, 18, 19,
                          20, 21, 22, 23]
                         )

    def test_it_reads_the_kstpkper_test(self):
        dirname = os.path.dirname(__file__)
        rh = ReadHead(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rh, ReadHead)
        self.assertEqual(rh.read_kstpkper(),
                         [(0, 0), (0, 1), (1, 1), (2, 1), (3, 1), (4, 1), (5, 1), (6, 1), (7, 1), (8, 1), (9, 1),
                          (0, 2), (0, 3), (0, 4), (1, 4), (2, 4), (3, 4), (4, 4), (5, 4), (6, 4), (7, 4), (8, 4),
                          (9, 4), (0, 5)]
                         )

    def test_it_reads_the_number_of_layers_test(self):
        dirname = os.path.dirname(__file__)
        rh = ReadHead(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rh, ReadHead)
        self.assertEqual(rh.read_number_of_layers(), 1)

    def test_it_reads_the_layer_data_by_totim_idx_kstpkper_test(self):
        dirname = os.path.dirname(__file__)
        rh = ReadHead(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rh, ReadHead)

        data_totim_4 = rh.read_layer_by_totim(4.0)
        self.assertEqual(data_totim_4,
                         [[450.0, 450.14, 449.99, 449.67, 449.26, 448.78, 448.26, 447.67, 446.99, 446.14, 445.0],
                          [450.0, 450.14, 449.99, 449.67, 449.26, 448.78, 448.26, 447.67, 446.99, 446.14, 445.0],
                          [450.0, 450.14, 449.99, 449.67, 449.26, 448.78, 448.26, 447.67, 446.99, 446.14, 445.0],
                          [450.0, 450.14, 449.99, 449.67, 449.26, 448.78, 448.26, 447.67, 446.99, 446.14, 445.0],
                          [450.0, 450.14, 449.99, 449.67, 449.26, 448.78, 448.26, 447.67, 446.99, 446.14, 445.0],
                          [450.0, 450.14, 449.99, 449.67, 449.26, 448.78, 448.26, 447.67, 446.99, 446.14, 445.0]])

        for idx, totim in enumerate(rh.read_times()):
            data_totim = rh.read_layer_by_totim(totim)
            self.assertEqual(data_totim, rh.read_layer_by_idx(idx=idx))
            self.assertEqual(data_totim, rh.read_layer_by_kstpkper(rh.read_kstpkper()[idx]))

    def test_it_reads_the_timeseries_by_layer_row_column_test(self):
        dirname = os.path.dirname(__file__)
        rh = ReadHead(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rh, ReadHead)
        self.assertEqual(rh.read_ts(0, 0, 0),
                         [[1.0, 450.0], [4.0, 450.0], [7.0, 450.0], [10.0, 450.0], [13.0, 450.0], [16.0, 450.0],
                          [19.0, 450.0], [22.0, 450.0], [25.0, 450.0], [28.0, 450.0], [31.0, 450.0], [59.0, 450.0],
                          [90.0, 450.0], [93.0, 450.0], [96.0, 450.0], [99.0, 450.0], [102.0, 450.0], [105.0, 450.0],
                          [108.0, 450.0], [111.0, 450.0], [114.0, 450.0], [117.0, 450.0], [120.0, 450.0],
                          [151.0, 450.0]]
                         )


if __name__ == "__main__":
    unittest.main()
