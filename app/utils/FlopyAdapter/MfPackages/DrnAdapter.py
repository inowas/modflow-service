import flopy.modflow as mf


class DrnAdapter:
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
            if key == 'stress_period_data':
                default[key] = self.to_dict(self._data[key])
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

    def get_package(self, _mf):
        content = self.merge()
        return mf.ModflowDrn(
            _mf,
            **content
        )

    @staticmethod
    def default():
        default = {
            "ipakcb": None,
            "stress_period_data": None,
            "dtype": None,
            "extension": "drn",
            "unitnumber": None,
            "options": None
        }

        return default

    @staticmethod
    def read_package(package):
        content = {
            "ipakcb": package.ipakcb,
            "stress_period_data": package.stress_period_data,
            "dtype": package.dtype,
            "extension": package.extension,
            "unitnumber": package.unitnumber,
            "options": package.options
        }
        return content
