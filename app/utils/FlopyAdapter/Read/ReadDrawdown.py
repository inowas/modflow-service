import os
import flopy.utils.binaryfile as bf


class ReadDrawdown:
    _filename = None

    def __init__(self, workspace):
        for file in os.listdir(workspace):
            if file.endswith(".ddn"):
                self._filename = os.path.join(workspace, file)
        pass

    def read_times(self):
        try:
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
            times = heads.get_times()
            if times is not None:
                return times
            return []
        except:
            return []

    def read_idx(self):
        try:
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
            times = heads.get_times()
            return list(range(len(times)))
        except:
            return []

    def read_kstpkper(self):
        try:
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
            kstpkper = heads.get_kstpkper()
            if kstpkper is not None:
                return kstpkper
            return []
        except:
            return []

    def read_number_of_layers(self):
        try:
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
            number_of_layers = heads.get_data().shape[0]
            return number_of_layers
        except:
            return 0

    def read_layer(self, **kwargs):
        return self.read_layer_by_totim(**kwargs)

    def read_layer_by_totim(self, totim=0, layer=0):
        try:
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
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
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
            data = heads.get_data(idx=idx, mflay=layer).tolist()
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = round(data[i][j], 2)
                    if data[i][j] < -999:
                        data[i][j] = None
            return data
        except:
            return []

    def read_layer_by_kstpkper(self, kstpkper=(0, 0), layer=0):
        try:
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
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
            heads = bf.HeadFile(filename=self._filename, text='drawdown', precision='single')
            return heads.get_ts(idx=(layer, row, column)).tolist()
        except:
            return []
