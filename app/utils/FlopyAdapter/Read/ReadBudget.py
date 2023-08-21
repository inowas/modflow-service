import os
from flopy.utils.mflistfile import MfListBudget, SwtListBudget


class ReadBudget:
    _filename = None

    def __init__(self, workspace):
        for file in os.listdir(workspace):
            if file.endswith(".list"):
                self._filename = os.path.join(workspace, file)
        pass

    def get_list_budget(self):
        try:
            if self._filename.endswith("swt.list"):
                list_budget = SwtListBudget(self._filename)
                return list_budget

            list_budget = MfListBudget(self._filename)
            return list_budget
        except:
            return None

    def read_times(self):
        try:
            list_budget = self.get_list_budget()
            times = list_budget.get_times()
            if times is not None:
                return times

            return []
        except:
            return []

    def read_idx(self):
        try:
            times = self.read_times()
            return list(range(len(times)))
        except:
            return []

    def read_kstpkper(self):
        try:
            list_budget = self.get_list_budget()
            kstpkper = list_budget.get_kstpkper()
            if kstpkper is not None:
                return kstpkper
            return []
        except:
            return []

    def read_budget_by_totim(self, totim=0, incremental=False):
        try:
            list_budget = self.get_list_budget()
            budget = list_budget.get_data(totim=totim, incremental=incremental)
            values = {}
            for x in budget:
                param = str(x[2].decode('UTF-8'))
                values[param] = float(str(x[1]))
            return values
        except:
            return []

    def read_budget_by_idx(self, idx=0, incremental=False):
        try:
            list_budget = self.get_list_budget()
            budget = list_budget.get_data(idx=idx, incremental=incremental)
            values = {}
            for x in budget:
                param = str(x[2].decode('UTF-8'))
                values[param] = float(str(x[1]))
            return values
        except:
            return []

    def read_budget_by_kstpkper(self, kstpkper=(0, 0), incremental=False):
        try:
            list_budget = self.get_list_budget()
            budget = list_budget.get_data(kstpkper=kstpkper, incremental=incremental)
            values = {}
            for x in budget:
                param = str(x[2].decode('UTF-8'))
                values[param] = float(str(x[1]))
            return values
        except:
            return []
