"""
This module is an intermediate layer between flopy version 3.2
and the inowas-modflow-configuration format.

Author: Ralf Junghanns
EMail: ralf.junghanns@gmail.com
"""

from .ReadBudget import ReadBudget
from .ReadConcentration import ReadConcentration
from .ReadDrawdown import ReadDrawdown
from .ReadHead import ReadHead
from .ReadFile import ReadFile


class InowasFlopyReadAdapter:
    """The Flopy Class"""

    _request = None
    _projectfolder = None
    _version = None

    def __init__(self, version, projectfolder, request):
        self._request = request
        self._projectfolder = projectfolder
        self._version = version
        pass

    def response(self):
        data = None
        request = self._request

        if 'budget' in request:
            budget_file = ReadBudget(self._projectfolder)
            if request['budget']['type'] == 'cumulative':
                if request['budget']['totim']:
                    totim = request['budget']['totim']
                    data = budget_file.read_budget_by_totim(totim=totim, incremental=False)
                if request['budget']['idx']:
                    idx = request['budget']['idx']
                    data = budget_file.read_budget_by_idx(idx=idx, incremental=False)
                if request['budget']['kstpkper']:
                    kstpkper = request['budget']['kstpkper']
                    data = budget_file.read_budget_by_kstpkper(kstpkper=kstpkper, incremental=False)

            if request['budget']['type'] == 'incremental':
                if request['budget']['totim']:
                    totim = request['budget']['totim']
                    data = budget_file.read_budget_by_totim(totim=totim, incremental=True)
                if request['budget']['idx']:
                    idx = request['budget']['idx']
                    data = budget_file.read_budget_by_idx(idx=idx, incremental=True)
                if request['budget']['kstpkper']:
                    kstpkper = request['budget']['kstpkper']
                    data = budget_file.read_budget_by_kstpkper(kstpkper=kstpkper, incremental=True)

        if 'layerdata' in request:
            if request['layerdata']['type'] == 'concentration':
                concentration_file = ReadConcentration(self._projectfolder)
                totim = request['layerdata']['totim']
                layer = request['layerdata']['layer']
                substance = request['layerdata']['substance']
                data = concentration_file.read_layer(totim=totim, layer=layer, substance=substance)

            if request['layerdata']['type'] == 'drawdown':
                drawdown_file = ReadDrawdown(self._projectfolder)
                totim = request['layerdata']['totim']
                layer = request['layerdata']['layer']
                data = drawdown_file.read_layer(totim=totim, layer=layer)

            if request['layerdata']['type'] == 'head':
                head_file = ReadHead(self._projectfolder)
                totim = request['layerdata']['totim']
                layer = request['layerdata']['layer']
                data = head_file.read_layer(totim=totim, layer=layer)

        if 'file' in request:
            extension = request['file']
            namfile = ReadFile(self._projectfolder)
            data = [namfile.read_file(extension)]

        if 'filelist' in request:
            namfile = ReadFile(self._projectfolder)
            return namfile.read_file_list()

        if 'timeseries' in request:
            if request['timeseries']['type'] == 'concentration':
                concentration_file = ReadConcentration(self._projectfolder)
                layer = request['timeseries']['layer']
                row = request['timeseries']['row']
                column = request['timeseries']['column']
                substance = request['timeseries']['substance']
                data = concentration_file.read_ts(layer=layer, row=row, column=column, substance=substance)

            if request['timeseries']['type'] == 'drawdown':
                drawdown_file = ReadDrawdown(self._projectfolder)
                layer = request['timeseries']['layer']
                row = request['timeseries']['row']
                column = request['timeseries']['column']
                data = drawdown_file.read_ts(layer=layer, row=row, column=column)

            if request['timeseries']['type'] == 'head':
                head_file = ReadHead(self._projectfolder)
                layer = request['timeseries']['layer']
                row = request['timeseries']['row']
                column = request['timeseries']['column']
                data = head_file.read_ts(layer=layer, row=row, column=column)

        if data is not None:
            return dict(
                status_code=200,
                request=request,
                response=data
            )

        return dict(
            status_code=500,
            message="Internal Server Error. Request data does not fit."
        )
