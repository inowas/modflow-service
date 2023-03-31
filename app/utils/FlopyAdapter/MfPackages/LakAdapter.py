import flopy.modflow as mf


class LakAdapter:
    _data = None

    def __init__(self, data):
        self._data = data

    def validate(self):
        # should be implemented
        # for key in content:
        #   do something
        #   return some hints
        pass

    def is_valid(self):
        # should be implemented
        # for key in content:
        #   do something
        #   return true or false
        return True

    def merge(self):
        default = self.default()
        for key in self._data:
            if key == 'sill_data' or 'flux_data':
                default[key] = self.to_dict(self._data[key])
                continue

            if key == 'stage_range' and self._data[key] is not None:
                default[key] = map(tuple, self._data[key])
                continue

            default[key] = self._data[key]
        return default

    def to_dict(self, data):
        if type(data) == list:
            spd_dict = {}
            for stress_period, record in enumerate(data):
                spd_dict[stress_period] = record
            return spd_dict
        return data

    def to_tuples(self, arrayOfArrays):
        return map(tuple, arrayOfArrays)

    def get_package(self, _mf):
        content = self.merge()
        return mf.ModflowLak(
            _mf,
            **content
        )

    @staticmethod
    def default():
        default = {
            "nlakes": 1,
            "ipakcb": None,
            "theta": -1.0,
            "nssitr": 0,
            "sscncr": 0.0,
            "surfdep": 0.0,
            "stages": 1.0,
            "stage_range": None,
            "tab_files": None,
            "tab_units": None,
            "lakarr": None,
            "bdlknc": None,
            "sill_data": None,
            "flux_data": None,
            "extension": 'lak',
            "unitnumber": None,
            "filenames": None,
            "options": None,
            "lwrt": 0
        }

        return default
