import errno
import os
import flopy.utils.binaryfile as bf


class ReadConcentration:
    _workspace = None

    def __init__(self, workspace):
        self._workspace = workspace

        for file in os.listdir(workspace):
            if file.upper() == "MT3D001.UCN":
                self._filename = os.path.join(workspace, file)
        pass

    def get_concentration_file_from_substance(self, substance=0):
        filename = os.path.join(self._workspace, 'MT3D00{}.UCN'.format(substance + 1))
        if not os.path.exists(filename):
            raise FileNotFoundError(errno.ENOENT, os.strerror(errno.ENOENT), filename)

        return filename

    def read_times(self):
        try:
            filename = self.get_concentration_file_from_substance()
            ucn_obj = bf.UcnFile(filename=filename, precision='single')
            return ucn_obj.get_times()
        except:
            return []

    def read_number_of_substances(self):
        try:
            return len([f for f in os.listdir(self._workspace) if
                        f.endswith('.UCN') and os.path.isfile(os.path.join(self._workspace, f))])
        except:
            return 0

    def read_number_of_layers(self):
        try:
            ucn_obj = bf.UcnFile(filename=self._filename, precision='single')
            number_of_layers = ucn_obj.get_data().shape[0]
            return number_of_layers
        except:
            return 0

    def read_layer(self, substance, totim, layer):
        try:
            filename = self.get_concentration_file_from_substance(substance)
            ucn_obj = bf.UcnFile(filename=filename, precision='single')
            data = ucn_obj.get_data(totim=totim, mflay=layer).tolist()
            for i in range(len(data)):
                for j in range(len(data[i])):
                    data[i][j] = round(data[i][j], 2)
                    if data[i][j] > 1e29:
                        data[i][j] = None
            return data
        except:
            return []

    def read_ts(self, substance, layer, row, column):
        try:
            filename = self.get_concentration_file_from_substance(substance)
            ucn_obj = bf.UcnFile(filename=filename, precision='single')
            return ucn_obj.get_ts(idx=(layer, row, column)).tolist()
        except:
            return []