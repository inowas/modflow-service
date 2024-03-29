import os
import flopy.utils.binaryfile as bf
import numpy as np


class ReadHead:
    _filename = None

    def __init__(self, workspace):
        for file in os.listdir(workspace):
            if file.endswith(".hds"):
                self._filename = os.path.join(workspace, file)
        pass

    def read_times(self):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            times = heads.get_times()
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
            heads = bf.HeadFile(filename=self._filename, precision='single')
            kstpkper = heads.get_kstpkper()
            if kstpkper is not None:
                return kstpkper
            return []
        except:
            return []

    def read_number_of_layers(self):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            number_of_layers = heads.get_data().shape[0]
            return number_of_layers
        except:
            return 0

    def read_layer(self, **kwargs):
        return self.read_layer_by_totim(**kwargs)

    def read_layer_by_totim(self, totim=0, layer=0):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            data = heads.get_data(totim=totim, mflay=layer).tolist()
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = round(data[i][j], 2)
                    if data[i][j] < -999:
                        data[i][j] = None
            return data
        except:
            return []

    def read_layer_by_idx(self, idx=0, layer=0):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            data = heads.get_data(idx=idx, mflay=layer).tolist()
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = round(data[i][j], 2)
                    if data[i][j] < -999:
                        data[i][j] = None
            return data
        except:
            return []

    def read_min_max_by_idx(self, idx=0):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            data = heads.get_data(idx=idx).tolist()
            min_value = np.max(data)
            max_value = np.max(data)

            for i in range(len(data)):
                for j in range(len(data[i])):
                    for k in range(len(data[i][j])):
                        if data[i][j][k] < -999:
                            data[i][j][k] = None
                        elif data[i][j][k] > max_value:
                            max_value = data[i][j][k]
                        elif data[i][j][k] < min_value:
                            min_value = data[i][j][k]

            return [min_value, max_value]
        except:
            return [0, 999]

    def read_layer_by_kstpkper(self, kstpkper=(0, 0), layer=0):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            data = heads.get_data(kstpkper=kstpkper, mflay=layer).tolist()
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = round(data[i][j], 2)
                    if data[i][j] < -999:
                        data[i][j] = None
            return data
        except:
            return []

    def read_ts(self, layer=0, row=0, column=0):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            data = heads.get_ts(idx=(layer, row, column)).tolist()
            for i in range(len(data)):
                data[i][0] = round(data[i][0], 0)
                if data[i][1] < -999:
                    data[i][1] = None
            return data
        except:
            return []
