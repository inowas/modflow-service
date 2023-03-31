import os
import unittest
from ...Read import ReadBudget


class ReadBudgetTest(unittest.TestCase):
    def test_it_reads_the_totims_test(self):
        dirname = os.path.dirname(__file__)
        rb = ReadBudget(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rb, ReadBudget)
        self.assertEqual(rb.read_times(), [1.0, 31.0, 59.0, 90.0, 120.0, 151.0])

    def test_it_reads_the_idx_test(self):
        dirname = os.path.dirname(__file__)
        rb = ReadBudget(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rb, ReadBudget)
        self.assertEqual(rb.read_idx(), [0, 1, 2, 3, 4, 5])

    def test_it_reads_the_kstpkper_test(self):
        dirname = os.path.dirname(__file__)
        rb = ReadBudget(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rb, ReadBudget)
        self.assertEqual(rb.read_kstpkper(), [(0, 0), (9, 1), (0, 2), (0, 3), (9, 4), (0, 5)])

    def test_it_reads_the_layer_data_by_totim_idx_kstpkper_test(self):
        dirname = os.path.dirname(__file__)
        rb = ReadBudget(os.path.join(dirname, 'data/test_read_head_example'))
        self.assertIsInstance(rb, ReadBudget)

        data_totim_4 = rb.read_budget_by_totim(31.0)
        self.assertEqual(
            data_totim_4, {
                'STORAGE_IN': 0.0, 'CONSTANT_HEAD_IN': 1814.4, 'RECHARGE_IN': 534600.0, 'TOTAL_IN': 536414.4,
                'STORAGE_OUT': -169607.81, 'CONSTANT_HEAD_OUT': -366806.0, 'RECHARGE_OUT': -0.0,
                'TOTAL_OUT': -536413.8, 'IN-OUT': 0.5625, 'PERCENT_DISCREPANCY': 0.0, 'tslen': 3.0
            }
        )

        for idx, totim in enumerate(rb.read_times()):
            data_totim = rb.read_budget_by_totim(totim)
            self.assertEqual(data_totim, rb.read_budget_by_idx(idx=idx))
            self.assertEqual(data_totim, rb.read_budget_by_kstpkper(rb.read_kstpkper()[idx]))

    def test_it_reads_the_totims_from_empty_budget_file_test(self):
        dirname = os.path.dirname(__file__)
        rb = ReadBudget(os.path.join(dirname, 'data/test_example_with_no_budget'))
        self.assertIsInstance(rb, ReadBudget)
        self.assertEqual(rb.read_times(), [])

    def test_it_reads_the_kstpkper_from_empty_budget_file_test(self):
        dirname = os.path.dirname(__file__)
        rb = ReadBudget(os.path.join(dirname, 'data/test_example_with_no_budget'))
        self.assertIsInstance(rb, ReadBudget)
        self.assertEqual(rb.read_kstpkper(), [])

    def test_it_reads_the_idx_from_empty_budget_file_test(self):
        dirname = os.path.dirname(__file__)
        rb = ReadBudget(os.path.join(dirname, 'data/test_example_with_no_budget'))
        self.assertIsInstance(rb, ReadBudget)
        self.assertEqual(rb.read_idx(), [])


if __name__ == "__main__":
    unittest.main()
