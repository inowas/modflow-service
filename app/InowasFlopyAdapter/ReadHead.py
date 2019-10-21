import os
import flopy.utils.binaryfile as bf


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
            return heads.get_times()
        except:
            return []

    def read_number_of_layers(self):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            number_of_layers = heads.get_data().shape[0]
            return number_of_layers
        except:
            return 0

    def read_layer(self, totim, layer):
        heads = bf.HeadFile(filename=self._filename, precision='single')
        data = heads.get_data(totim=totim, mflay=layer).tolist()
        for i in range(len(data)):
            for j in range(len(data[i])):
                data[i][j] = round(data[i][j], 2)
                if data[i][j] < -999:
                    data[i][j] = None
        return data

    def read_ts(self, layer, row, column):
        try:
            heads = bf.HeadFile(filename=self._filename, precision='single')
            return heads.get_ts(idx=(layer, row, column)).tolist()
        except:
            return []